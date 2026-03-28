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

## Risk Notes

The current legacy import flow still contains risks that are intentionally not changed in this skeleton stage, including:

- database credentials handled outside the new scaffold but still present in legacy code
- potentially destructive import behavior in the legacy warehouse script
- file-path coupling between legacy scripts

The new scaffold prepares a safer place to fix those issues later, but does not change the current behavior yet.
