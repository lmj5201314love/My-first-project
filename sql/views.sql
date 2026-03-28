-- Minimal MySQL analysis views for the current warehouse schema.
-- These views stay intentionally close to the current fact and dimension fields.

-- Daily KPI view by equipment.
-- Purpose:
-- Provide one daily row per equipment with the average KPI values and simple production totals.
CREATE OR REPLACE VIEW vw_daily_equipment_kpi AS
SELECT
    t.full_date,
    e.production_line,
    f.equipment_id,
    AVG(f.oee) AS avg_oee,
    AVG(f.availability) AS avg_availability,
    AVG(f.performance) AS avg_performance,
    AVG(f.quality_rate) AS avg_quality_rate,
    SUM(f.actual_production) AS total_actual_production,
    SUM(f.qualified_count) AS total_qualified_count,
    SUM(f.defect_count) AS total_defect_count,
    SUM(CASE WHEN f.machine_failure = 1 THEN 1 ELSE 0 END) AS failure_events
FROM fact_equipment_status f
JOIN dim_time t
    ON f.time_key = t.time_key
JOIN dim_equipment e
    ON f.equipment_id = e.equipment_id
GROUP BY
    t.full_date,
    e.production_line,
    f.equipment_id;

-- Failure summary view by equipment and line.
-- Purpose:
-- Show how often failures occur and how KPIs behave around failure-labelled records.
CREATE OR REPLACE VIEW vw_failure_summary AS
SELECT
    e.production_line,
    f.equipment_id,
    COUNT(*) AS total_records,
    SUM(CASE WHEN f.machine_failure = 1 THEN 1 ELSE 0 END) AS failure_records,
    ROUND(AVG(f.oee), 6) AS avg_oee,
    ROUND(AVG(f.availability), 6) AS avg_availability,
    ROUND(AVG(f.performance), 6) AS avg_performance,
    ROUND(AVG(f.quality_rate), 6) AS avg_quality_rate,
    ROUND(AVG(f.defect_rate), 6) AS avg_defect_rate
FROM fact_equipment_status f
JOIN dim_equipment e
    ON f.equipment_id = e.equipment_id
GROUP BY
    e.production_line,
    f.equipment_id;

-- Shift KPI view.
-- Purpose:
-- Compare KPI behavior across Day / Evening / Night shifts and production lines.
CREATE OR REPLACE VIEW vw_shift_kpi AS
SELECT
    e.production_line,
    f.shift,
    COUNT(*) AS total_records,
    ROUND(AVG(f.oee), 6) AS avg_oee,
    ROUND(AVG(f.availability), 6) AS avg_availability,
    ROUND(AVG(f.performance), 6) AS avg_performance,
    ROUND(AVG(f.quality_rate), 6) AS avg_quality_rate,
    SUM(f.actual_production) AS total_actual_production,
    SUM(f.qualified_count) AS total_qualified_count,
    SUM(f.defect_count) AS total_defect_count,
    SUM(CASE WHEN f.machine_failure = 1 THEN 1 ELSE 0 END) AS failure_events
FROM fact_equipment_status f
JOIN dim_equipment e
    ON f.equipment_id = e.equipment_id
GROUP BY
    e.production_line,
    f.shift;
