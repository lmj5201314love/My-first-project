"""Safer warehouse import entry point for the current project stage."""

from __future__ import annotations

import argparse
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

try:
    from src.config import (
        LEGACY_PROCESSED_CSV,
        LEGACY_WAREHOUSE_SCRIPT,
        get_database_config,
        get_database_config_help_message,
        get_database_config_summary,
        get_missing_database_env_vars,
    )
except ModuleNotFoundError:
    from config import (  # type: ignore
        LEGACY_PROCESSED_CSV,
        LEGACY_WAREHOUSE_SCRIPT,
        get_database_config,
        get_database_config_help_message,
        get_database_config_summary,
        get_missing_database_env_vars,
    )


def describe_current_source_of_truth() -> str:
    """Explain which file still owns warehouse import behavior."""
    return f"Legacy warehouse source of truth: {LEGACY_WAREHOUSE_SCRIPT.name}"


def get_processed_input_path() -> str:
    """Return the processed CSV path expected by the future import module."""
    return str(LEGACY_PROCESSED_CSV)


def get_config_summary() -> dict[str, str]:
    """Return a safe summary of database configuration values."""
    return get_database_config_summary()


def load_processed_data(filepath: str | None = None) -> pd.DataFrame:
    """Load the processed CSV used by the current warehouse flow."""
    target_path = filepath or get_processed_input_path()
    df = pd.read_csv(target_path)
    print(f"[INFO] Loaded processed data: {len(df)} rows x {len(df.columns)} columns")
    return df


def build_equipment_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build the equipment dimension using the current legacy field design."""
    equip_cols = ["equipment_id", "production_line", "Type", "theoretical_cycle_time"]
    equip_dim = df[equip_cols].drop_duplicates("equipment_id").copy()
    equip_dim.columns = [
        "equipment_id",
        "production_line",
        "equipment_type",
        "theoretical_cycle_time",
    ]
    equip_dim["installation_date"] = "2024-01-01"
    return equip_dim


def build_time_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build the date-grain time dimension from production timestamps."""
    dt_series = pd.to_datetime(df["production_time"])
    time_dim = pd.DataFrame(
        {
            "full_date": dt_series.dt.date,
            "time_key": dt_series.dt.strftime("%Y%m%d").astype(int),
            "year": dt_series.dt.year,
            "month": dt_series.dt.month,
            "day": dt_series.dt.day,
            "week_of_year": dt_series.dt.isocalendar().week.astype(int),
        }
    )
    time_dim["is_workday"] = dt_series.dt.weekday < 5
    time_dim = time_dim.drop_duplicates("time_key").sort_values("time_key").reset_index(drop=True)
    return time_dim


