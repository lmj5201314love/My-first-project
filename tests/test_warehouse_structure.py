"""Read-only structure tests for warehouse staging DataFrames."""

from __future__ import annotations

import unittest

from src.warehouse import (
    build_equipment_dimension,
    build_fact_table,
    build_time_dimension,
    load_processed_data,
)


EXPECTED_EQUIPMENT_COLUMNS = [
    "equipment_id",
    "production_line",
    "equipment_type",
    "theoretical_cycle_time",
    "installation_date",
]

EXPECTED_TIME_COLUMNS = [
    "full_date",
    "time_key",
    "year",
    "month",
    "day",
    "week_of_year",
    "is_workday",
]

EXPECTED_FACT_COLUMNS = [
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


class TestWarehouseStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.processed_df = load_processed_data()
        cls.equipment_dim = build_equipment_dimension(cls.processed_df)
        cls.time_dim = build_time_dimension(cls.processed_df)
        cls.fact_df = build_fact_table(cls.processed_df)

    def test_load_processed_data_returns_non_empty_dataframe(self) -> None:
        self.assertFalse(self.processed_df.empty, "Processed CSV should load into a non-empty DataFrame.")
        self.assertGreater(
            len(self.processed_df.columns),
            0,
            "Processed CSV should contain at least one column.",
        )

    def test_build_equipment_dimension_has_expected_columns(self) -> None:
        self.assertEqual(
            list(self.equipment_dim.columns),
            EXPECTED_EQUIPMENT_COLUMNS,
            "Equipment dimension columns drifted from the current warehouse design.",
        )

    def test_build_equipment_dimension_has_unique_non_null_primary_key(self) -> None:
        self.assertTrue(
            self.equipment_dim["equipment_id"].notna().all(),
            "Equipment dimension should not contain missing equipment_id values.",
        )
        self.assertTrue(
            self.equipment_dim["equipment_id"].is_unique,
            "Equipment dimension should keep equipment_id unique.",
        )

    def test_build_equipment_dimension_contains_required_business_columns(self) -> None:
        for column in ("production_line", "equipment_type", "theoretical_cycle_time"):
            self.assertIn(
                column,
                self.equipment_dim.columns,
                f"Equipment dimension is missing required column: {column}",
            )
        self.assertGreater(len(self.equipment_dim), 0, "Equipment dimension should contain rows.")

    def test_build_time_dimension_has_expected_columns(self) -> None:
        self.assertEqual(
            list(self.time_dim.columns),
            EXPECTED_TIME_COLUMNS,
            "Time dimension columns drifted from the current warehouse design.",
        )

    def test_build_time_dimension_has_unique_time_key_and_date_grain(self) -> None:
        self.assertTrue(
            self.time_dim["time_key"].notna().all(),
            "Time dimension should not contain missing time_key values.",
        )
        self.assertTrue(
            self.time_dim["time_key"].is_unique,
            "Time dimension should contain unique time_key values after date-grain deduplication.",
        )
        self.assertEqual(
            len(self.time_dim),
            self.time_dim["full_date"].nunique(),
            "Time dimension should be deduplicated to one row per full_date.",
        )

    def test_build_time_dimension_contains_required_calendar_columns(self) -> None:
        for column in ("full_date", "year", "month", "day", "week_of_year", "is_workday"):
            self.assertIn(
                column,
                self.time_dim.columns,
                f"Time dimension is missing required calendar column: {column}",
            )
        self.assertGreater(len(self.time_dim), 0, "Time dimension should contain rows.")

    def test_build_fact_table_has_expected_columns(self) -> None:
        self.assertEqual(
            list(self.fact_df.columns),
            EXPECTED_FACT_COLUMNS,
            "Fact table columns drifted from the current warehouse design.",
        )

    def test_build_fact_table_preserves_input_row_count(self) -> None:
        self.assertEqual(
            len(self.fact_df),
            len(self.processed_df),
            "Fact table row count should match the processed CSV row count.",
        )

    def test_build_fact_table_contains_required_metrics_and_non_null_time_key(self) -> None:
        for column in ("machine_failure", "oee", "availability", "performance", "quality_rate", "time_key"):
            self.assertIn(
                column,
                self.fact_df.columns,
                f"Fact table is missing required metric column: {column}",
            )
        self.assertTrue(
            self.fact_df["time_key"].notna().all(),
            "Fact table should not contain missing time_key values.",
        )

    def test_build_fact_table_uses_expected_boolean_and_integer_semantics(self) -> None:
        self.assertEqual(
            self.fact_df["machine_failure"].dtype.kind,
            "b",
            "machine_failure should use boolean dtype semantics in the fact table.",
        )
        self.assertEqual(
            self.fact_df["defect_count"].dtype.kind,
            "i",
            "defect_count should use integer dtype semantics in the fact table.",
        )
        self.assertEqual(
            self.fact_df["qualified_count"].dtype.kind,
            "i",
            "qualified_count should use integer dtype semantics in the fact table.",
        )


if __name__ == "__main__":
    unittest.main()
