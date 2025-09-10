import pandas as pd
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

