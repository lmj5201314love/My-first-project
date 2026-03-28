"""Scaffold for future warehouse import refactor.

The legacy script `data_import.py` remains the current source of truth.
No import behavior is migrated here yet.
"""

from __future__ import annotations

from src.config import LEGACY_PROCESSED_CSV, LEGACY_WAREHOUSE_SCRIPT, get_database_config


def describe_current_source_of_truth() -> str:
    """Explain which file still owns warehouse import behavior."""
    return f"Legacy warehouse source of truth: {LEGACY_WAREHOUSE_SCRIPT.name}"


def get_processed_input_path() -> str:
    """Return the processed CSV path expected by the future import module."""
    return str(LEGACY_PROCESSED_CSV)


def get_config_summary() -> dict[str, str]:
    """Return a safe summary of database configuration placeholders."""
    config = get_database_config()
    return {
        "user": config["user"],
        "host": config["host"],
        "port": config["port"],
        "database": config["database"],
    }


def import_to_warehouse() -> None:
    """Placeholder for the future modular warehouse import entry point."""
    raise NotImplementedError(
        "Warehouse import logic has not been migrated yet. Use data_import.py for now."
    )
