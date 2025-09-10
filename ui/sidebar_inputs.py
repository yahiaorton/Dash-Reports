from dash import html
import dash_bootstrap_components as dbc

sidebar_inputs = [
    html.Div(
        [
            html.Label("Enter Company ID: ", htmlFor="company_ID_input"),
            dbc.Input(type="number", step=1, value=1, id="company_ID_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Person IDs: ", htmlFor="person_inst_IDs_input"),
            dbc.Input(type="text", value=None, id="person_inst_IDs_input", placeholder="EX: 1101,1102,1103"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Company Type Code: ", htmlFor="company_type_input"),
            dbc.Input(type="number", step=1, value=None, id="company_type_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Business Entity ID: ", htmlFor="business_entity_input"),
            dbc.Input(type="number", step=1, value=1, id="business_entity_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("With Children", htmlFor="with_child_input"),
            dbc.Checkbox(value=False, id="with_child_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Employee Status Code: ", htmlFor="employee_status_input"),
            dbc.Input(type="number", step=1, value=None, id="employee_status_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Military Status Code: ", htmlFor="military_status_input"),
            dbc.Input(type="number", step=1, value=None, id="military_status_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Financial Company IDs: ", htmlFor="financial_company_IDs_input"),
            dbc.Input(type="text", value=None, id="financial_company_IDs_input"),
        ],
        className="mb-3 me-3",
    ),
    html.Div(
        [
            html.Label("Enter Custody IDs: ", htmlFor="custody_IDs_input"),
            dbc.Input(type="text", value=None, id="custody_IDs_input"),
        ],
        className="mb-3 me-3",
    ),
]