"""Minimal shared configuration for the future modular project."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"

# Legacy files remain the current source of truth during the scaffold stage.
LEGACY_RAW_CSV = PROJECT_ROOT / "ai4i2020.csv"
LEGACY_PROCESSED_CSV = PROJECT_ROOT / "manufacturing_data_processed.csv"
LEGACY_PREPROCESS_SCRIPT = PROJECT_ROOT / "data_preparation+.py"
LEGACY_WAREHOUSE_SCRIPT = PROJECT_ROOT / "data_import.py"


def get_database_config() -> dict[str, str]:
    """Read database connection settings from environment variables."""
    return {
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "3306"),
        "database": os.getenv("DB_NAME", ""),
    }
