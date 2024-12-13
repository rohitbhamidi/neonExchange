import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from frontend_app.components.layout import serve_layout
from frontend_app.pages import realtime_trading, analytics

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], 
                suppress_callback_exceptions=True, 
                title="Stocks Dashboard")

app.layout = serve_layout()

@app.callback(
    dash.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/realtime':
        return realtime_trading.layout()
    elif pathname == '/analytics':
        return analytics.layout()
    else:
        return realtime_trading.layout()

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
