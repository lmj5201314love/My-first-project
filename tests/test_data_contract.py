"""Minimal processed-data contract checks."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = PROJECT_ROOT / "manufacturing_data_processed.csv"
REQUIRED_COLUMNS = {"production_time", "equipment_id", "oee"}


class TestProcessedDataContract(unittest.TestCase):
    def test_processed_csv_exists(self) -> None:
        self.assertTrue(
            PROCESSED_CSV.exists(),
            f"Expected processed CSV to exist: {PROCESSED_CSV}",
        )

    def test_processed_csv_contains_key_columns(self) -> None:
        with PROCESSED_CSV.open("r", encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))

        missing = REQUIRED_COLUMNS.difference(header)
        self.assertFalse(missing, f"Missing required processed columns: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
