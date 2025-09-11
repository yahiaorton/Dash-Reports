import dash
import dash_ag_grid as dag

from utils.query_utils import *
from utils.aggrid_utils import *

def get_aggrid_component():
    return dag.AgGrid(
        id="report-table",
        className="ag-theme-alpine",
        rowModelType="infinite",
        columnDefs=[{}],
        defaultColDef = {
            "flex": 1,
            "minWidth": 150,
            "sortable": True,
            "resizable": True,
            "menuTabs": ["filterMenuTab"],
            "floatingFilter": False,
            "cellStyle": {"textAlign": "center", "display": "flex", "justifyContent": "center"},
        },
        dashGridOptions={
            "floatingFilter": False,        # no search box under headers
            "suppressMenuHide": True,       # keep the icon always visible
            "icons": {                      # replace menu icon with a filter glyph
                "menu": "<span class='ag-icon ag-icon-filter' role='presentation'></span>"
            },
            "pagination": True,
            "paginationPageSize": 10,
            "domLayout": "autoHeight",
            "rowSelection": "multiple",  # "single" or "multiple"
            "rowMultiSelectWithClick": True,
            "cacheBlockSize": 20,
        },
        # Required when passing HTML strings (icons) or JS snippets elsewhere
        dangerously_allow_code=True,
    ),