def build_fact_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build the fact table with the current legacy field contract."""
    fact_df = df.copy()
    fact_df["time_key"] = pd.to_datetime(fact_df["production_time"]).dt.strftime("%Y%m%d").astype(int)

    column_mapping = {
        "UDI": "udi",
        "Air temperature [K]": "air_temperature",
        "Process temperature [K]": "process_temperature",
        "Rotational speed [rpm]": "rotational_speed",
        "Torque [Nm]": "torque",
        "Tool wear [min]": "tool_wear",
        "Machine failure": "machine_failure",
    }
    fact_df = fact_df.rename(columns=column_mapping)

    fact_columns = [
        "equipment_id",
        "time_key",
        "production_time",
        "shift",
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
        "process_stability_score",
        "planned_production",
        "actual_production",
        "defect_count",
        "qualified_count",
        "defect_rate",
        "availability",
        "performance",
        "quality_rate",
        "oee",
        "machine_failure",
    ]

    fact_df["machine_failure"] = fact_df["machine_failure"].astype(bool)
    fact_df["defect_count"] = fact_df["defect_count"].astype(int)
    fact_df["qualified_count"] = fact_df["qualified_count"].astype(int)
    return fact_df[fact_columns]


def create_db_engine(config: dict[str, str] | None = None):
    """Create a SQLAlchemy engine from environment-based configuration."""
    resolved_config = config or get_database_config()
    missing = get_missing_database_env_vars()
    if missing:
        raise ValueError(get_database_config_help_message())

    password_encoded = quote_plus(resolved_config["password"])
    connection_str = (
        f"mysql+pymysql://{resolved_config['user']}:{password_encoded}"
        f"@{resolved_config['host']}:{resolved_config['port']}/{resolved_config['database']}"
        "?charset=utf8mb4"
    )
    return create_engine(connection_str)


def import_to_mysql(
    engine,
    equip_df: pd.DataFrame,
    time_df: pd.DataFrame,
    fact_df: pd.DataFrame,
    clear_existing: bool = False,
) -> None:
    """Import dimension and fact tables into MySQL with safer defaults."""
    if clear_existing:
        print("[WARNING] clear_existing=True was explicitly enabled.")
        print("[WARNING] Existing warehouse tables will be truncated before import.")
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(text("TRUNCATE TABLE fact_equipment_status"))
            conn.execute(text("TRUNCATE TABLE dim_equipment"))
            conn.execute(text("TRUNCATE TABLE dim_time"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()

    print("[INFO] Starting MySQL import...")
    equip_df.to_sql("dim_equipment", engine, if_exists="append", index=False)
    print(f"[INFO] dim_equipment imported: {len(equip_df)} rows")

    time_df.to_sql("dim_time", engine, if_exists="append", index=False)
    print(f"[INFO] dim_time imported: {len(time_df)} rows")

    batch_size = 2000
    total = len(fact_df)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = fact_df.iloc[start:end]
        batch.to_sql(
            "fact_equipment_status",
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )
        if (end // batch_size) % 5 == 0 or end == total:
            print(f"[INFO] fact_equipment_status imported: {end}/{total} rows")

    print("[SUCCESS] MySQL import finished.")


def verify_data(engine) -> dict[str, object]:
    """Run post-import sanity checks against the current warehouse design."""
    print("[INFO] Running warehouse verification checks...")

    sql_counts = """
        SELECT
            (SELECT COUNT(*) FROM dim_equipment) AS equipment_count,
            (SELECT COUNT(*) FROM dim_time) AS time_count,
            (SELECT COUNT(*) FROM fact_equipment_status) AS fact_count
    """
    counts = pd.read_sql(sql_counts, engine).iloc[0].to_dict()

    sql_oee = """
        SELECT
            ROUND(AVG(oee), 3) AS avg_oee,
            ROUND(MIN(oee), 3) AS min_oee,
            ROUND(MAX(oee), 3) AS max_oee,
            SUM(CASE WHEN machine_failure = 1 THEN 1 ELSE 0 END) AS failure_count
        FROM fact_equipment_status
    """
    oee_stats = pd.read_sql(sql_oee, engine).iloc[0].to_dict()

    sql_fk_check = """
        SELECT COUNT(*) AS orphan_count
        FROM fact_equipment_status f
        LEFT JOIN dim_equipment e ON f.equipment_id = e.equipment_id
        WHERE e.equipment_id IS NULL
    """
    orphan = pd.read_sql(sql_fk_check, engine).iloc[0].to_dict()

    summary = {
        "counts": counts,
        "oee_stats": oee_stats,
        "foreign_key_check": orphan,
    }

    print(f"[INFO] Row counts: {counts}")
    print(f"[INFO] OEE summary: {oee_stats}")
    print(f"[INFO] Foreign key check: {orphan}")
    return summary


def print_dataframe_summary(
    raw_df: pd.DataFrame,
    equip_df: pd.DataFrame,
    time_df: pd.DataFrame,
    fact_df: pd.DataFrame,
) -> None:
    """Print a beginner-friendly summary before any write step."""
    print()
    print("[SUMMARY] Current warehouse staging overview")
    print(f"  source_of_truth: {describe_current_source_of_truth()}")
    print(f"  processed_input: {get_processed_input_path()}")
    print(f"  processed_shape: {raw_df.shape}")
    print(f"  equipment_dim_shape: {equip_df.shape}")
    print(f"  time_dim_shape: {time_df.shape}")
    print(f"  fact_table_shape: {fact_df.shape}")
    print(f"  processed_columns_sample: {list(raw_df.columns[:8])}")
    print(f"  fact_columns_sample: {list(fact_df.columns[:8])}")
    print(f"  db_config_summary: {get_config_summary()}")
    print("[SUMMARY] Default mode is dry-run. No database write has been executed.")


def parse_args() -> argparse.Namespace:
    """Parse CLI flags for safe warehouse execution."""
    parser = argparse.ArgumentParser(
        description=(
            "Safer warehouse import entry point. By default this only reads the processed CSV, "
            "builds dimension/fact DataFrames, and prints a summary."
        )
    )
    parser.add_argument(
        "--input",
        default=get_processed_input_path(),
        help="Path to the processed CSV. Defaults to the current legacy processed file.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write dimension and fact tables to MySQL.",
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Truncate existing warehouse tables before import. Ignored unless --write is set.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run post-import verification after a successful database write.",
    )
    return parser.parse_args()


def main() -> int:
    """Run a safe-first warehouse workflow."""
    args = parse_args()

    try:
        df = load_processed_data(args.input)
        equip_dim = build_equipment_dimension(df)
        time_dim = build_time_dimension(df)
        fact_df = build_fact_table(df)

        print_dataframe_summary(df, equip_dim, time_dim, fact_df)

        if not args.write:
            if args.clear_existing:
                print("[INFO] --clear-existing was ignored because --write was not provided.")
            print("[INFO] To write to MySQL, rerun with --write after checking your environment variables.")
            return 0

        missing = get_missing_database_env_vars()
        if missing:
            print(f"[ERROR] {get_database_config_help_message()}")
            print("[INFO] Database write was skipped. Your local data summary above is still valid.")
            return 1

        engine = create_db_engine()
        import_to_mysql(
            engine=engine,
            equip_df=equip_dim,
            time_df=time_dim,
            fact_df=fact_df,
            clear_existing=args.clear_existing,
        )

        if args.verify:
            verify_data(engine)

        return 0
    except FileNotFoundError as exc:
        print(f"[ERROR] Processed CSV not found: {exc}")
        print("[INFO] Please confirm manufacturing_data_processed.csv exists before running warehouse steps.")
        return 1
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except Exception as exc:
        print(f"[ERROR] Warehouse step failed: {exc}")
        print("[INFO] The legacy script remains available for comparison: data_import.py")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
