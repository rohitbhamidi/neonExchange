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
                    # Default ticker is AAPL as requested
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

    # Revert to limit=300 as before to prevent "Insufficient Data" issues caused by overly large windows.
    data = db_handler.fetch_live_trades([ticker_value], limit=300)
    if not data:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E",title="No Data Available")
        return fig, "N/A", "0"

    df = pd.DataFrame(data, columns=["localTS","ticker","price","size","exchange"])
    # Convert localTS to datetime
    df['localTS'] = pd.to_datetime(df['localTS'])
    df.sort_values(by="localTS", inplace=True)
    df['price'] = df['price'].astype(float)
    df['RSI'] = compute_rsi(df['price'])

    # If there's not enough variation in time or only one data point:
    if df['localTS'].nunique() < 2:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E",title="Insufficient Data")
        latest_price = df['price'].iloc[-1] if not df.empty else "N/A"
        total_trades_10s = 0
        return fig, f"{latest_price:.2f}" if latest_price != "N/A" else "N/A", str(total_trades_10s)

    latest_price = df['price'].iloc[-1]
    latest_time = df["localTS"].max()
    window_start = latest_time - pd.Timedelta(seconds=10)
    recent_trades = df[df["localTS"] >= window_start]
    total_trades_10s = len(recent_trades)

    # Create line chart with RSI
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["localTS"],
            y=df["price"],
            mode='lines',
            line=dict(color='#A980FF', width=2, shape='linear'),
            name='Price'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["localTS"],
            y=df["RSI"],
            mode='lines',
            line=dict(color='#7A45D1', width=2, dash='dot', shape='linear'),
            name='RSI',
            yaxis='y2'
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C1B1E",
        plot_bgcolor="#1C1B1E",
        margin=dict(l=20,r=20,t=50,b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(title='Price', showgrid=False),
        yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False),
        transition=dict(duration=500)
    )

    return fig, f"{latest_price:.2f}", str(total_trades_10s)
