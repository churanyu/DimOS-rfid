# Copyright 2026. RFID DimOS integration.

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rfid_service import RfidScanner


def rfid_scanner_python_dir() -> Path:
    """Directory containing rfid_service.py."""
    package_dir = Path(__file__).resolve().parent
    if (package_dir / "rfid_service.py").is_file():
        return package_dir
    return package_dir.parent / "rfid scanner python"


def ensure_rfid_scanner_importable() -> Path:
    """Add the existing RFID API package to sys.path."""
    scanner_dir = rfid_scanner_python_dir()
    if not scanner_dir.is_dir():
        raise FileNotFoundError(
            f"RFID scanner code not found at {scanner_dir}. "
            "Expected the 'rfid scanner python' folder next to dimos_rfid/."
        )
    path = str(scanner_dir)
    if path not in sys.path:
        sys.path.insert(0, path)
    return scanner_dir


def create_direct_scanner(
    *,
    host: str,
    user: str,
    password: str,
    stale_seconds: float,
) -> RfidScanner:
    """Import and construct RfidScanner from the existing API code."""
    ensure_rfid_scanner_importable()
    from rfid_service import RfidScanner, ScannerConfig

    return RfidScanner(
        ScannerConfig(
            host=host,
            user=user,
            password=password,
            stale_seconds=stale_seconds,
        )
    )
