from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.core.config import MAX_FILE_SIZE, UPLOAD_DIR
from app.core.security import sanitize_filename, validate_file_name
from app.services.profiling_service import load_dataset, profile_dataset

DATASETS: dict[str, dict[str, Any]] = {}


def save_uploaded_file(file: UploadFile) -> dict[str, Any]:
    if file.filename is None:
        raise ValueError("No file selected.")

    safe_name = validate_file_name(file.filename)
    file_id = str(uuid.uuid4())
    storage_name = f"{file_id}_{sanitize_filename(safe_name)}"
    storage_path = UPLOAD_DIR / storage_name

    total_size = 0
    with open(storage_path, "wb") as output:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                output.close()
                storage_path.unlink(missing_ok=True)
                raise ValueError("File is too large. Maximum size is 100 MB.")
            output.write(chunk)

    profile = profile_dataset(str(storage_path))
    df = load_dataset(str(storage_path))
    rows = df.head(5000).to_dict(orient="records") if len(df) > 0 else []

    dataset = {
        "id": file_id,
        "filename": safe_name,
        "file_type": Path(safe_name).suffix.lower().lstrip("."),
        "file_size": total_size,
        "storage_path": str(storage_path),
        "status": "processed",
        "created_at": datetime.utcnow().isoformat(),
        "profile": profile,
        "rows": rows,
        "row_count": int(profile.get("row_count", len(rows))),
    }
    DATASETS[file_id] = dataset
    return dataset


def get_dataset(dataset_id: str) -> dict[str, Any]:
    dataset = DATASETS.get(dataset_id)
    if dataset is None:
        raise KeyError(f"Dataset {dataset_id} not found.")
    return dataset
