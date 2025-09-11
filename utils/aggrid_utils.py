import pandas as pd
from pandas.api.types import (
    is_integer_dtype, is_float_dtype, is_bool_dtype,
    is_datetime64_any_dtype, is_categorical_dtype, is_object_dtype
)

def _infer_filter_for_series(s, *, max_unique_for_set=100, sample=None) -> str:

    if is_bool_dtype(s):
        return "agSetColumnFilter"
    if is_datetime64_any_dtype(s):
        return "agDateColumnFilter"
    if is_integer_dtype(s) or is_float_dtype(s):
        return "agNumberColumnFilter"

    ser = s.dropna()
    pop = len(ser)
    if pop == 0:
        return "agTextColumnFilter"

    # robust, no ValueError
    if sample is None or pop <= sample:
        nunique = ser.nunique()
    else:
        nunique = ser.sample(sample, random_state=0).nunique()

    return "agSetColumnFilter" if nunique <= max_unique_for_set else "agTextColumnFilter"



# Reusable JS snippets (only needed if you want nice date filtering/formatting)
DATE_COMPARATOR_JS = {
    "function": """
    function(filterLocalDateAtMidnight, cellValue) {
        if (cellValue == null || cellValue === '') return -1;
        const d = new Date(cellValue);
        // Compare dates at midnight
        const cellMidnight = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
        const filterMidnight = filterLocalDateAtMidnight.getTime();
        if (cellMidnight < filterMidnight) return -1;
        if (cellMidnight > filterMidnight) return 1;
        return 0;
    }
    """
}

DATE_FORMATTER_JS = {
    "function": "params.value ? new Date(params.value).toLocaleDateString() : ''"
}


def make_column_defs(df: pd.DataFrame,
                     *,
                     set_threshold: int = 100,
                     sample_for_cardinality: int = 5000,
                     include_date_helpers: bool = True):

    coldefs = [{
        "headerName": "Select",
        "field": "select",
        "sortable": False,
        "checkboxSelection": True,   # adds checkbox for selection
        "width": 50,
        "headerClass": "select-checkbox-header",
    }]
    for col in df.columns:
        s = df[col]
        f = _infer_filter_for_series(
            s, max_unique_for_set=set_threshold, sample=sample_for_cardinality
        )
        coldef = {"field": col, "sortable": True, "filter": f}

        if f == "agNumberColumnFilter":
            coldef["type"] = "numericColumn"

        if f == "agDateColumnFilter" and include_date_helpers:
            coldef["filterParams"] = {"comparator": DATE_COMPARATOR_JS}
            coldef["valueFormatter"] = DATE_FORMATTER_JS

        coldefs.append(coldef)
    return coldefs


def df_to_rowdata(df: pd.DataFrame) -> list[dict]:

    out = df.copy()

    # Convert datetimes to ISO strings (keeps server/client sort predictable)
    for c in out.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
        out[c] = out[c].dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Replace NaNs with None
    out = out.where(pd.notna(out), None)

    return out.to_dict("records")

def apply_sort(request, dff):
    sorting = []
    asc = []
    for sort in request["sortModel"]:
        sorting.append(sort["colId"])
        if sort["sort"] == "asc":
            asc.append(True)
        else:
            asc.append(False)
    dff = dff.sort_values(by=sorting, ascending=asc)
    return dff

operators = {
    "greaterThanOrEqual": "ge",
    "lessThanOrEqual": "le",
    "lessThan": "lt",
    "greaterThan": "gt",
    "notEqual": "ne",
    "equals": "eq",
}

def filter_df(dff, filter_model, col):
    if "filter" in filter_model:
        if filter_model["filterType"] == "date":
            crit1 = filter_model["dateFrom"]
            crit1 = pd.Series(crit1).astype(dff[col].dtype)[0]
            if "dateTo" in filter_model:
                crit2 = filter_model["dateTo"]
                crit2 = pd.Series(crit2).astype(dff[col].dtype)[0]
        else:
            crit1 = filter_model["filter"]
            crit1 = pd.Series(crit1).astype(dff[col].dtype)[0]
            if "filterTo" in filter_model:
                crit2 = filter_model["filterTo"]
                crit2 = pd.Series(crit2).astype(dff[col].dtype)[0]
    if "type" in filter_model:
        if filter_model["type"] == "contains":
            dff = dff.loc[dff[col].str.contains(crit1)]
        elif filter_model["type"] == "notContains":
            dff = dff.loc[~dff[col].str.contains(crit1)]
        elif filter_model["type"] == "startsWith":
            dff = dff.loc[dff[col].str.startswith(crit1)]
        elif filter_model["type"] == "notStartsWith":
            dff = dff.loc[~dff[col].str.startswith(crit1)]
        elif filter_model["type"] == "endsWith":
            dff = dff.loc[dff[col].str.endswith(crit1)]
        elif filter_model["type"] == "notEndsWith":
            dff = dff.loc[~dff[col].str.endswith(crit1)]
        elif filter_model["type"] == "inRange":
            if filter_model["filterType"] == "date":
                dff = dff.loc[
                    dff[col].astype("datetime64[ns]").between_time(crit1, crit2)
                ]
            else:
                dff = dff.loc[dff[col].between(crit1, crit2)]
        elif filter_model["type"] == "blank":
            dff = dff.loc[dff[col].isnull()]
        elif filter_model["type"] == "notBlank":
            dff = dff.loc[~dff[col].isnull()]
        else:
            dff = dff.loc[getattr(dff[col], operators[filter_model["type"]])(crit1)]
    elif filter_model["filterType"] == "set":
        dff = dff.loc[dff[col].astype("string").isin(filter_model["values"])]
    return dff

def apply_filters(request, dff):
    filters = request["filterModel"]
    for f in filters:
        try:
            if "operator" in filters[f]:
                if filters[f]["operator"] == "AND":
                    dff = filter_df(dff, filters[f]["condition1"], f)
                    dff = filter_df(dff, filters[f]["condition2"], f)
                else:
                    dff1 = filter_df(dff, filters[f]["condition1"], f)
                    dff2 = filter_df(dff, filters[f]["condition2"], f)
                    dff = pd.concat([dff1, dff2])
            else:
                dff = filter_df(dff, filters[f], f)
        except:
            pass
    return dff
