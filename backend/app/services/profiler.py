from pathlib import Path

import pandas as pd


def load_dataset(file_path: str):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    if extension == ".xlsx":
        return pd.read_excel(file_path)

    if extension == ".json":
        return pd.read_json(file_path)

    if extension == ".parquet":
        return pd.read_parquet(file_path)

    raise ValueError(f"Unsupported file format: {extension}")


def profile_dataset(file_path: str):
    df = load_dataset(file_path)

    columns = []

    for column in df.columns:
        columns.append(
            {
                "name": str(column),
                "data_type": str(df[column].dtype),
                "missing_values": int(df[column].isna().sum()),
                "unique_values": int(df[column].nunique()),
            }
        )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_details": columns,
    }