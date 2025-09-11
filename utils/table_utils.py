import pandas as pd
import numpy as np
from dash.dash_table.Format import Format, Group, Scheme

def infer_dash_columns(df: pd.DataFrame):
    cols = []
    for col in df.columns:
        dt = df[col].dtype

        if pd.api.types.is_datetime64_any_dtype(dt):
            col_type = "datetime"
        elif pd.api.types.is_numeric_dtype(dt):
            col_type = "numeric"
        elif pd.api.types.is_bool_dtype(dt):
            col_type = "any"      # DataTable has no boolean type; treat as 'any' (or 'text')
        else:
            col_type = "text"

        spec = {"name": col, "id": col, "type": col_type}

        cols.append(spec)
    return cols

def apply_global_search(df: pd.DataFrame, search_value: str) -> pd.DataFrame:
    q = (search_value or "").strip()
    if q:
        cols = df.columns
        mask = np.column_stack([
            df[c].astype(str).str.contains(q, case=False, na=False) for c in cols if c in df.columns
        ]).any(axis=1)
        
        return df[mask]

    return df


def sort_df_by(df: pd.DataFrame, sort_by: list) -> pd.DataFrame:
    print(sort_by)
    if not sort_by:
        return df

    valid = [s for s in sort_by if isinstance(s, dict) and s.get("column_id") in df.columns]
    if not valid:
        return df

    by  = [s["column_id"] for s in valid]
    asc = [s.get("direction", "asc") == "asc" for s in valid]

    return df.sort_values(by=by, ascending=asc, kind="mergesort", na_position="last")
