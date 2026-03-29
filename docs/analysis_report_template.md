# Analysis Report Template

This document is a small template for later notebook work, report writing, and portfolio-style project presentation. It is based on the current repository state today.

## Project Goal

This project aims to show how a manufacturing-style dataset can be cleaned, structured, and analyzed to understand equipment performance, shift differences, quality behavior, and failure patterns.

This is a manufacturing / industrial data analysis project first. It is not a pure machine learning project at the current stage.

## Business Questions

The current project is best suited to answer questions like these:

1. Which equipment or production lines show weaker OEE performance?
2. Do `Day`, `Evening`, and `Night` shifts show different KPI patterns?
3. How does machine failure relate to quality and OEE behavior?
4. Which equipment appears more often in failure-labelled records?
5. Which conclusions are supported by the current proxy metrics, and which are still outside the scope of this project?

Where available, later failure analysis can also compare the broader `Machine failure` label with finer AI4I failure mode labels such as `TWF`, `HDF`, `PWF`, `OSF`, and `RNF`.

## Data Scope And Current Assumptions

### Current data sources

- `ai4i2020.csv`
  Raw dataset
- `manufacturing_data_processed.csv`
  Legacy processed output
- `dim_equipment`, `dim_time`, `fact_equipment_status`
  Current warehouse table design documented in SQL

### Current field types

- raw fields:
  source AI4I fields such as `Type`, temperature, rotational speed, torque, tool wear, and `Machine failure`
- derived fields:
  generated fields such as `production_time`, `shift`, `production_line`, `equipment_id`, and `time_key`
- proxy / simulated metrics:
  current project metrics such as `planned_production`, `actual_production`, `defect_rate`, `availability`, `performance`, `quality_rate`, and `oee`
  quality-related findings should be interpreted against the current simulated integer-count quantity logic rather than against certified plant counts

### Current analysis boundary

This project can support:

- KPI comparison across equipment, lines, dates, and shifts
- failure-oriented summaries
- structure-first warehouse analysis

This project should not yet claim:

- industrial-grade OEE certification
- real plant scheduling conclusions
- causal root-cause proof
- production-grade predictive modeling

## Recommended Analysis Flow

Use this sequence when writing a notebook or report:

1. Start with project scope and dataset context.
2. Show overall data shape and key fields.
3. Review equipment- and line-level KPI patterns.
4. Review shift-level KPI differences.
5. Review failure summaries and failure-related KPI behavior.
6. Summarize findings in plain business language.
7. End with limitations and next steps.

This order helps keep the story practical and avoids jumping straight into isolated charts without context.

## Suggested Figures And Tables

### 1. Dataset overview table

Use for:

- row count
- column count
- number of equipment IDs
- date range

Question answered:

- What is the current size and scope of the dataset?

### 2. Daily equipment KPI table

Suggested source:

- `vw_daily_equipment_kpi`

Question answered:

- Which equipment shows lower average OEE or higher defect totals over time?

### 3. Shift KPI comparison chart

Suggested source:

- `vw_shift_kpi`

Question answered:

- Are some shifts consistently weaker on OEE, availability, performance, or quality?

### 4. Failure summary table

Suggested source:

- `vw_failure_summary`

Question answered:

- Which equipment appears most often in failure-labelled records, and how do its KPI averages compare?

### 5. OEE / failure / quality relationship chart

Suggested fields:

- `oee`
- `quality_rate`
- `machine_failure`

Question answered:

- How do failure-labelled records differ from non-failure records under the current proxy KPI logic?

### 6. Production line comparison table or bar chart

Suggested fields:

- `production_line`
- `oee`
- `availability`
- `performance`
- `quality_rate`

Question answered:

- Which production line looks stronger or weaker overall under the current project logic?

## Findings Template

Use this short structure for each major finding:

### Finding 1

- Observation:
  [write the main finding in one sentence]
- Evidence:
  [name the table, view, figure, or KPI summary that supports it]
- Business meaning:
  [explain why this matters in a manufacturing context]
- Current limitation:
  [state what this result does not prove]

### Finding 2

- Observation:
  [write the main finding in one sentence]
- Evidence:
  [name the table, view, figure, or KPI summary that supports it]
- Business meaning:
  [explain why this matters]
- Current limitation:
  [state what this result does not prove]

### Finding 3

- Observation:
  [write the main finding in one sentence]
- Evidence:
  [name the table, view, figure, or KPI summary that supports it]
- Business meaning:
  [explain why this matters]
- Current limitation:
  [state what this result does not prove]

## Limitations And Next Step

Important current limitations:

- current OEE, quality, and production metrics are proxy / simulated project metrics
- current timestamps, lines, and equipment identifiers are partly generated by project rules
- the project is not yet an industrial production system
- the SQL schema and views are a first-pass local design

How this template should be used next:

- notebook / EDA work should follow this structure first
- later BI or dashboard work can reuse the same business questions
- later resume or portfolio descriptions should describe the project as a structured manufacturing analytics simulation project, not as a production plant system
