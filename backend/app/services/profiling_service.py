from __future__ import annotations

import gzip
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_json_value(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def _safe_read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def _safe_read_json(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            return pd.DataFrame(payload["data"])
        return pd.DataFrame([payload])
    raise ValueError("JSON dataset must be a list of objects or a dict with a data list.")


def _safe_read_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)


def _safe_read_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def _read_gzip_csv(path: str) -> pd.DataFrame:
    with gzip.open(path, "rb") as gz_handle:
        content = gz_handle.read()
    temp_path = path + ".csv"
    with open(temp_path, "wb") as out:
        out.write(content)
    try:
        return pd.read_csv(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _read_zip_file(path: str) -> pd.DataFrame:
    supported = [".csv", ".json", ".parquet", ".xlsx"]
    with zipfile.ZipFile(path) as archive:
        candidates = [
            name for name in archive.namelist() if Path(name).suffix.lower() in supported
        ]
        if not candidates:
            raise ValueError("The archive does not contain a supported dataset file.")
        if len(candidates) > 5:
            raise ValueError("The archive contains too many dataset files to process safely.")
        target_name = candidates[0]
        extracted = archive.read(target_name)
        temp_dir = Path(tempfile.mkdtemp(prefix=f"{Path(path).stem}_zip_extract_", dir=str(Path(path).parent)))
        target_file = temp_dir / Path(target_name).name
        target_file.write_bytes(extracted)
        try:
            suffix = target_file.suffix.lower()
            if suffix == ".csv":
                return pd.read_csv(target_file)
            if suffix == ".json":
                with open(target_file, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, list):
                    return pd.DataFrame(payload)
                if isinstance(payload, dict) and isinstance(payload.get("data"), list):
                    return pd.DataFrame(payload["data"])
                return pd.DataFrame([payload])
            if suffix == ".xlsx":
                return pd.read_excel(target_file)
            if suffix == ".parquet":
                return pd.read_parquet(target_file)
            raise ValueError("Unsupported archive dataset file type.")
        finally:
            if temp_dir.exists():
                for child in temp_dir.iterdir():
                    if child.is_file():
                        child.unlink()
                temp_dir.rmdir()


def load_dataset(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return _safe_read_csv(file_path)
    if suffix == ".json":
        return _safe_read_json(file_path)
    if suffix == ".xlsx":
        return _safe_read_excel(file_path)
    if suffix == ".parquet":
        return _safe_read_parquet(file_path)
    if suffix == ".gz":
        return _read_gzip_csv(file_path)
    if suffix == ".zip":
        return _read_zip_file(file_path)
    raise ValueError(f"Unsupported file format: {suffix}")


def _safe_summary(column: pd.Series) -> dict[str, Any]:
    missing = int(column.isna().sum())
    unique = int(column.nunique(dropna=True))
    example = None
    if not column.empty:
        values = column.dropna()
        if not values.empty:
            example = _normalize_json_value(values.iloc[0])
    return {
        "name": str(column.name),
        "dtype": str(column.dtype),
        "missing_values": missing,
        "missing_rate": round((missing / len(column)) * 100, 2) if len(column) else 0.0,
        "unique_values": unique,
        "example": example,
    }


def profile_dataset(file_path: str) -> dict[str, Any]:
    df = load_dataset(file_path)
    columns = [_safe_summary(df[column]) for column in df.columns]
    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    categorical_columns = [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_datetime64_any_dtype(df[col])]
    date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

    profile = {
        "filename": Path(file_path).name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "column_names": [str(name) for name in df.columns],
        "columns": [_normalize_json_value(column) for column in columns],
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "num_numeric_columns": len(numeric_columns),
        "numeric_columns": [str(col) for col in numeric_columns],
        "categorical_columns": [str(col) for col in categorical_columns],
        "date_columns": [str(col) for col in date_columns],
        "data_types": {str(col): str(df[col].dtype) for col in df.columns},
        "quality": {
            "health": "good" if df.isna().sum().sum() == 0 else "warning",
            "missing_percentage": round((df.isna().sum().sum() / max(len(df) * len(df.columns), 1)) * 100, 2),
            "duplicate_percentage": round((df.duplicated().sum() / max(len(df), 1)) * 100, 2),
        },
    }
    return _normalize_json_value(profile)
