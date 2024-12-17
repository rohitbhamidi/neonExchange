import pandas as pd
import numpy as np
from dash import html, dcc, Input, Output, callback
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config
import plotly.graph_objects as go
import logging

db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def compute_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100/(1+rs))
    return rsi

def layout():
    return html.Div(
        className="page-content",
        children=[
            html.H1("Real-time Trading", style={"color":"#FFFFFF","fontSize":"24px","marginBottom":"20px"}),
            html.Div(
                className="filter-section",
                children=[
                    html.Label("Ticker:", style={"color":"#E0E0E0"}),
                    # Default ticker now AAPL
                    dcc.Input(id='realtime-ticker-input', type='text', value='AAPL', className='filter-input', placeholder='e.g. AAPL'),
                    html.Button("Update", id='realtime-update-button', className='download-btn', n_clicks=0)
                ]
            ),
            html.Div(
                style={"display":"flex","flexDirection":"row","justifyContent":"space-between","alignItems":"flex-start"},
                children=[
                    html.Div(
                        className="chart-container",
                        style={"flex":"2","marginRight":"20px"},
                        children=[
                            dcc.Graph(id='realtime-price-chart', style={"height":"400px"}),
                            dcc.Interval(
                                id='realtime-interval',
                                interval=Config.UPDATE_INTERVAL_MS, 
                                n_intervals=0
                            )
                        ]
                    ),
                    html.Div(
                        style={"flex":"1"},
                        children=[
                            html.Div(
                                className="metric-card",
                                children=[
                                    html.Div("Current Price", className="metric-title"),
                                    html.Div(id="realtime-current-price", className="metric-value")
                                ]
                            ),
                            html.Div(
                                className="metric-card",
                                children=[
                                    html.Div("Trades (last 10s)", className="metric-title"),
                                    html.Div(id="realtime-total-trades", className="metric-value")
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

@callback(
    Output('realtime-price-chart', 'figure'),
    Output('realtime-current-price', 'children'),
    Output('realtime-total-trades', 'children'),
    Input('realtime-interval', 'n_intervals'),
    Input('realtime-update-button', 'n_clicks'),
    Input('realtime-ticker-input', 'value')
)
def update_realtime_chart(n_intervals, n_clicks, ticker_value):
    ticker_value = ticker_value.strip().upper() if ticker_value else "AAPL"
    logger.info(f"Fetching real-time trades for {ticker_value}")

    # Increase limit to show a longer historical window, e.g. 1000 trades
    data = db_handler.fetch_live_trades([ticker_value], limit=1000)
    if not data:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E",title="No Data Available")
        fig.update_xaxes(tickformat="%H:%M")
        return fig, "N/A", "0"

    df = pd.DataFrame(data, columns=["localTS","ticker","price","size","exchange"])
    df.sort_values(by="localTS", inplace=True)
    df['price'] = df['price'].astype(float)
    df['RSI'] = compute_rsi(df['price'])

    latest_price = df['price'].iloc[-1]

    # Key metrics
    latest_time = df["localTS"].max()
    window_start = latest_time - pd.Timedelta(seconds=10)
    recent_trades = df[df["localTS"] >= window_start]
    total_trades_10s = len(recent_trades)

    # Line chart with RSI as secondary y-axis, linear shape, no markers, smooth transition
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["localTS"],
            y=df["price"],
            mode='lines',
            line=dict(color='#A980FF', width=2),
            name='Price'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["localTS"],
            y=df["RSI"],
            mode='lines',
            line=dict(color='#7A45D1', width=2, dash='dot'),
            name='RSI',
            yaxis='y2'
        )
    )

    # Format time to only show hour:minute
    fig.update_xaxes(tickformat="%H:%M")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C1B1E",
        plot_bgcolor="#1C1B1E",
        margin=dict(l=20,r=20,t=50,b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(title='Price', showgrid=False),
        yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False),
        transition=dict(duration=500)  # smooth transition
    )

    return fig, f"{latest_price:.2f}", str(total_trades_10s)
