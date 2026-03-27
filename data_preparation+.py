import pandas as pd
import numpy as np
from datetime import datetime, timedelta

"""
制造业OEE数据分析 - 数据预处理脚本
基于AI4I 2020真实工业数据集，构建符合制造业务逻辑的宽表数据

核心优化点：
1. 分离设备状态(Availability)与质量缺陷(Quality)，避免故障时的"双重惩罚"
2. 质量缺陷率基于工艺参数偏离度计算（温度/扭矩波动→缺陷率上升），更符合物理实际
3. 保留工艺稳定性特征，用于后续机器学习建模
"""

# ==================== 第1步：读取原始真实数据 ====================
df = pd.read_csv('ai4i2020.csv')

print(f"原始数据加载完成：共 {len(df)} 条记录")
print(f"原始字段：{list(df.columns)}")


# ==================== 第2步：生成时间维度 ====================
# 制造场景假设：连续生产数据，每15分钟一个采样点（对应一个生产节拍）
# 时间跨度：10000条 × 15分钟 ≈ 104天（约3.5个月）
start_time = datetime(2025, 1, 1, 8, 0, 0)  # 早班8:00开始
# 得到时间，分别是年、月、日、小时、分钟、秒

df['production_time'] = [start_time + timedelta(minutes=15*i) for i in range(len(df))]
# timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

# 生成班次（制造业三班倒）
def get_shift(hour):
    if 8 <= hour < 16:
        return 'Day'      # 白班 08:00-16:00
    elif 16 <= hour < 24:
        return 'Evening'  # 晚班 16:00-24:00
    else:
        return 'Night'    # 夜班 00:00-08:00

df['shift'] = df['production_time'].dt.hour.apply(get_shift)
#series.dt属性，从日期时间中提取特定的部分
# 假设 df['production_time'] = 2025-01-01 14:30:00
# df['production_time'].dt.year   提取年份：2025
# df['production_time'].dt.month  提取月份：1

# Series.apply(函数) 或 DataFrame.apply(函数, axis=1)
# 作用：对每一行（或每一列）执行自定义操作
# numbers = pd.Series([1, 2, 3, 4, 5])
# result = numbers.apply(lambda x: '奇数' if x % 2 == 1 else '偶数')
# 结果：['奇数', '偶数', '奇数', '偶数', '奇数']

print(f"时间范围：{df['production_time'].min()} 至 {df['production_time'].max()}")


# ==================== 第3步：产线与设备维度映射 ====================
# AI4I原始Type字段：L(低负荷), M(中负荷), H(高负荷)
# 映射到3条产线，每条产线3台设备，共9台设备（离散制造典型配置）

type_mapping = {'L': 'Line1', 'M': 'Line2', 'H': 'Line3'}
df['production_line'] = df['Type'].map(type_mapping)
# 语法：Series.map(字典或函数)
# 作用：一对一替换值，类似Excel的VLOOKUP
# 基础用法：字典映射
# type_mapping = {'L': 'Line1', 'M': 'Line2', 'H': 'Line3'}
# df['Type'] = ['L', 'M', 'H', 'L', 'M']
# df['production_line'] = df['Type'].map(type_mapping)
# 结果：['Line1', 'Line2', 'Line3', 'Line1', 'Line2']
# 进阶：用函数映射（计算）
# df['number'] = [1, 2, 3]
# df['squared'] = df['number'].map(lambda x: x ** 2)
# 结果：[1, 4, 9]

# 设备编号生成：基于Type分组内的行号循环分配（1,2,3,1,2,3...）
df['equipment_seq'] = df.groupby('Type').cumcount() % 3 + 1
df['equipment_id'] = df['production_line'] + '_EQ0' + df['equipment_seq'].astype(str)
# groupbt按照指定列来进行分组
# cumcount()计算每组的行号，依次编号1、2、3、4、...

print(f"设备分布：\n{df['equipment_id'].value_counts().sort_index()}")


# ==================== 第4步：生产数据生成 ====================
# 理论节拍设定（基于产品复杂度Type）
# L(简单): 15分钟/件, M(中等): 12分钟/件, H(复杂): 10分钟/件
cycle_time_map = {'L': 900, 'M': 720, 'H': 600}  # 单位：秒/件
df['theoretical_cycle_time'] = df['Type'].map(cycle_time_map)

