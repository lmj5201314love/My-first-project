"""Scaffold for future preprocessing refactor.

The legacy script `data_preparation+.py` remains the current source of truth.
No business logic is migrated here yet.
"""

from __future__ import annotations

from pathlib import Path

from src.config import LEGACY_PREPROCESS_SCRIPT, LEGACY_PROCESSED_CSV, LEGACY_RAW_CSV


def get_legacy_input_path() -> Path:
    """Return the current raw CSV path used by the legacy flow."""
    return LEGACY_RAW_CSV


def get_legacy_output_path() -> Path:
    """Return the current processed CSV path used by the legacy flow."""
    return LEGACY_PROCESSED_CSV


def describe_current_source_of_truth() -> str:
    """Explain which file still owns preprocessing behavior."""
    return f"Legacy preprocessing source of truth: {LEGACY_PREPROCESS_SCRIPT.name}"


def run_preprocessing() -> None:
    """Placeholder for the future modular preprocessing entry point."""
    raise NotImplementedError(
        "Preprocessing logic has not been migrated yet. Use data_preparation+.py for now."
    )
