"""Scaffold for future validation helpers."""

from __future__ import annotations

import csv
from pathlib import Path

from src.config import LEGACY_PROCESSED_CSV


REQUIRED_PROCESSED_COLUMNS = (
    "production_time",
    "equipment_id",
    "oee",
)


def processed_file_exists(path: Path | None = None) -> bool:
    """Return whether the processed CSV currently exists."""
    target = path or LEGACY_PROCESSED_CSV
    return target.exists()


def read_processed_header(path: Path | None = None) -> list[str]:
    """Read only the header row from the processed CSV."""
    target = path or LEGACY_PROCESSED_CSV
    with target.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def validate_processed_contract(path: Path | None = None) -> tuple[bool, list[str]]:
    """Check whether key contract columns are present in the processed CSV."""
    header = read_processed_header(path)
    missing = [column for column in REQUIRED_PROCESSED_COLUMNS if column not in header]
    return (len(missing) == 0, missing)
