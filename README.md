# Manufacturing Data Analysis Project

Student manufacturing analytics project built on the AI4I 2020 dataset, currently being refactored from legacy scripts into a safer local project structure.

## Current Real Pipeline

Current source data flow in this repository:

`ai4i2020.csv` -> `data_preparation+.py` -> `manufacturing_data_processed.csv` -> `data_import.py`

This is still the real legacy pipeline today.

## Current Source Of Truth

- `ai4i2020.csv`: raw input dataset
- `data_preparation+.py`: preprocessing source of truth
- `manufacturing_data_processed.csv`: legacy processed output reference
- `data_import.py`: MySQL import source of truth

The newer modules under `src/` are safer incremental entry points, but they do not replace the legacy scripts yet.

## Legacy Scripts And New Entrypoints

- `data_preparation+.py`
  Legacy preprocessing script. Still authoritative for current preprocessing logic.
- `src/preprocess.py`
  Safer preprocessing entry scaffold. It reorganizes the same flow into clearer functions and defaults to dry-run mode.
- `data_import.py`
  Legacy warehouse import script. Still authoritative for current import logic.
- `src/warehouse.py`
  Safer warehouse entry scaffold. It builds warehouse DataFrames and prints summaries by default instead of writing to MySQL.

## Current Tables And Views

Current warehouse design is based on three tables:

- `dim_equipment`
  Equipment dimension built from processed CSV fields such as `equipment_id`, `production_line`, and `theoretical_cycle_time`.
- `dim_time`
  Date-grain time dimension built from `production_time`.
- `fact_equipment_status`
  Fact table containing KPI, quality, and machine status fields such as `oee`, `availability`, `performance`, `quality_rate`, and `machine_failure`.

Current SQL view definitions include:

- `vw_daily_equipment_kpi`
  Daily KPI summary by equipment.
- `vw_failure_summary`
  Failure-oriented KPI summary by equipment and line.
- `vw_shift_kpi`
  KPI summary by production line and shift.

See [data_dictionary.md](C:\Itmes_2\docs\data_dictionary.md) for field-level explanations.
See [run_guide.md](C:\Itmes_2\docs\run_guide.md) for step-by-step commands.
See [analysis_report_template.md](C:\Itmes_2\docs\analysis_report_template.md) before starting notebook or EDA work.

## Recommended Beginner Workflow

Recommended order for understanding and validating the project:

1. Read [project_scope.md](C:\Itmes_2\docs\project_scope.md) and [data_dictionary.md](C:\Itmes_2\docs\data_dictionary.md).
2. Treat `data_preparation+.py` and `data_import.py` as the current business references.
3. Run `src/preprocess.py` in dry-run mode to inspect the preprocessing output safely.
4. Run `src/warehouse.py` in dry-run mode to inspect dimension and fact table structure safely.
5. Run the test suite to verify current data and warehouse contracts.
6. Review `sql/schema.sql` and `sql/views.sql` as the first-pass warehouse documentation.

## Current Safety Design

The repository now includes a few safe-first design choices:

- `src/preprocess.py` defaults to dry-run mode
- `src/preprocess.py` does not overwrite `manufacturing_data_processed.csv` unless you explicitly pass `--output`
- `src/warehouse.py` defaults to dry-run mode
- `src/warehouse.py` does not write to MySQL unless you explicitly pass `--write`
- `src/warehouse.py` only allows truncation behavior when `--clear-existing` is explicitly combined with `--write`
- database configuration for the new warehouse entry comes from environment variables rather than hard-coded secrets

## Recommended Commands

Safe commands for local inspection:

- `.\.venv\Scripts\python.exe -m src.preprocess`
- `.\.venv\Scripts\python.exe -m src.preprocess --output data/processed/manufacturing_data_processed_refactor.csv`
- `.\.venv\Scripts\python.exe -m src.warehouse`
- `python -m unittest tests.test_data_contract`
- `.\.venv\Scripts\python.exe -m unittest tests.test_warehouse_structure`

Notes:

- Prefer the project `.venv` Python when running modules that depend on `pandas` or `sqlalchemy`.
- Do not run `src/warehouse.py --write` unless database environment variables are set and you really intend to write to MySQL.

## Current Tests

The current tests protect different layers of the project:

- `tests/test_data_contract.py`
  Protects processed CSV contract and legacy-vs-refactor output comparison.
  It checks file existence, key fields, column count, column order, row count, first-row sample, and warehouse-required input columns.
- `tests/test_warehouse_structure.py`
  Protects DataFrame structure produced by `src/warehouse.py`.
  It checks equipment dimension columns and uniqueness, time dimension date-grain behavior, and fact table columns, row count, and basic dtype semantics.

## SQL Files

- `sql/schema.sql`
  First-pass MySQL DDL that mirrors the current DataFrame contracts from `src/warehouse.py`.
- `sql/views.sql`
  First-pass MySQL analysis views built on the current fact and dimension fields.

These SQL files are documentation-grade and structure-grade artifacts for the current stage. They have not been executed automatically by the repository.

## Current Limits

This project is still in a transition stage. Important caveats:

- legacy scripts are still the business reference
- current OEE and related KPI fields are proxy or simulated manufacturing metrics built from current rules
- the SQL design is a first-pass schema, not a final production warehouse
- the new modules focus on safety and readability first, not on rewriting all legacy behavior at once
