import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus  # <-- 添加这行，用于处理密码中的特殊字符
import numpy as np
from datetime import datetime

# ==================== 配置区（需修改） ====================
DB_CONFIG = {
    'user': 'root',
    'password': '20260316lmjQWQ@',  # <-- 必须修改
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'manufacturing_oee'
}

# ==================== 数据库连接 ====================
def create_db_engine(config: dict) -> object:
    # 参数名: 类型      输入类型提示
    # -> 返回类型           返回值类型提示
    #IDE自动补全 可读性 静态检查
    # #：给代码维护者看，解释"这行代码为什么这么写"
    # """：给函数调用者看，解释"这个函数是干什么的"
    """
    创建数据库连接引擎
    使用连接池复用连接，适合批量数据导入
    """
    # 对密码进行 URL 编码，将 @ 转换为 %40
    password_encoded = quote_plus(config['password'])

    connection_str = (
        f"mysql+pymysql://{config['user']}:{password_encoded}@" 
        f"{config['host']}:{config['port']}/{config['database']}?"
        f"charset=utf8mb4"
    )
    return create_engine(connection_str)

# ==================== 数据加载与验证 ====================
def load_processed_data(filepath: str) -> pd.DataFrame:
    """
    加载预处理后的CSV数据
    返回：DataFrame
    """
    df = pd.read_csv(filepath)
    print(f"[INFO] 成功加载数据：{len(df)} 行，{len(df.columns)} 列")
    return df

# ==================== 维度表构建 ====================
def build_equipment_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """
    构建设备维度表
    逻辑：从事实数据中提取设备唯一属性
    """
    equip_cols = ['equipment_id', 'production_line', 'Type', 'theoretical_cycle_time']
    equip_dim = df[equip_cols].drop_duplicates('equipment_id')
    
    # 列重命名（符合SQL schema）
    equip_dim.columns = [
        'equipment_id', 'production_line', 'equipment_type', 'theoretical_cycle_time'
    ]
    
    # 添加静态属性（模拟值）
    equip_dim['installation_date'] = '2024-01-01'
    
    print(f"[INFO] 设备维度表构建完成：{len(equip_dim)} 台设备")
    return equip_dim

def build_time_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """
    构建时间维度表（日期粒度）
    修正点：移除shift字段，避免日期-班次一对多问题
    班次作为退化维度保留在事实表中

    Args:
    df: 包含production_time的DataFrame
    Returns:
    时间维度DataFrame
    """
    # 提取日期相关信息
    dt_series = pd.to_datetime(df['production_time'])
    
    time_dim = pd.DataFrame({
        'full_date': dt_series.dt.date,
        'time_key': dt_series.dt.strftime('%Y%m%d').astype(int),
        'year': dt_series.dt.year,
        'month': dt_series.dt.month,
        'day': dt_series.dt.day,
        'week_of_year': dt_series.dt.isocalendar().week.astype(int)
    })
    
    # 计算是否工作日（周一=0，周五=4，周六=5，周日=6）
    time_dim['is_workday'] = dt_series.dt.weekday < 5
    
    # 去重：每个日期只有一条记录
    time_dim = time_dim.drop_duplicates('time_key').sort_values('time_key')
    
    print(f"[INFO] 时间维度表构建完成：{len(time_dim)} 天（含工作日标记）")
    return time_dim

