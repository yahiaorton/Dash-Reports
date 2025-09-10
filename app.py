import pandas as pd
from utilities.query_utils import *
from utilities.table_utils import *
import datetime as dt

import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from ui.sidebar_inputs import sidebar_inputs

DEFAULT_STR_ID = 92
DEFAULT_ORG_IDS = None

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

sidebar = html.Div(
    className="d-flex flex-column flex-shrink-0 p-3 bg-body-tertiary",
    style={"width": "280px", "height": "100vh"},
    children=[
        # Brand
        dbc.Row(
            className="align-items-center justify-content-between",
            children=[
                dbc.Col([html.Span("Filters", className="fs-4")]),
                dbc.Col([dbc.Button("Generate", id="generate-button", color="primary", className="ms-5", n_clicks=0, type="button")]),
            ],
        ),

        html.Hr(),

        # Input Data Form (pills)
        dbc.Nav(
            [
                dbc.Form(sidebar_inputs),
            ],
            vertical=True,
            pills=True,
            className="mb-auto overflow-y-auto",
        ),

        html.Hr(),
    ],
)

def build_report_tab(report_title: str):
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    children=[
                        dbc.Col(
                            children=[
                                html.H2(f"{report_title} Data Report"),
                                html.P("Comprehensive personnel data and organizational information", className="mb-4 text-muted"),
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            children=[
                                dbc.Button(
                                    children=[html.I(className="bi bi-download me-2"), f"Download {report_title} Report"], 
                                    id=f"{report_title.lower()}-download-button", 
                                    outline=True,
                                    color="dark", 
                                    className="ms-5", 
                                    n_clicks=0, 
                                    type="button"
                                ),
                                dcc.Download(id=f"{report_title.lower()}-download"),
                            ],
                            width="auto",
                        ),
                    ],
                    className="justify-content-between",
                ),
                dbc.Spinner(
                    children=html.Div(
                        className="table-modern",
                        children=DataTable(
                            id=f"{report_title.lower()}-data-table", 
                            columns=[], 
                            data=[], 
                            style_table={"overflowX": "auto"},
                            style_cell={"textAlign": "center"},
                            style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
                            sort_action="native",
                            sort_mode="multi",
                            page_action="native",
                            page_size=10,
                            style_as_list_view=True
                        )
                    ),
                    color="primary",
                ),
                
            ]
        ),
        className="border-0",
    )

# Optional: a main content area to the right
content = html.Div(
    className="p-4 overflow-auto",
    children=[
        dbc.Tabs([
            dbc.Tab(build_report_tab("Military"), label="Military Tab", tab_id="Military Tab"),
            dbc.Tab(build_report_tab("Custodies"), label="Custodies Tab", tab_id="Custodies Tab"),
        ],
        active_tab="Military Tab",
        id="tabs",
        ),
    ],
)

app.layout = html.Div([sidebar, content], className="d-flex")

@app.callback(
    Output("military-data-table", "columns"),
    Output("military-data-table", "data"),
    Output("custodies-data-table", "columns"),
    Output("custodies-data-table", "data"),
    Input("tabs", "active_tab"),
    Input("generate-button", "n_clicks"),
    State("company_ID_input", "value"),
    State("person_inst_IDs_input", "value"),
    State("company_type_input", "value"),
    State("business_entity_input", "value"),
    State("with_child_input", "value"),
    State("military_status_input", "value"),
    State("employee_status_input", "value"),
    State("financial_company_IDs_input", "value"),
    State("custody_IDs_input", "value"),
)
def switch_tab(at, n_clicks, company_id, person_ids, company_type, business_entity_id, with_child, military_status, employee_status, financial_company_ids, custody_ids):
    if at == "Military Tab":    
        query = build_millitary_query(
            DEFAULT_STR_ID,
            DEFAULT_ORG_IDS,
            company_id,
            person_ids,
            company_type,
            business_entity_id,
            with_child,
            military_status, 
            financial_company_ids
        )
    else:
        query = build_custodies_query(
            DEFAULT_STR_ID,
            DEFAULT_ORG_IDS,
            company_id,
            person_ids,
            company_type,
            business_entity_id,
            with_child,
            employee_status,
            financial_company_ids,
            custody_ids
        )
    
    df = get_df_from_query(query)
    
    columns = infer_dash_columns(df)
    data = df.to_dict("records")

    return columns, data, columns, data

@dash.callback(
    Output("military-download", "data"),
    Input("military-download-button", "n_clicks"),
    State("military-data-table", "derived_virtual_data"),  # current filtered/sorted view
    prevent_initial_call=True,
)
def download_military_data(n, rows):
    if not rows:
        raise PreventUpdate
    df = pd.DataFrame(rows)
    fname = f"military_report_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return dcc.send_data_frame(df.to_excel, fname, sheet_name="Report", index=False)

@dash.callback(
    Output("custodies-download", "data"),
    Input("custodies-download-button", "n_clicks"),
    State("custodies-data-table", "derived_virtual_data"),
    prevent_initial_call=True,
)
def download_custodies_data(n, rows):
    if not rows:
        raise PreventUpdate
    df = pd.DataFrame(rows)
    fname = f"custodies_report_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return dcc.send_data_frame(df.to_excel, fname, sheet_name="Report", index=False)


if __name__ == '__main__':

    app.run(debug=False, host="0.0.0.0", port=8050)
