"""Processed-data contract and comparison checks."""

from __future__ import annotations

import csv
import math
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_PROCESSED_CSV = PROJECT_ROOT / "manufacturing_data_processed.csv"
REFACTOR_PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "manufacturing_data_processed_refactor.csv"

REQUIRED_COLUMNS = {"production_time", "equipment_id", "oee", "Machine failure"}

FAILURE_MODE_COLUMNS = ("TWF", "HDF", "PWF", "OSF", "RNF")
FAILURE_MODE_COLUMN_SET = set(FAILURE_MODE_COLUMNS)

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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_integer_like(value: str) -> bool:
    return math.isclose(float(value), round(float(value)), rel_tol=0.0, abs_tol=1e-9)


class TestProcessedDataContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.refactor_rows = read_csv_rows(REFACTOR_PROCESSED_CSV)

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
            len(legacy_header) + len(FAILURE_MODE_COLUMNS),
            len(refactor_header),
            "Refactor processed output should keep legacy columns and add the expected failure mode fields.",
        )

    def test_refactor_output_column_order_matches_legacy(self) -> None:
        legacy_header = read_csv_header(LEGACY_PROCESSED_CSV)
        refactor_header = read_csv_header(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            legacy_header,
            refactor_header[: len(legacy_header)],
            "Refactor processed output should preserve the legacy column order before any new failure mode columns.",
        )
        self.assertEqual(
            list(FAILURE_MODE_COLUMNS),
            refactor_header[len(legacy_header) :],
            "Refactor processed output should append failure mode columns after the legacy contract columns.",
        )

    def test_refactor_output_column_set_matches_legacy(self) -> None:
        legacy_header = set(read_csv_header(LEGACY_PROCESSED_CSV))
        refactor_header = set(read_csv_header(REFACTOR_PROCESSED_CSV))
        self.assertEqual(
            legacy_header.union(FAILURE_MODE_COLUMN_SET),
            refactor_header,
            "Refactor processed output column names should equal the legacy contract plus failure mode fields.",
        )

    def test_refactor_output_row_count_matches_legacy(self) -> None:
        legacy_rows = count_csv_rows(LEGACY_PROCESSED_CSV)
        refactor_rows = count_csv_rows(REFACTOR_PROCESSED_CSV)
        self.assertEqual(
            legacy_rows,
            refactor_rows,
            "Refactor processed output row count drifted from the legacy processed CSV.",
        )

    def test_refactor_output_contains_required_key_columns(self) -> None:
        header = read_csv_header(REFACTOR_PROCESSED_CSV)
        missing = REQUIRED_COLUMNS.union(FAILURE_MODE_COLUMN_SET).difference(header)
        self.assertFalse(
            missing,
            "Refactor processed output is missing key columns required by the current contract: "
            f"{sorted(missing)}",
        )

    def test_refactor_output_contains_required_columns_for_warehouse_builds(self) -> None:
        header = set(read_csv_header(REFACTOR_PROCESSED_CSV))
        missing = WAREHOUSE_REQUIRED_COLUMNS.difference(header)
        self.assertFalse(
            missing,
            "Refactor processed CSV is missing warehouse input columns. "
            "If this fails in the future, the risk will surface when warehouse dimension/fact "
            f"builders select or rename columns: {sorted(missing)}",
        )

    def test_legacy_processed_csv_contains_required_columns_for_warehouse_builds(self) -> None:
        header = set(read_csv_header(LEGACY_PROCESSED_CSV))
        missing = WAREHOUSE_REQUIRED_COLUMNS.difference(header)
        self.assertFalse(
            missing,
            "Legacy processed CSV is missing warehouse input columns. "
            "If this fails in the future, the risk will surface when warehouse dimension/fact "
            f"builders select or rename columns: {sorted(missing)}",
        )

    def test_refactor_output_uses_integer_quantity_semantics(self) -> None:
        for row in self.refactor_rows:
            self.assertTrue(
                is_integer_like(row["planned_production"]),
                "planned_production should follow integer-count semantics in the refactor snapshot.",
            )
            self.assertTrue(
                is_integer_like(row["actual_production"]),
                "actual_production should follow integer-count semantics in the refactor snapshot.",
            )
            self.assertTrue(
                is_integer_like(row["defect_count"]),
                "defect_count should follow integer-count semantics in the refactor snapshot.",
            )
            self.assertTrue(
                is_integer_like(row["qualified_count"]),
                "qualified_count should follow integer-count semantics in the refactor snapshot.",
            )

    def test_refactor_output_preserves_quantity_relationships(self) -> None:
        for row in self.refactor_rows:
            planned = int(round(float(row["planned_production"])))
            actual = int(round(float(row["actual_production"])))
            defect = int(round(float(row["defect_count"])))
            qualified = int(round(float(row["qualified_count"])))
            self.assertGreaterEqual(planned, 0)
            self.assertGreaterEqual(actual, 0)
            self.assertGreaterEqual(defect, 0)
            self.assertGreaterEqual(qualified, 0)
            self.assertLessEqual(actual, planned)
            self.assertLessEqual(defect, actual)
            self.assertEqual(
                qualified,
                actual - defect,
                "qualified_count should equal actual_production - defect_count.",
            )

    def test_refactor_output_has_nonzero_defect_counts(self) -> None:
        defect_total = sum(int(round(float(row["defect_count"]))) for row in self.refactor_rows)
        self.assertGreater(
            defect_total,
            0,
            "Refactor processed output should produce a non-zero total defect count.",
        )

    def test_refactor_output_quality_rate_has_valid_variation(self) -> None:
        quality_values = [float(row["quality_rate"]) for row in self.refactor_rows]
        self.assertTrue(
            all(0.0 <= value <= 1.0 for value in quality_values),
            "quality_rate should stay within the [0, 1] range.",
        )
        self.assertGreater(
            len(set(quality_values)),
            1,
            "quality_rate should show real variation under the refactored quantity logic.",
        )

    def test_refactor_output_oee_stays_in_valid_range(self) -> None:
        oee_values = [float(row["oee"]) for row in self.refactor_rows]
        self.assertTrue(
            all(0.0 <= value <= 1.0 for value in oee_values),
            "oee should stay within the [0, 1] range.",
        )

    def test_refactor_output_contains_failure_mode_columns(self) -> None:
        header = set(read_csv_header(REFACTOR_PROCESSED_CSV))
        missing = FAILURE_MODE_COLUMN_SET.difference(header)
        self.assertFalse(
            missing,
            "Refactor processed output should retain granular failure mode labels: "
            f"{sorted(missing)}",
        )

    def test_refactor_output_failure_mode_columns_are_binary_like(self) -> None:
        for row in self.refactor_rows:
            for column in FAILURE_MODE_COLUMNS:
                self.assertIn(
                    row[column],
                    {"0", "1", "0.0", "1.0"},
                    f"{column} should stay 0/1-like in the refactor snapshot.",
                )


if __name__ == "__main__":
    unittest.main()
