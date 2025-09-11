import pandas as pd
import openpyxl
from urllib.parse import parse_qs, urlparse
from datetime import datetime

import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

from utils.query_utils import *
from utils.table_utils import *
from utils.aggrid_utils import *

from components.components import get_aggrid_component

DF = None
DF_CURRENT = None
TABLE = Tables.Military

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.layout = dbc.Container(
    children=[
        dbc.Card(
            children=[
                dbc.CardBody(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(dbc.Input(id="search_field", placeholder="🔍 Search...", type="text", className="form-control", debounce=True), width="auto"),
                                dbc.Col(
                                    dbc.Row(
                                        children=[
                                            dbc.Col(dbc.Button(children=[html.I(className="bi bi-funnel-fill"), " Filter"], id="filter-button", color="secondary", className="ml-2"), width="auto"),
                                            dbc.Col(dbc.Button("Export", id="export-button", color="dark", outline=True, className="ml-2"), width="auto"),
                                        ]
                                    ),
                                    width="auto",
                                ),
                            ],
                            justify="between",
                            className="mb-3",
                        ),
                        dbc.Row(
                            children=get_aggrid_component(),
                            className="overflow-auto",
                        )
                    ],
                ),
            ],
        ),
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="intermediate-store"),
        dcc.Download(id="download-dataframe-xlsx"),
    ],
    fluid=True,
    className="mt-3",
)

@callback(
    Output("report-table", "columnDefs"),
    Output("intermediate-store", "data"),
    Input("url", "search"),
)
def build_column_defs(search):
    # Extract query params
    query_params = parse_qs(urlparse(search).query)

    params_dict = {key: value[0] for key, value in query_params.items()}

    df = get_df_from_query(build_query(TABLE, params_dict))

    global DF
    DF = df

    return make_column_defs(df), {"value": "Done"}

@callback(
    Output("report-table", "getRowsResponse"),
    Input("report-table", "getRowsRequest"),
    Input("search_field", "value"),
    Input("intermediate-store", "data"),
)
def infinite_scroll(request, search_value, _store_data):

    global DF
    global DF_CURRENT
    
    if not isinstance(DF, pd.DataFrame):
        return no_update
    dff = DF.copy()

    if search_value is not None:
        dff = apply_global_search(dff, search_value)

    if request:
        if request["filterModel"]:
            dff = apply_filters(request, dff)

        if request["sortModel"]:
            dff = apply_sort(request, dff)

        DF_CURRENT = dff

        lines = len(dff.index)
        if lines == 0:
            lines = 1

        partial = dff.iloc[request["startRow"]: request["endRow"]]
        return {"rowData": partial.to_dict("records"), "rowCount": lines}
    
@callback(
    Output("download-dataframe-xlsx", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True
)
def export(n_clicks):
    global DF_CURRENT

    if not isinstance(DF_CURRENT, pd.DataFrame):
        return no_update
    
    return dcc.send_data_frame(DF_CURRENT.to_excel, f"{TABLE}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx")

if __name__ == '__main__':
    app.run(debug=True)
