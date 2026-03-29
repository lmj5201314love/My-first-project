# Data Dictionary

This document explains the current field meanings used by the repository. It reflects the current code and SQL files in the project today. It is not a final industrial data standard.

## How To Read This Document

- `Raw field`: comes directly from the original AI4I dataset
- `Derived field`: created by current preprocessing or warehouse logic
- `Proxy / simulated metric`: a metric that follows the current project rules and intent, but should not be treated as a plant-certified industrial KPI definition

## Processed CSV Key Fields

The processed CSV is currently represented by `manufacturing_data_processed.csv` and the refactor snapshot under `data/processed/`.

| Field | Type In Practice | Source | Meaning |
| --- | --- | --- | --- |
| `UDI` | integer-like | Raw field | Unique record identifier from the source dataset |
| `Type` | categorical | Raw field | Product or load type from AI4I, currently mapped as `L`, `M`, `H` |
| `Air temperature [K]` | numeric | Raw field | Air temperature in Kelvin |
| `Process temperature [K]` | numeric | Raw field | Process temperature in Kelvin |
| `Rotational speed [rpm]` | numeric | Raw field | Rotational speed in rpm |
| `Torque [Nm]` | numeric | Raw field | Torque in Nm |
| `Tool wear [min]` | numeric | Raw field | Tool wear in minutes |
| `Machine failure` | 0/1-like | Raw field | Source failure label from AI4I |
| `production_time` | datetime-like | Derived field | Synthetic production timestamp added during preprocessing |
| `shift` | categorical | Derived field | Shift label derived from `production_time`: `Day`, `Evening`, `Night` |
| `production_line` | categorical | Derived field | Line label mapped from `Type` |
| `equipment_id` | categorical | Derived field | Equipment identifier derived from line plus within-type sequence |
| `process_stability_score` | numeric | Derived field, proxy metric | Combined deviation score built from temperature and torque stability |
| `air_temp_dev` | numeric | Derived field | Relative deviation from mean air temperature |
| `process_temp_dev` | numeric | Derived field | Relative deviation from mean process temperature |
| `torque_dev` | numeric | Derived field | Relative deviation from mean torque |
| `theoretical_cycle_time` | numeric | Derived field | Assumed theoretical cycle time in seconds based on `Type` |
| `planned_production` | numeric | Derived field, proxy metric | Planned production quantity for the current 15-minute window |
| `actual_production` | numeric | Derived field, proxy metric | Simulated actual production quantity after performance and random fluctuation |
| `defect_rate` | numeric | Derived field, proxy metric | Simulated defect rate based on process stability and failure penalty |
| `defect_count` | integer-like | Derived field, proxy metric | Rounded defect count for the current record |
| `qualified_count` | integer-like | Derived field, proxy metric | Rounded non-defect count for the current record |
| `availability` | numeric | Derived field, proxy metric | Availability factor used in current OEE logic |
| `performance` | numeric | Derived field, proxy metric | Performance factor used in current OEE logic |
| `quality_rate` | numeric | Derived field, proxy metric | Quality factor used in current OEE logic |
| `oee` | numeric | Derived field, proxy metric | Current project OEE proxy built from availability, performance, and quality |

## Warehouse Tables

### `dim_equipment`

Purpose:
Store stable equipment attributes used by the current warehouse flow.

| Field | Source | Meaning |
| --- | --- | --- |
| `equipment_id` | Derived field | Equipment business key, for example `Line1_EQ01` |
| `production_line` | Derived field | Production line assignment |
| `equipment_type` | Derived field | Equipment type mapped from source `Type` |
| `theoretical_cycle_time` | Derived field | Assumed theoretical cycle time in seconds |
| `installation_date` | Derived field | Static placeholder date used by current warehouse code |

### `dim_time`

Purpose:
Provide date-level calendar context for fact records.

| Field | Source | Meaning |
| --- | --- | --- |
| `time_key` | Derived field | Integer date key in `YYYYMMDD` format |
| `full_date` | Derived field | Calendar date from `production_time` |
| `year` | Derived field | Calendar year |
| `month` | Derived field | Calendar month number |
| `day` | Derived field | Day of month |
| `week_of_year` | Derived field | ISO week number |
| `is_workday` | Derived field | `True` for weekday and `False` for weekend under the current rule |

### `fact_equipment_status`

Purpose:
Store record-level KPI, process, quality, and failure status fields for warehouse analysis.

| Field | Source | Meaning |
| --- | --- | --- |
| `equipment_id` | Derived field | Equipment key linked to `dim_equipment` |
| `time_key` | Derived field | Date key linked to `dim_time` |
| `production_time` | Derived field | Record timestamp at the current 15-minute grain |
| `shift` | Derived field | Shift label |
| `air_temperature` | Raw field renamed | Air temperature in Kelvin |
| `process_temperature` | Raw field renamed | Process temperature in Kelvin |
| `rotational_speed` | Raw field renamed | Rotational speed in rpm |
| `torque` | Raw field renamed | Torque in Nm |
| `tool_wear` | Raw field renamed | Tool wear in minutes |
| `process_stability_score` | Derived field, proxy metric | Combined process stability score |
| `planned_production` | Derived field, proxy metric | Planned output for the time window |
| `actual_production` | Derived field, proxy metric | Simulated actual output |
| `defect_count` | Derived field, proxy metric | Simulated defect count |
| `qualified_count` | Derived field, proxy metric | Simulated qualified count |
| `defect_rate` | Derived field, proxy metric | Simulated defect rate |
| `availability` | Derived field, proxy metric | Current availability factor |
| `performance` | Derived field, proxy metric | Current performance factor |
| `quality_rate` | Derived field, proxy metric | Current quality factor |
| `oee` | Derived field, proxy metric | Current OEE proxy |
| `machine_failure` | Raw field renamed | Boolean-style failure flag in warehouse form |

## Views

### `vw_daily_equipment_kpi`

Purpose:
Show daily KPI averages and production totals by equipment.

Main outputs:

- average `oee`
- average `availability`
- average `performance`
- average `quality_rate`
- total actual production
- total qualified and defect counts
- failure event count

### `vw_failure_summary`

Purpose:
Show how often each equipment appears with failure-labelled records and what average KPI values look like for that equipment.

Main outputs:

- total record count
- failure-labelled record count
- average `oee`
- average `availability`
- average `performance`
- average `quality_rate`
- average `defect_rate`

### `vw_shift_kpi`

Purpose:
Compare KPI behavior across `Day`, `Evening`, and `Night` shifts by production line.

Main outputs:

- shift-level average `oee`
- shift-level average `availability`
- shift-level average `performance`
- shift-level average `quality_rate`
- total production and quality counts
- failure event count

## Current Interpretation Notes

These definitions are intentionally practical and current-stage only:

- current `production_time` is synthetic, not a raw timestamp from the source dataset
- current `production_line` and `equipment_id` are generated mappings, not original source identifiers
- current `defect_rate`, `availability`, `performance`, `quality_rate`, and `oee` are project metrics built from preprocessing rules
- current SQL schema is designed to match the Python DataFrame structure first, not to represent a final industrial warehouse standard

If business logic changes later, this document should be updated together with the tests and SQL files.
