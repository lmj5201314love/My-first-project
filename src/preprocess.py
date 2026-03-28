"""Safer preprocessing entry point for the current project stage."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from src.config import LEGACY_PREPROCESS_SCRIPT, LEGACY_PROCESSED_CSV, LEGACY_RAW_CSV
except ModuleNotFoundError:
    from config import LEGACY_PREPROCESS_SCRIPT, LEGACY_PROCESSED_CSV, LEGACY_RAW_CSV  # type: ignore


RAW_REQUIRED_COLUMNS = (
    "UDI",
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Machine failure",
)

OUTPUT_COLUMNS = [
    "UDI",
    "production_time",
    "equipment_id",
    "production_line",
    "shift",
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "process_stability_score",
    "air_temp_dev",
    "process_temp_dev",
    "torque_dev",
    "theoretical_cycle_time",
    "planned_production",
    "actual_production",
    "defect_rate",
    "defect_count",
    "qualified_count",
    "availability",
    "performance",
    "quality_rate",
    "oee",
    "Machine failure",
]


def get_legacy_input_path() -> Path:
    """Return the current raw CSV path used by the legacy flow."""
    return LEGACY_RAW_CSV


def get_legacy_output_path() -> Path:
    """Return the current processed CSV path used by the legacy flow."""
    return LEGACY_PROCESSED_CSV


def describe_current_source_of_truth() -> str:
    """Explain which file still owns preprocessing behavior."""
    return f"Legacy preprocessing source of truth: {LEGACY_PREPROCESS_SCRIPT.name}"


def load_raw_data(filepath: str | None = None) -> pd.DataFrame:
    """Load the raw AI4I CSV and validate the required input columns."""
    target_path = Path(filepath) if filepath else get_legacy_input_path()
    if not target_path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found: {target_path}. Please confirm ai4i2020.csv exists first."
        )

    df = pd.read_csv(target_path)
    missing = [column for column in RAW_REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(
            "Raw CSV is missing required columns: "
            f"{missing_text}. Please compare it with the current legacy input contract."
        )

    print(f"[INFO] Loaded raw data: {len(df)} rows x {len(df.columns)} columns")
    return df


def assign_shift(hour: int) -> str:
    """Map production hour to the current three-shift label."""
    if 8 <= hour < 16:
        return "Day"
    if 16 <= hour < 24:
        return "Evening"
    return "Night"


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add production timestamp and shift fields following the legacy logic."""
    result = df.copy()
    start_time = datetime(2025, 1, 1, 8, 0, 0)
    result["production_time"] = [start_time + timedelta(minutes=15 * i) for i in range(len(result))]
    result["shift"] = pd.to_datetime(result["production_time"]).dt.hour.apply(assign_shift)
    return result


def map_equipment(df: pd.DataFrame) -> pd.DataFrame:
    """Map product types to production lines and equipment IDs."""
    result = df.copy()
    type_mapping = {"L": "Line1", "M": "Line2", "H": "Line3"}
    result["production_line"] = result["Type"].map(type_mapping)
    result["equipment_seq"] = result.groupby("Type").cumcount() % 3 + 1
    result["equipment_id"] = result["production_line"] + "_EQ0" + result["equipment_seq"].astype(str)
    return result


def add_production_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add theoretical cycle time and production quantity fields."""
    result = df.copy()
    cycle_time_map = {"L": 900, "M": 720, "H": 600}
    result["theoretical_cycle_time"] = result["Type"].map(cycle_time_map)
    result["planned_production"] = (15 * 60) / result["theoretical_cycle_time"]
    result["performance_rate"] = result["Rotational speed [rpm]"] / 1500.0

    np.random.seed(42)
    result["actual_production"] = (
        result["planned_production"]
        * result["performance_rate"]
        * np.random.uniform(0.95, 1.0, len(result))
    )
    result["actual_production"] = result["actual_production"].clip(
        upper=result["planned_production"]
    )
    return result


def add_process_stability_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add process stability features using the legacy calculation approach."""
    result = df.copy()
    air_ideal = result["Air temperature [K]"].mean()
    process_ideal = result["Process temperature [K]"].mean()
    torque_ideal = result["Torque [Nm]"].mean()

    result["air_temp_dev"] = abs(result["Air temperature [K]"] - air_ideal) / air_ideal
    result["process_temp_dev"] = (
        abs(result["Process temperature [K]"] - process_ideal) / process_ideal
    )
    result["torque_dev"] = abs(result["Torque [Nm]"] - torque_ideal) / torque_ideal
    result["process_stability_score"] = (
        result["air_temp_dev"] + result["process_temp_dev"] + result["torque_dev"]
    ) / 3
    return result


