from dash import html, dcc
import dash_bootstrap_components as dbc
from frontend_app.components.navbar import navbar

def serve_layout():
    """
    Serves the main layout for the entire application.
    Includes a navbar and a main content area.
    """
    return html.Div(
        children=[
            html.Div(
                children=[navbar()],
                style={"backgroundColor": "#1E1E1E", "color": "#FFFFFF"}
            ),
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content', style={"padding": "20px", "backgroundColor": "#121212", "color": "#FFFFFF"})
        ],
        style={"fontFamily": "Arial, sans-serif"}
    )
