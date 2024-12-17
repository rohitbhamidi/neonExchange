import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import logging
from frontend_app.config import Config
from frontend_app.components.sidebar import sidebar
from frontend_app.pages import realtime, analytics

logging.basicConfig(level=logging.INFO)

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Modernized Trading Dashboard"
)

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        sidebar(),
        html.Div(id='page-content', style={"marginLeft":"220px","padding":"20px"})
    ]
)

@app.callback(
    dash.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/realtime':
        return realtime.layout()
    elif pathname == '/analytics':
        return analytics.layout()
    else:
        # Default to Real-time if none selected
        return realtime.layout()

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
