# Manufacturing Data Analysis Project

## Current Status

This repository is being reorganized into a small, maintainable local project without rewriting the current workflow all at once.

Current source of truth:

- `ai4i2020.csv`
- `data_preparation+.py`
- `manufacturing_data_processed.csv`
- `data_import.py`

Current real pipeline:

`ai4i2020.csv` -> `data_preparation+.py` -> `manufacturing_data_processed.csv` -> `data_import.py`

At this stage, the legacy scripts remain authoritative for business logic:

- `data_preparation+.py` is still the preprocessing source of truth.
- `data_import.py` is still the warehouse import source of truth.
- `src/warehouse.py` is now a safer new-entry scaffold for warehouse work, but it does not replace the legacy script yet.

The new `src/` package is only a scaffold for incremental migration.

## Current Goal

The current goal is to create a minimal project skeleton that makes the next refactor easier for a beginner to follow.

This stage does not:

- rewrite preprocessing logic
- rewrite warehouse import logic
- change business formulas
- delete legacy files

## Repository Layout

- `data/raw/`: intended location for raw input data in the future
- `data/processed/`: intended location for processed output data in the future
- `src/`: modular Python code that will gradually replace legacy scripts
- `sql/`: schema and view definitions for warehouse setup
- `tests/`: lightweight checks and contract tests
- `prompts/`: guided prompts for the next refactor steps
- `docs/`: scope and project notes

## Dependencies

See `requirements.txt` for the current minimal Python dependencies used by the existing scripts.

## Planned Migration Path

1. Keep legacy scripts unchanged as the reference implementation.
2. Move preprocessing logic into `src/preprocess.py` in small steps.
3. Move validation logic into `src/validate.py`.
4. Move warehouse import logic into `src/warehouse.py`.
5. Add SQL schema and view definitions under `sql/`.
6. Compare new modules against legacy outputs before retiring old scripts.

## Safer Warehouse Entry

The new `src/warehouse.py` is designed as a safer first step for warehouse refactoring:

- it reads database configuration from environment variables instead of hard-coding credentials
- it prints a safe configuration summary without exposing the password
- it defaults to a dry-run summary mode
- it does not write to MySQL unless you explicitly pass a write flag
- it does not truncate existing tables unless you explicitly pass a clear flag together with a write flag

This means the legacy warehouse script is still the source of truth, while the new entry point is a safer place to gradually move import logic.

## Risk Notes

The current legacy import flow still contains risks that are intentionally not changed in this skeleton stage, including:

- database credentials handled outside the new scaffold but still present in legacy code
- potentially destructive import behavior in the legacy warehouse script
- file-path coupling between legacy scripts

The new scaffold prepares a safer place to fix those issues later, but does not change the current behavior yet.
