"""Shared configuration helpers for the modular project."""

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


def get_database_config_summary() -> dict[str, str]:
    """Return a safe, beginner-friendly config summary without exposing secrets."""
    config = get_database_config()
    password_status = "set" if config["password"] else "missing"
    return {
        "user": config["user"] or "(missing)",
        "password": f"({password_status})",
        "host": config["host"] or "(missing)",
        "port": config["port"] or "(missing)",
        "database": config["database"] or "(missing)",
    }


def get_missing_database_env_vars() -> list[str]:
    """Return required database environment variable names that are still missing."""
    config = get_database_config()
    missing: list[str] = []

    if not config["user"]:
        missing.append("DB_USER")
    if not config["password"]:
        missing.append("DB_PASSWORD")
    if not config["host"]:
        missing.append("DB_HOST")
    if not config["port"]:
        missing.append("DB_PORT")
    if not config["database"]:
        missing.append("DB_NAME")

    return missing


def get_database_config_help_message() -> str:
    """Return a clear setup message for beginners when env vars are incomplete."""
    missing = get_missing_database_env_vars()
    if not missing:
        return "Database environment variables look complete."

    missing_text = ", ".join(missing)
    return (
        "Database configuration is incomplete. "
        f"Please set these environment variables before writing to MySQL: {missing_text}. "
        "You can copy the values from .env.example into your local environment first."
    )