# 计划产量：每个15分钟窗口的理论产出
# 15分钟 = 900秒，计划产量 = 900 / 理论节拍
df['planned_production'] = (15 * 60) / df['theoretical_cycle_time']

# 实际产量：基于转速性能率计算
# 假设理论转速为1500rpm，实际转速/1500 = 性能系数
df['performance_rate'] = df['Rotational speed [rpm]'] / 1500.0

# 实际产量 = 计划产量 × 性能率 × 随机波动(95%-100%)
# 随机波动模拟真实生产中的微小不确定性
np.random.seed(42)  # 固定随机种子，保证可复现
df['actual_production'] = df['planned_production'] * df['performance_rate'] * np.random.uniform(0.95, 1.0, len(df))

# 防止实际产量超过计划（工业中超产通常不算绩效，这里做截断处理）
df['actual_production'] = df['actual_production'].clip(upper=df['planned_production'])
# Series.clip(lower=最小值, upper=最大值)
# 作用：限制数值范围，超出边界的自动替换成边界值


# ==================== 第5步：工艺稳定性计算（核心特征工程） ====================
"""
工业逻辑：产品质量取决于工艺参数稳定性，而非简单的"故障=全报废"
关键工艺参数：空气温度、过程温度、扭矩
"""

# 计算各参数的理想值（使用数据集统计均值作为标准）
air_ideal = df['Air temperature [K]'].mean()           # 约298-300K
process_ideal = df['Process temperature [K]'].mean()   # 约308-310K  
torque_ideal = df['Torque [Nm]'].mean()                # 约40Nm

# 计算标准化偏离度（0表示完美匹配标准值，越大表示偏离越严重）
df['air_temp_dev'] = abs(df['Air temperature [K]'] - air_ideal) / air_ideal
df['process_temp_dev'] = abs(df['Process temperature [K]'] - process_ideal) / process_ideal
df['torque_dev'] = abs(df['Torque [Nm]'] - torque_ideal) / torque_ideal

# 综合工艺稳定性得分（0-1之间，0为完美稳定，越大越不稳定）
df['process_stability_score'] = (df['air_temp_dev'] + df['process_temp_dev'] + df['torque_dev']) / 3

print(f"工艺稳定性统计：均值={df['process_stability_score'].mean():.4f}, 最大={df['process_stability_score'].max():.4f}")


# ==================== 第6步：质量缺陷计算（优化核心） ====================
"""
优化逻辑：缺陷率由工艺稳定性决定，故障仅增加额外风险，不必然导致100%报废

缺陷率公式：
- 基础缺陷率：1%（正常生产波动）
- 工艺偏差惩罚：每1%综合偏差，缺陷率增加2%
- 故障额外惩罚：Machine failure=1时，额外增加10%缺陷率（模拟故障预警或部分批次影响）
- 上限控制：最高20%（避免极端值，符合工业实际）
"""

# 基础缺陷率计算（基于工艺稳定性）
df['defect_rate'] = 0.01 + (df['process_stability_score'] * 2)

# 故障影响：故障状态下缺陷率上升，但不是100%
# 逻辑：故障往往是渐进的（如轴承磨损），或发生在生产周期后半段
df.loc[df['Machine failure'] == 1, 'defect_rate'] += 0.10

# 限制缺陷率范围：1% - 20%（工业中超过20%通常已触发停线机制）
df['defect_rate'] = df['defect_rate'].clip(0.01, 0.20)

# 计算缺陷数量和合格数量
df['defect_count'] = (df['actual_production'] * df['defect_rate']).round().astype(int)
df['qualified_count'] = (df['actual_production'] - df['defect_count']).clip(lower=0)  # 防止负数
# round是对数据四舍五入

print(f"质量统计：平均缺陷率={df['defect_rate'].mean():.2%}, 总缺陷数={df['defect_count'].sum()}")


# ==================== 第7步：OEE三要素计算（优化核心） ====================
"""
OEE = Availability × Performance × Quality Rate

关键修正：
1. Availability：故障时=0（时间损失），正常时=1。不直接影响Quality Rate的计算基础
2. Performance：实际产量/计划产量，上限100%（超产不算性能提升，属计划失误）
3. Quality Rate：合格品/实际生产量，独立于Availability计算
"""

