# Run Guide

This is a small step-by-step guide for the first time you run the project locally.

## Before You Start

### Use the project `.venv` when possible

Recommended Python executable:

```powershell
.\.venv\Scripts\python.exe
```

Why this matters:

- the project modules under `src/` depend on packages like `pandas` and `sqlalchemy`
- your system `python` may not have the same packages installed
- the project `.venv` is the safest way to get the expected behavior

Commands that are especially recommended to run with `.venv\Scripts\python.exe`:

- `src.preprocess`
- `src.warehouse`
- `tests.test_warehouse_structure`

`tests.test_data_contract` is lighter because it mainly reads CSV files, but using the same `.venv` still keeps things consistent.

## Recommended First-Run Order

If you are new to the repository, use this order:

1. Read [README.md](C:\Itmes_2\README.md)
2. Read [data_dictionary.md](C:\Itmes_2\docs\data_dictionary.md)
3. Run `src.preprocess` in dry-run mode
4. Run `src.warehouse` in dry-run mode
5. Run `tests.test_data_contract`
6. Run `tests.test_warehouse_structure`
7. Review [schema.sql](C:\Itmes_2\sql\schema.sql) and [views.sql](C:\Itmes_2\sql\views.sql)
8. Open [01_eda_skeleton.ipynb](C:\Itmes_2\notebooks\01_eda_skeleton.ipynb) and continue from the `Dataset Overview` section

This order lets you understand the project before trying any command that writes a new file or talks to MySQL.

## Command Checklist

### 1. Read the project overview

What to open:

- [README.md](C:\Itmes_2\README.md)
- [data_dictionary.md](C:\Itmes_2\docs\data_dictionary.md)

What this is for:

- understand the current legacy pipeline
- understand what the new `src/` entrypoints do
- understand key fields, tables, and views

Writes file or DB:

- No

### 2. Run preprocess dry-run

Command:

```powershell
.\.venv\Scripts\python.exe -m src.preprocess
```

What this does:

- reads `ai4i2020.csv`
- builds the processed DataFrame in memory
- prints a summary and sample preview

Normal output should include:

- `Loaded raw data`
- `Current preprocessing overview`
- `Default mode is dry-run. No processed CSV has been written.`

Writes file or DB:

- No

### 3. Run warehouse dry-run

Command:

```powershell
.\.venv\Scripts\python.exe -m src.warehouse
```

What this does:

- reads `manufacturing_data_processed.csv`
- builds `dim_equipment`, `dim_time`, and `fact_equipment_status` in memory
- prints a summary of their shapes and current DB config status

Normal output should include:

- `Loaded processed data`
- `Current warehouse staging overview`
- `Default mode is dry-run. No database write has been executed.`

Writes file or DB:

- No

### 4. Run processed CSV contract tests

Command:

```powershell
python -m unittest tests.test_data_contract
```

What this does:

- checks that the legacy processed CSV exists
- compares the refactor processed snapshot against the legacy processed CSV
- checks that warehouse-required input columns still exist

Normal output should include:

- `Ran ... tests`
- `OK`

Writes file or DB:

- No

### 5. Run warehouse structure tests

Command:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_warehouse_structure
```

What this does:

- checks the structure of the warehouse DataFrames produced by `src.warehouse`
- validates expected columns, uniqueness, row counts, and basic dtype semantics

Normal output should include:

- `Loaded processed data`
- `Ran ... tests`
- `OK`

Writes file or DB:

- No

### 6. Optional: write a new processed CSV snapshot

Command:

```powershell
.\.venv\Scripts\python.exe -m src.preprocess --output data/processed/manufacturing_data_processed_refactor.csv
```

What this does:

- runs the refactored preprocess flow
- writes a new processed CSV to the path you provide

Normal output should include:

- the dry-run style summary
- `Wrote processed CSV to: ...`

Writes file or DB:

- Writes a file
- Does not write to MySQL

### 7. Optional and risky: attempt warehouse write

Command:

```powershell
.\.venv\Scripts\python.exe -m src.warehouse --write
```

What this does:

- attempts to create a DB engine from environment variables
- attempts to write dimension and fact tables to MySQL

Normal output should include either:

- a clear message saying DB config is incomplete, or
- import progress messages if your environment is fully configured

Writes file or DB:

- Writes to MySQL
- Does not write CSV files

## Safe vs Risky Commands

### Safe commands

These are safe by default:

- `.\.venv\Scripts\python.exe -m src.preprocess`
- `.\.venv\Scripts\python.exe -m src.warehouse`
- `python -m unittest tests.test_data_contract`
- `.\.venv\Scripts\python.exe -m unittest tests.test_warehouse_structure`

Why they are safe:

- they are read-only or dry-run in the current project state
- they do not write MySQL
- they do not overwrite the legacy processed CSV

### Commands that write a new CSV

- `.\.venv\Scripts\python.exe -m src.preprocess --output ...`

Why to be careful:

- this writes a new processed CSV to the exact path you pass
- it does not overwrite the legacy processed CSV unless you explicitly point at that file

### Commands that may write MySQL

- `.\.venv\Scripts\python.exe -m src.warehouse --write`

Why to be careful:

- this attempts database writes
- it depends on environment variables like `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME`

### When `--clear-existing` can matter

`--clear-existing` only matters if it is combined with `--write`.

Example:

```powershell
.\.venv\Scripts\python.exe -m src.warehouse --write --clear-existing
```

Meaning:

- warehouse tables may be truncated before import
- this is the highest-risk command path in the new entrypoint

Do not use it unless you understand the target database and really intend to replace the current warehouse contents.

## Common Beginner Mistakes

### Using the wrong Python environment

Symptom:

- commands fail with errors like `No module named pandas`

Fix:

- use `.\.venv\Scripts\python.exe` instead of system `python`

### Forgetting that `src.preprocess` is dry-run by default

Symptom:

- you expect a new CSV file, but no file appears

Fix:

- pass `--output <path>` if you want a new processed CSV written

### Trying `src.warehouse --write` before setting environment variables

Symptom:

- warehouse write is skipped with a configuration message

Fix:

- set your DB environment variables first, based on `.env.example`

### Thinking the new entrypoints already replaced the legacy scripts

Symptom:

- confusion about which files are authoritative

Fix:

- remember:
  - `data_preparation+.py` is still the preprocessing source of truth
  - `data_import.py` is still the warehouse import source of truth
  - `src/preprocess.py` and `src/warehouse.py` are safer transition entrypoints

## What To Read After Running

Once the commands above make sense, the best next files to read are:

- [schema.sql](C:\Itmes_2\sql\schema.sql)
- [views.sql](C:\Itmes_2\sql\views.sql)
- [data_dictionary.md](C:\Itmes_2\docs\data_dictionary.md)

That gives you the best current picture of:

- processed data structure
- warehouse table structure
- current KPI meanings
