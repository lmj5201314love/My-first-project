"""Processed-data contract and comparison checks."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_PROCESSED_CSV = PROJECT_ROOT / "manufacturing_data_processed.csv"
REFACTOR_PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "manufacturing_data_processed_refactor.csv"

REQUIRED_COLUMNS = {"production_time", "equipment_id", "oee", "Machine failure"}

WAREHOUSE_REQUIRED_COLUMNS = {
    "equipment_id",
    "production_line",
    "Type",
    "theoretical_cycle_time",
    "production_time",
    "shift",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
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
    "Machine failure",
}


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


def read_csv_first_row(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        return next(reader)


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


class TestProcessedDataContract(unittest.TestCase):
    def test_legacy_processed_csv_exists(self) -> None:
        self.assertTrue(
            LEGACY_PROCESSED_CSV.exists(),
            f"Expected legacy processed CSV to exist: {LEGACY_PROCESSED_CSV}",
        )

    def test_refactor_processed_csv_exists(self) -> None:
        self.assertTrue(
            REFACTOR_PROCESSED_CSV.exists(),
            "Expected refactor processed CSV snapshot to exist for read-only comparison: "
            f"{REFACTOR_PROCESSED_CSV}",
        )

    def test_legacy_processed_csv_contains_key_columns(self) -> None:
        header = read_csv_header(LEGACY_PROCESSED_CSV)

        missing = REQUIRED_COLUMNS.difference(header)
        self.assertFalse(missing, f"Missing required processed columns: {sorted(missing)}")

    def test_refactor_output_column_count_matches_legacy(self) -> None:
        legacy_header = read_csv_header(LEGACY_PROCESSED_CSV)
        refactor_header = read_csv_header(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            len(legacy_header),
            len(refactor_header),
            "Refactor processed output column count drifted from the legacy processed CSV.",
        )

    def test_refactor_output_column_order_matches_legacy(self) -> None:
        legacy_header = read_csv_header(LEGACY_PROCESSED_CSV)
        refactor_header = read_csv_header(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            legacy_header,
            refactor_header,
            "Refactor processed output column order drifted from the legacy processed CSV.",
        )

    def test_refactor_output_column_set_matches_legacy(self) -> None:
        legacy_header = set(read_csv_header(LEGACY_PROCESSED_CSV))
        refactor_header = set(read_csv_header(REFACTOR_PROCESSED_CSV))
        self.assertEqual(
            legacy_header,
            refactor_header,
            "Refactor processed output column names drifted from the legacy processed CSV.",
        )

    def test_refactor_output_row_count_matches_legacy(self) -> None:
        legacy_rows = count_csv_rows(LEGACY_PROCESSED_CSV)
        refactor_rows = count_csv_rows(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            legacy_rows,
            refactor_rows,
            "Refactor processed output row count drifted from the legacy processed CSV.",
        )

    def test_refactor_output_first_row_matches_legacy(self) -> None:
        legacy_first_row = read_csv_first_row(LEGACY_PROCESSED_CSV)
        refactor_first_row = read_csv_first_row(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            legacy_first_row,
            refactor_first_row,
            "Refactor processed output first-row sample drifted from the legacy processed CSV.",
        )

    def test_refactor_output_contains_required_key_columns(self) -> None:
        header = read_csv_header(REFACTOR_PROCESSED_CSV)
        missing = REQUIRED_COLUMNS.difference(header)
        self.assertFalse(
            missing,
            "Refactor processed output is missing key columns required by the current contract: "
            f"{sorted(missing)}",
        )

    def test_processed_csv_contains_required_columns_for_warehouse_builds(self) -> None:
        header = set(read_csv_header(LEGACY_PROCESSED_CSV))
        missing = WAREHOUSE_REQUIRED_COLUMNS.difference(header)
        self.assertFalse(
            missing,
            "Legacy processed CSV is missing warehouse input columns. "
            "If this fails in the future, the risk will surface when warehouse dimension/fact "
            f"builders select or rename columns: {sorted(missing)}",
        )


if __name__ == "__main__":
    unittest.main()
