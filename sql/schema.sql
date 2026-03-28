-- MySQL schema draft for the current warehouse staging design.
-- This version intentionally follows the DataFrame structures produced by src/warehouse.py.
-- It is a minimal, beginner-friendly first pass rather than a fully optimized production schema.

-- Use the project database first if needed.
-- Example:
-- USE manufacturing_oee;

DROP TABLE IF EXISTS fact_equipment_status;
DROP TABLE IF EXISTS dim_time;
DROP TABLE IF EXISTS dim_equipment;

-- Equipment dimension
-- Source mapping:
-- build_equipment_dimension() ->
-- equipment_id, production_line, equipment_type, theoretical_cycle_time, installation_date
CREATE TABLE dim_equipment (
    equipment_id VARCHAR(32) NOT NULL COMMENT 'Business key generated from production line and sequence, e.g. Line1_EQ01',
    production_line VARCHAR(32) NOT NULL COMMENT 'Production line mapped from Type',
    equipment_type VARCHAR(8) NOT NULL COMMENT 'Equipment type mapped from source Type: L / M / H',
    theoretical_cycle_time INT NOT NULL COMMENT 'Theoretical cycle time in seconds',
    installation_date DATE NOT NULL COMMENT 'Static placeholder date from current Python logic',
    PRIMARY KEY (equipment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Equipment dimension based on current warehouse DataFrame contract';

-- Time dimension
-- Source mapping:
-- build_time_dimension() ->
-- full_date, time_key, year, month, day, week_of_year, is_workday
CREATE TABLE dim_time (
    time_key INT NOT NULL COMMENT 'Date key in YYYYMMDD format',
    full_date DATE NOT NULL COMMENT 'Calendar date derived from production_time',
    year SMALLINT NOT NULL COMMENT 'Calendar year',
    month TINYINT NOT NULL COMMENT 'Calendar month number',
    day TINYINT NOT NULL COMMENT 'Calendar day of month',
    week_of_year TINYINT NOT NULL COMMENT 'ISO week number from pandas isocalendar',
    is_workday BOOLEAN NOT NULL COMMENT 'True for weekday, false for weekend under current logic',
    PRIMARY KEY (time_key),
    UNIQUE KEY uq_dim_time_full_date (full_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Date-grain time dimension based on current warehouse DataFrame contract';

-- Fact table
-- Source mapping:
-- build_fact_table() ->
-- equipment_id, time_key, production_time, shift, air_temperature, process_temperature,
-- rotational_speed, torque, tool_wear, process_stability_score, planned_production,
-- actual_production, defect_count, qualified_count, defect_rate, availability,
-- performance, quality_rate, oee, machine_failure
--
-- Reasonable current-stage assumptions:
-- 1. Numeric KPI fields are stored as DECIMAL for readability and stable SQL aggregation.
-- 2. There is no natural single-column business key in the current Python output,
--    so a surrogate fact_id is used here for a simple first-pass DDL.
CREATE TABLE fact_equipment_status (
    fact_id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Surrogate key for the current first-pass fact table',
    equipment_id VARCHAR(32) NOT NULL COMMENT 'Foreign key to dim_equipment',
    time_key INT NOT NULL COMMENT 'Foreign key to dim_time',
    production_time DATETIME NOT NULL COMMENT 'Original production timestamp at 15-minute grain',
    shift VARCHAR(16) NOT NULL COMMENT 'Shift label: Day / Evening / Night',
    air_temperature DECIMAL(8,3) NOT NULL COMMENT 'Air temperature in Kelvin',
    process_temperature DECIMAL(8,3) NOT NULL COMMENT 'Process temperature in Kelvin',
    rotational_speed DECIMAL(10,3) NOT NULL COMMENT 'Rotational speed in rpm',
    torque DECIMAL(10,3) NOT NULL COMMENT 'Torque in Nm',
    tool_wear DECIMAL(10,3) NOT NULL COMMENT 'Tool wear in minutes',
    process_stability_score DECIMAL(12,6) NOT NULL COMMENT 'Current process stability score from preprocessing',
    planned_production DECIMAL(12,6) NOT NULL COMMENT 'Planned production quantity for the current time window',
    actual_production DECIMAL(12,6) NOT NULL COMMENT 'Actual production quantity for the current time window',
    defect_count INT NOT NULL COMMENT 'Rounded defect count from preprocessing',
    qualified_count INT NOT NULL COMMENT 'Rounded qualified count from preprocessing',
    defect_rate DECIMAL(12,6) NOT NULL COMMENT 'Defect rate from preprocessing',
    availability DECIMAL(12,6) NOT NULL COMMENT 'Availability factor used in current OEE calculation',
    performance DECIMAL(12,6) NOT NULL COMMENT 'Performance factor used in current OEE calculation',
    quality_rate DECIMAL(12,6) NOT NULL COMMENT 'Quality factor used in current OEE calculation',
    oee DECIMAL(12,6) NOT NULL COMMENT 'Current OEE proxy metric',
    machine_failure BOOLEAN NOT NULL COMMENT 'Machine failure flag mapped to boolean semantics',
    PRIMARY KEY (fact_id),
    KEY idx_fact_equipment_id (equipment_id),
    KEY idx_fact_time_key (time_key),
    KEY idx_fact_production_time (production_time),
    CONSTRAINT fk_fact_equipment
        FOREIGN KEY (equipment_id) REFERENCES dim_equipment (equipment_id),
    CONSTRAINT fk_fact_time
        FOREIGN KEY (time_key) REFERENCES dim_time (time_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Equipment status fact table based on current warehouse DataFrame contract';