def add_quality_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add defect rate and count features using the legacy business intent."""
    result = df.copy()
    result["defect_rate"] = 0.01 + (result["process_stability_score"] * 2)
    result.loc[result["Machine failure"] == 1, "defect_rate"] += 0.10
    result["defect_rate"] = result["defect_rate"].clip(0.01, 0.20)
    result["defect_count"] = (result["actual_production"] * result["defect_rate"]).round().astype(int)
    result["qualified_count"] = (result["actual_production"] - result["defect_count"]).clip(lower=0)
    return result


def add_oee_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add availability, performance, quality, and OEE fields."""
    result = df.copy()
    result["availability"] = np.where(result["Machine failure"] == 1, 0.0, 1.0)
    result["performance"] = (result["actual_production"] / result["planned_production"]).clip(0, 1.0)
    result["quality_rate"] = result["qualified_count"] / result["actual_production"].replace(0, np.nan)
    result["quality_rate"] = result["quality_rate"].fillna(0)
    result["oee"] = result["availability"] * result["performance"] * result["quality_rate"]
    return result


def select_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Select the final output columns that match the legacy processed file contract."""
    missing = [column for column in OUTPUT_COLUMNS if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(
            "Processed DataFrame is missing required output columns: "
            f"{missing_text}. Please review the preprocessing steps."
        )
    return df[OUTPUT_COLUMNS].copy()


def validate_processed_data(df: pd.DataFrame) -> dict[str, object]:
    """Run lightweight validation checks on the processed DataFrame."""
    required_columns = ("production_time", "equipment_id", "oee")
    missing = [column for column in required_columns if column not in df.columns]
    validation = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_required_columns": missing,
        "equipment_count": int(df["equipment_id"].nunique()) if "equipment_id" in df.columns else 0,
        "oee_zero_count": int((df["oee"] == 0).sum()) if "oee" in df.columns else 0,
        "oee_gt_0_9_count": int((df["oee"] > 0.9).sum()) if "oee" in df.columns else 0,
    }
    validation["is_valid"] = len(missing) == 0
    return validation


def print_preprocess_summary(raw_df: pd.DataFrame, processed_df: pd.DataFrame) -> None:
    """Print a beginner-friendly preprocessing summary in dry-run mode."""
    validation = validate_processed_data(processed_df)
    print()
    print("[SUMMARY] Current preprocessing overview")
    print(f"  source_of_truth: {describe_current_source_of_truth()}")
    print(f"  raw_input: {get_legacy_input_path()}")
    print(f"  legacy_output_reference: {get_legacy_output_path()}")
    print(f"  raw_shape: {raw_df.shape}")
    print(f"  processed_shape: {processed_df.shape}")
    print(f"  processed_columns_sample: {list(processed_df.columns[:8])}")
    print(f"  validation_summary: {validation}")
    print("[SUMMARY] Processed data preview:")
    print(processed_df.head(3).to_string(index=False))
    print("[SUMMARY] Default mode is dry-run. No processed CSV has been written.")


def save_processed_data(df: pd.DataFrame, output_path: str) -> Path:
    """Write the processed DataFrame only when an explicit output path is provided."""
    target_path = Path(output_path)
    if not target_path.parent.exists():
        raise FileNotFoundError(
            f"Output directory does not exist: {target_path.parent}. "
            "Please create it first or choose an existing folder."
        )

    df.to_csv(target_path, index=False, encoding="utf-8")
    return target_path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for safe preprocessing execution."""
    parser = argparse.ArgumentParser(
        description=(
            "Safer preprocessing entry point. By default this only reads the raw CSV, "
            "builds the processed DataFrame, and prints a summary."
        )
    )
    parser.add_argument(
        "--input",
        default=str(get_legacy_input_path()),
        help="Path to the raw CSV. Defaults to the current legacy raw file.",
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional output path for a new processed CSV. "
            "If omitted, the command stays in dry-run mode and writes nothing."
        ),
    )
    return parser.parse_args()


def main() -> int:
    """Run a safe-first preprocessing workflow."""
    args = parse_args()

    try:
        raw_df = load_raw_data(args.input)
        processed_df = add_time_features(raw_df)
        processed_df = map_equipment(processed_df)
        processed_df = add_production_features(processed_df)
        processed_df = add_process_stability_features(processed_df)
        processed_df = add_quality_features(processed_df)
        processed_df = add_oee_features(processed_df)
        processed_df = select_output_columns(processed_df)

        print_preprocess_summary(raw_df, processed_df)

        if not args.output:
            print("[INFO] To write a new processed CSV, rerun with --output <path>.")
            return 0

        saved_path = save_processed_data(processed_df, args.output)
        print(f"[SUCCESS] Wrote processed CSV to: {saved_path}")
        return 0
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except PermissionError as exc:
        print(f"[ERROR] Could not write the processed CSV: {exc}")
        print("[INFO] Please choose another output path or close the file if it is open elsewhere.")
        return 1
    except Exception as exc:
        print(f"[ERROR] Preprocessing step failed: {exc}")
        print("[INFO] The legacy script remains available for comparison: data_preparation+.py")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
