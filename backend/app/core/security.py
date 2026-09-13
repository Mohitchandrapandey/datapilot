from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.core.config import ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    unsafe_name = Path(filename).name
    safe_name = unsafe_name.replace("/", "_").replace("\\", "_")
    return safe_name


def is_allowed_extension(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def validate_file_name(filename: str) -> str:
    if not filename or not filename.strip():
        raise ValueError("No file selected.")

    safe_filename = sanitize_filename(filename)
    if not is_allowed_extension(safe_filename):
        raise ValueError("Unsupported file format.")

    if safe_filename in {".", ".."}:
        raise ValueError("Invalid file name.")

    return safe_filename


def is_safe_path(target: Path, root: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False
