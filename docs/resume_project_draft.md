# Resume Project Draft

## Project Positioning

This is a local manufacturing / industrial data analysis project built on the AI4I 2020 dataset. Its current focus is not machine learning deployment, but building a clearer analytics workflow for preprocessing, KPI construction, warehouse-style modeling, and failure-oriented analysis.

The project uses proxy / simulated manufacturing metrics such as `planned_production`, `actual_production`, `quality_rate`, and `oee`. These metrics are useful for structured analysis and project presentation, but they should not be described as plant-certified industrial KPIs.

## Resume Title Options

1. Manufacturing KPI Analysis and Failure Pattern Exploration Based on AI4I 2020
2. Industrial Data Analysis Project for Equipment KPI, Shift Performance, and Failure Modes
3. Manufacturing Analytics Workflow Refactor with OEE Proxy Metrics and Failure Mode Analysis

## Tech Stack

- Python
- pandas
- NumPy
- MySQL
- SQL
- Jupyter Notebook
- matplotlib
- unittest

Current project workflow also includes:

- safe-first preprocessing and warehouse entrypoints under `src/`
- processed-data contract tests and warehouse structure tests
- first-pass warehouse schema and view definitions
- notebook-based KPI, shift, and failure analysis

## Resume Bullet Draft

- Refactored a student manufacturing analytics project based on the AI4I 2020 dataset into safer modular entrypoints for preprocessing and warehouse staging, while preserving legacy scripts as source references during migration.
- Reworked simulated production and quality logic from weak float-style quantities to integer-count semantics, improving the analytical usefulness of `planned_production`, `actual_production`, `defect_count`, `qualified_count`, `quality_rate`, and proxy `oee`.
- Built structure checks for processed-data contracts and warehouse DataFrames, covering column contracts, quantity / quality sanity checks, and dimension / fact table consistency before database import.
- Developed a local EDA notebook that analyzes equipment KPI ranking, line-level KPI differences, shift performance, and `Machine failure` plus finer failure mode labels (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) with concise findings and minimal presentation visuals.

## 30-Second Project Pitch

I built a local manufacturing data analysis project on top of the AI4I 2020 dataset. The main work was refactoring legacy preprocessing and warehouse scripts into safer modular entrypoints, improving the simulated quantity and quality logic so the KPI chain was more analytically meaningful, and then using notebook-based analysis to compare equipment, production lines, shifts, and failure modes. It is a manufacturing analytics simulation project rather than a production plant system, so I describe OEE and related metrics as proxy indicators rather than certified industrial KPIs.

## 90-Second Project Pitch

This project started from a legacy script-based manufacturing analytics workflow using the AI4I 2020 dataset. My goal was to turn it into a cleaner local project that is easier to explain, test, and present, without pretending it is a real factory production system.

On the engineering side, I added safer modular entrypoints for preprocessing and warehouse staging, kept the legacy scripts as references, and added tests to protect processed-data contracts and warehouse DataFrame structure. On the data side, I corrected the first version of the quantity and quality chain so that production, defect, and qualified counts follow integer-count semantics instead of tiny float-like values that made quality variation hard to analyze.

On the analysis side, I built a notebook flow covering dataset overview, equipment and production line KPI comparison, shift KPI comparison, and failure analysis using both the broad `Machine failure` label and finer AI4I failure mode labels such as `TWF`, `HDF`, `PWF`, `OSF`, and `RNF`. The current outputs support descriptive manufacturing analysis and project presentation, but I keep the project boundaries explicit: the KPI definitions are still proxy / simulated metrics, and the results should not be framed as industrial-grade root-cause proof.

## Interview Follow-Up Questions To Prepare For

1. Why do you call this OEE a proxy metric?
   Because `availability`, `performance`, and `quality_rate` are constructed from project rules rather than sourced from a real MES or certified plant KPI definition.

2. Why did you change the quantity and quality logic?
   The earlier version used very small float-style quantities, which made `defect_count` nearly always zero and weakened the analytical value of `quality_rate`.

3. What was the value of adding finer failure mode labels?
   They make failure analysis more granular than a single `Machine failure` flag and support comparisons across `TWF`, `HDF`, `PWF`, `OSF`, and `RNF`.

4. Why did you keep the legacy scripts instead of rewriting everything at once?
   Keeping them as source references reduced migration risk and made it easier to validate new modular code against the existing workflow.

5. What role did tests play in the project?
   Tests helped protect processed-data structure, quantity / quality sanity, and warehouse DataFrame contracts while the project was being refactored incrementally.

6. Why build warehouse-style tables and SQL views for a local project?
   It makes the analysis easier to explain in dimensional terms and better matches how manufacturing KPI analysis is often structured in BI or reporting workflows.

7. Why not jump straight into machine learning?
   The project still needed cleaner preprocessing semantics, safer structure, and clearer descriptive analysis before predictive modeling would be credible.

8. What are the main limitations of the current project?
   The metrics are simulated, timestamps and equipment mappings are partly generated, and the project is best presented as a structured manufacturing analytics simulation rather than a production system.
