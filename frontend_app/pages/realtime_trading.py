import pandas as pd
from dash import html, dcc, Input, Output, callback, ctx
import plotly.express as px
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config
import dash_bootstrap_components as dbc
import time

db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)

def layout():
    """
    Layout for the Real-time Trading page.
    - Includes a ticker input filter
    - Real-time updating price chart
    - Key metrics display
    """
    return html.Div(
        children=[
            html.H2("Real-time Trading Dashboard", style={"marginBottom": "20px"}),
            html.Div(
                children=[
                    html.Label("Filter by Ticker(s):", style={"display": "block"}),
                    dcc.Input(id='realtime-ticker-input', type='text', placeholder='e.g. AAPL,MSFT', style={"width": "300px", "marginRight": "10px"}),
                    dbc.Button("Update", id='realtime-update-button', color="primary"),
                ],
                style={"marginBottom": "20px"}
            ),
            html.Div(
                children=[
                    html.H4("Latest Key Metrics", style={"marginBottom": "10px"}),
                    html.Div(id='realtime-key-metrics', style={"marginBottom": "20px"})
                ]
            ),
            dcc.Graph(id='realtime-price-chart'),
            dcc.Interval(
                id='realtime-interval',
                interval=2000, # 2 seconds
                n_intervals=0
            )
        ]
    )

@callback(
    Output('realtime-price-chart', 'figure'),
    Output('realtime-key-metrics', 'children'),
    Input('realtime-interval', 'n_intervals'),
    Input('realtime-update-button', 'n_clicks'),
    Input('realtime-ticker-input', 'value')
)
def update_realtime_chart(n_intervals, n_clicks, ticker_value):
    """
    Callback to update the real-time chart and metrics every 2 seconds or when user updates ticker filter.
    """
    if ticker_value:
        tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]
    else:
        tickers = ["AAPL"]  # Default ticker if none provided

    data = db_handler.fetch_live_trades(tickers=tickers, limit=200)
    if not data:
        # Handle no data scenario gracefully
        fig = px.line(title="No Data Available")
        metrics = html.Div("No recent trades found.", style={"color": "red"})
        return fig, metrics

    df = pd.DataFrame(data, columns=["localTS", "ticker", "price", "size", "exchange"])
    df.sort_values(by="localTS", inplace=True)

    # Real-time line chart of price vs time
    fig = px.line(df, x="localTS", y="price", color="ticker", title="Real-time Price Updates")
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20))

    # Key metrics: current price, total trades in last 10 seconds
    # Assume localTS is datetime(6), we consider last 10 seconds from max localTS
    if not df.empty:
        latest_time = df["localTS"].max()
        time_window_start = latest_time - pd.Timedelta(seconds=10)
        recent_df = df[df["localTS"] >= time_window_start]
        total_trades_10s = len(recent_df)
        current_prices = df.groupby("ticker")["price"].last().to_dict()

        metrics_list = []
        for t in tickers:
            cp = current_prices.get(t, "N/A")
            metrics_list.append(html.Div(f"Ticker: {t}, Current Price: {cp}", style={"marginBottom": "5px"}))

        metrics_list.append(html.Div(f"Total Trades (last 10s): {total_trades_10s}"))
        metrics = html.Div(metrics_list)
    else:
        metrics = html.Div("No recent trades found.")

    return fig, metrics