# ==================== 事实表构建 ====================
def build_fact_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    构建事实表（宽表）
    修正：使用.copy()创建独立副本，避免修改原始数据
    """
    # 防御性复制：防止修改外部传入的df
    fact_df = df.copy()
    
    # 生成时间键（YYYYMMDD）
    fact_df['time_key'] = pd.to_datetime(
        fact_df['production_time']
    ).dt.strftime('%Y%m%d').astype(int)
    
    # 字段映射（仅修改副本）
    column_mapping = {
        'UDI': 'udi',
        'Air temperature [K]': 'air_temperature',
        'Process temperature [K]': 'process_temperature',
        'Rotational speed [rpm]': 'rotational_speed',
        'Torque [Nm]': 'torque',
        'Tool wear [min]': 'tool_wear',
        'Machine failure': 'machine_failure'
    }
    fact_df = fact_df.rename(columns=column_mapping)
    
    # 选择字段（返回全新DataFrame，与原df无关）
    fact_columns = [
        'equipment_id', 'time_key', 'production_time', 'shift',
        'air_temperature', 'process_temperature', 'rotational_speed', 
        'torque', 'tool_wear', 'process_stability_score',
        'planned_production', 'actual_production', 'defect_count', 
        'qualified_count', 'defect_rate',
        'availability', 'performance', 'quality_rate', 'oee',
        'machine_failure'
    ]
    
    # 数据类型强制转换（在副本上操作）
    fact_df['machine_failure'] = fact_df['machine_failure'].astype(bool)
    fact_df['defect_count'] = fact_df['defect_count'].astype(int)
    fact_df['qualified_count'] = fact_df['qualified_count'].astype(int)
    
    return fact_df[fact_columns]

# ==================== 数据导入（分批） ====================
def import_to_mysql(engine, equip_df: pd.DataFrame, time_df: pd.DataFrame, 
                    fact_df: pd.DataFrame, clear_existing: bool = False):
    """
    分批导入数据到MySQL
    参数:
        clear_existing: 是否先清空现有数据（开发调试时使用，生产环境慎用）
    """
    from sqlalchemy import text
    
    # 如需清空（按依赖顺序：先子表后父表，避免外键冲突）
    if clear_existing:
        print("[WARNING] 清空模式已启用，将删除现有数据...")
        with engine.connect() as conn:
            # 临时禁用外键检查（避免TRUNCATE时外键冲突）
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 先清空事实表（有外键依赖）
            conn.execute(text("TRUNCATE TABLE fact_equipment_status"))
            print("  ✓ 已清空 fact_equipment_status")
            
            # 再清空维度表（被依赖）
            conn.execute(text("TRUNCATE TABLE dim_equipment"))
            print("  ✓ 已清空 dim_equipment")
            conn.execute(text("TRUNCATE TABLE dim_time"))
            print("  ✓ 已清空 dim_time")
            
            # 恢复外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
    
    print("[INFO] 开始数据导入...")
    
    # 导入维度表（小数据量直接导入）
    equip_df.to_sql('dim_equipment', engine, if_exists='append', index=False)
    print(f"  ✓ dim_equipment: {len(equip_df)} 行")
    
    time_df.to_sql('dim_time', engine, if_exists='append', index=False)
    print(f"  ✓ dim_time: {len(time_df)} 行")
    
    # 导入事实表（分批）
    batch_size = 2000
    total = len(fact_df)
    
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = fact_df.iloc[start:end]
        
        batch.to_sql(
            'fact_equipment_status',
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
        
        if (end // batch_size) % 5 == 0 or end == total:
            print(f"  ✓ fact_equipment_status: {end}/{total} 行")
    
    print("[SUCCESS] 数据导入完成")

# ==================== 数据验证 ====================
def verify_data(engine):
    """
    导入后验证数据完整性和逻辑正确性
    """
    print("\n[INFO] 执行数据验证...")
    
    # 验证1：记录数统计
    sql_counts = """
        SELECT 
            (SELECT COUNT(*) FROM dim_equipment) as equipment_count,
            (SELECT COUNT(*) FROM dim_time) as time_count,
            (SELECT COUNT(*) FROM fact_equipment_status) as fact_count
    """
    counts = pd.read_sql(sql_counts, engine)
    print(f"  设备维度: {counts['equipment_count'][0]} 行")
    print(f"  时间维度: {counts['time_count'][0]} 行")
    print(f"  事实表: {counts['fact_count'][0]} 行")
    
    # 验证2：OEE统计合理性
    sql_oee = """
        SELECT 
            ROUND(AVG(oee), 3) as avg_oee,
            ROUND(MIN(oee), 3) as min_oee,
            ROUND(MAX(oee), 3) as max_oee,
            SUM(CASE WHEN machine_failure = 1 THEN 1 ELSE 0 END) as failure_count
        FROM fact_equipment_status
    """
    oee_stats = pd.read_sql(sql_oee, engine)
    print(f"\n  OEE均值: {oee_stats['avg_oee'][0]}")
    print(f"  故障记录: {oee_stats['failure_count'][0]} 条")
    
    # 验证3：工艺稳定性与缺陷率相关性（应为正相关）
    sql_corr = """
        SELECT 
            CASE 
                WHEN process_stability_score < 0.05 THEN '高稳定(0-0.05)'
                WHEN process_stability_score < 0.15 THEN '中稳定(0.05-0.15)'
                ELSE '低稳定(>0.15)'
            END as stability_level,
            ROUND(AVG(defect_rate), 3) as avg_defect_rate,
            COUNT(*) as record_count
        FROM fact_equipment_status
        GROUP BY stability_level
        ORDER BY avg_defect_rate
    """
    corr_result = pd.read_sql(sql_corr, engine)
    print("\n  工艺稳定性与缺陷率关系:")
    print(corr_result.to_string(index=False))
    
    # 验证4：外键完整性（检查是否有孤儿记录）
    sql_fk_check = """
        SELECT COUNT(*) as orphan_count
        FROM fact_equipment_status f
        LEFT JOIN dim_equipment e ON f.equipment_id = e.equipment_id
        WHERE e.equipment_id IS NULL
    """
    orphan = pd.read_sql(sql_fk_check, engine)
    if orphan['orphan_count'][0] == 0:
        print("\n  ✓ 外键完整性检查通过")
    else:
        print(f"\n  ✗ 发现 {orphan['orphan_count'][0]} 条孤儿记录")

# ==================== 主函数 ====================
def main():
    """主流程"""
    try:
        engine = create_db_engine(DB_CONFIG)
        df = load_processed_data('manufacturing_data_processed.csv')
        
        # 构建表（无副作用，原始df保持不变）
        equip_dim = build_equipment_dimension(df)
        time_dim = build_time_dimension(df)
        fact_df = build_fact_table(df)
        
        # 验证数据未被修改（可删除，仅作演示）
        assert 'time_key' not in df.columns, "原始数据不应被修改"
        
        # 导入（首次运行用clear_existing=False，重新运行用True）
        import_to_mysql(
            engine, 
            equip_dim, 
            time_dim, 
            fact_df,
            clear_existing=True  # 开发调试时设为True，生产设为False
        )
        
        verify_data(engine)
        
    except Exception as e:
        print(f"\n[ERROR] 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        raise

# 这一行必须存在！
if __name__ == "__main__":
    main()