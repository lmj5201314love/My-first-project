# AGENTS.md

## Project

This is a student manufacturing data analysis project based on the AI4I 2020 dataset.
Current goal: refactor the existing scripts into a cleaner, modular local project without changing the business intent.

## Current source of truth

- `data_preparation+.py` is the main reference for preprocessing logic.
- `data_import.py` is the main reference for MySQL import logic.
- `ai4i2020.csv` is the raw input dataset.
- `manufacturing_data_processed.csv` is the current processed output.

## Current business intent

The project simulates a manufacturing analytics workflow:

- generate production time and shifts
- map product types to production lines and equipment
- derive process stability features
- compute defect rate, quality metrics, and proxy OEE
- import dimension and fact tables into MySQL
- validate data integrity and business plausibility

## Non-goals for now

Do NOT:

- add web app / API / frontend
- add ML training pipeline yet
- add Power BI assets yet
- rewrite the whole repository at once
- delete legacy scripts unless explicitly requested

## Refactor rules

- Prefer small, high-confidence changes
- Create new modular code under `src/`
- Keep old scripts for reference until new flow is verified
- Use functions with clear names and docstrings
- Use type hints where reasonable
- Avoid hard-coded secrets
- Keep comments concise and useful
- Preserve current business logic first; improve logic only when explicitly requested

## Data safety

- Do not silently overwrite important files
- Do not delete source CSV files
- Before changing data logic, explain the impact

## Output contract for every task

After each task, report:

1. files changed
2. what changed in each file
3. commands run
4. result summary
5. risks / assumptions
6. next recommended step
