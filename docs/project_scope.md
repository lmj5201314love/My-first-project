# Project Scope

## Goal

Refactor the current manufacturing analytics project into a modular, maintainable local codebase.

## Current stage

- raw CSV exists
- preprocessing script exists
- processed CSV exists
- MySQL import script exists
- local Python environment is active

## Immediate next milestones

1. create project skeleton
2. move preprocessing logic into `src/preprocess.py`
3. move validation logic into `src/validate.py`
4. move warehouse import logic into `src/warehouse.py`
5. create `sql/schema.sql`
6. create `sql/views.sql`

## Success criteria

- new preprocessing script runs successfully
- new import script runs successfully
- old scripts remain untouched for comparison
- code is easier to read and maintain