# 可用率：故障标记直接决定（0或1）
df['availability'] = np.where(df['Machine failure'] == 1, 0.0, 1.0)
# np.where(条件, 条件为真时的值, 条件为假时的值)
# 作用：整列批量判断，比apply快10-100倍

# 性能率：实际/计划，限制在0-100%（制造业实践中，超产不提升OEE）
df['performance'] = (df['actual_production'] / df['planned_production']).clip(0, 1.0)

# 质量率：合格品/实际生产量
# 防止除以0：如果实际产量为0（计划停产），质量率设为0
df['quality_rate'] = df['qualified_count'] / df['actual_production'].replace(0, np.nan)
df['quality_rate'] = df['quality_rate'].fillna(0)
# replace将0替换为np.nan，避免除以0导致inf或错误
# fillna将np.nan替换为0

# OEE综合计算
df['oee'] = df['availability'] * df['performance'] * df['quality_rate']

print(f"\nOEE统计结果：")
print(f"  均值：{df['oee'].mean():.3f}")
print(f"  最小值：{df['oee'].min():.3f}（故障或严重工艺漂移）")
print(f"  最大值：{df['oee'].max():.3f}（理想状态）")


# ==================== 第8步：字段整理与保存 ====================
# 选择最终字段（保留原始传感器、中间特征、OEE指标）
final_columns = [
    # 基础标识
    'UDI', 'production_time', 'equipment_id', 'production_line', 'shift', 'Type',
    
    # 原始传感器数据（来自AI4I真实数据）
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 
    'Torque [Nm]', 'Tool wear [min]',
    
    # 工艺稳定性特征（用于后续ML建模）
    'process_stability_score', 'air_temp_dev', 'process_temp_dev', 'torque_dev',
    
    # 生产数据
    'theoretical_cycle_time', 'planned_production', 'actual_production', 
    'defect_rate', 'defect_count', 'qualified_count',
    
    # OEE三要素与综合指标
    'availability', 'performance', 'quality_rate', 'oee',
    
    # 原始故障标记（真实标签，用于验证）
    'Machine failure'
]

df_final = df[final_columns]

# 保存为清洗后的数据（此文件将导入MySQL）
output_file = 'manufacturing_data_processed.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8')

print(f"\n✓ 数据预处理完成，已保存至：{output_file}")
print(f"  总记录数：{len(df_final)}")
print(f"  字段数：{len(df_final.columns)}")
print(f"  文件大小：{df_final.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
# df.memory_usage(deep=True)  # 返回每列的字节数（B）
# sum表示加总所有列

# ==================== 第9步：数据质量验证 ====================
print("\n===== 数据质量验证 =====")

# 验证1：设备分布均匀性
print("\n1. 设备记录数分布：")
print(df_final['equipment_id'].value_counts().sort_index())
# value_counts()返回每个值出现的次数，sort_index()按索引排序

# 验证2：OEE分布合理性（应呈现连续分布，而非只有0和1）
print(f"\n2. OEE分布合理性检查：")
print(f"   OEE=0的记录数：{(df_final['oee'] == 0).sum()}（纯故障停机）")
print(f"   OEE>0.9的记录数：{(df_final['oee'] > 0.9).sum()}（高效生产）")
print(f"   0<OEE<0.6的记录数：{((df_final['oee'] > 0) & (df_final['oee'] < 0.6)).sum()}（工艺波动或微故障）")

# 验证3：故障与OEE关系（故障时OEE应为0或极低）
failure_oee = df_final[df_final['Machine failure'] == 1]['oee'].mean()
normal_oee = df_final[df_final['Machine failure'] == 0]['oee'].mean()
print(f"\n3. 故障与OEE关系验证：")
print(f"   故障状态平均OEE：{failure_oee:.3f}（应为0）")
print(f"   正常状态平均OEE：{normal_oee:.3f}（应>0.7）")

# 验证4：工艺稳定性与缺陷率相关性（应正相关）
correlation = df_final['process_stability_score'].corr(df_final['defect_rate'])
print(f"\n4. 工艺稳定性与缺陷率相关性：{correlation:.3f}（应为正值，越大表示工艺越不稳定缺陷越多）")
# corr是计算两列数据的皮尔逊相关系数（即高数中的-1到1的那个数据，表示相关性的）

print("\n===== 验证完成，数据可用于后续MySQL导入 =====")