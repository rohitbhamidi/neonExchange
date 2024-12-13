import pandas as pd
import numpy as np
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config
import dash_bootstrap_components as dbc

db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)

def compute_technical_indicators(df):
    """
    Compute Bollinger Bands, MACD, and RSI for the given dataframe.
    df should have columns: localTS, price (sorted by localTS ascending).
    """
    if len(df) < 30:
        # Not enough data to compute indicators
        return df, None, None, None, None, None

    df = df.copy()
    df.set_index('localTS', inplace=True)

    # Bollinger Bands (20-period)
    period_bb = 20
    df['MA20'] = df['price'].rolling(window=period_bb).mean()
    df['STD20'] = df['price'].rolling(window=period_bb).std()
    df['UpperBB'] = df['MA20'] + 2*df['STD20']
    df['LowerBB'] = df['MA20'] - 2*df['STD20']

    # MACD
    # MACD = EMA12 - EMA26
    # Signal = 9 EMA of MACD
    df['EMA12'] = df['price'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['price'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

    # RSI (14-period)
    change = df['price'].diff()
    gain = change.where(change > 0, 0)
    loss = -change.where(change < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100/(1+rs))

    # Convert index back to column
    df.reset_index(inplace=True)

    # Extract arrays
    bb_data = (df['UpperBB'], df['MA20'], df['LowerBB'])
    macd_data = (df['MACD'], df['Signal'], df['MACD_Hist'])
    rsi_data = df['RSI']

    return df, bb_data, macd_data, rsi_data, df['price'], df['ticker']

def generate_realtime_figure(df, bb_data, macd_data, rsi_data):
    """
    Generate a figure with:
    - Top subplot: candlestick + Bollinger Bands
    - Second subplot: MACD
    - Third subplot: RSI
    """
    fig = make_three_subplots()

    # Unpack BB data
    upper_bb, ma20, lower_bb = bb_data
    # Unpack MACD data
    macd_line, signal_line, macd_hist = macd_data

    # Candlestick on top subplot
    fig.add_trace(
        go.Candlestick(
            x=df['localTS'],
            open=df['price'],
            high=df['price']+0.5,  # assuming slight increments for candlestick highs
            low=df['price']-0.5,   # and lows, since we only have price not OHLC
            close=df['price'],
            name='Price',
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=upper_bb,
            line=dict(color='blue', width=1, dash='dot'),
            name='Upper BB'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=ma20,
            line=dict(color='gray', width=1),
            name='MA20'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=lower_bb,
            line=dict(color='blue', width=1, dash='dot'),
            name='Lower BB'
        ),
        row=1, col=1
    )

    # MACD
    fig.add_trace(
        go.Bar(
            x=df['localTS'],
            y=macd_hist,
            name='MACD Hist',
            marker_color='green'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=macd_line,
            line=dict(color='cyan', width=2),
            name='MACD'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=signal_line,
            line=dict(color='orange', width=2),
            name='Signal'
        ),
        row=2, col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(
            x=df['localTS'],
            y=rsi_data,
            line=dict(color='yellow', width=2),
            name='RSI'
        ),
        row=3, col=1
    )

    # Update layout to dark theme
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    # Adjust each subplot's settings
    fig.update_xaxes(showgrid=False, linecolor='gray')
    fig.update_yaxes(showgrid=False, linecolor='gray')

    return fig

def make_three_subplots():
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.5, 0.25, 0.25],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    return fig

def layout():
    """
    Layout for the Real-time Trading page.
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
            html.H4("Latest Key Metrics", style={"marginBottom": "10px"}),
            html.Div(id='realtime-key-metrics', style={"marginBottom": "20px"}),
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
    if ticker_value:
        tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]
    else:
        tickers = ["AAPL"]

    data = db_handler.fetch_live_trades(tickers=tickers, limit=300)
    if not data:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121212",
            plot_bgcolor="#121212",
            title="No Data Available"
        )
        metrics = html.Div("No recent trades found.", style={"color": "red"})
        return fig, metrics

    df = pd.DataFrame(data, columns=["localTS", "ticker", "price", "size", "exchange"])
    df.sort_values(by="localTS", inplace=True)

    # Compute technical indicators
    df_ind, bb_data, macd_data, rsi_data, price_series, ticker_series = compute_technical_indicators(df)

    if bb_data is None:
        # Not enough data for indicators
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121212",
            plot_bgcolor="#121212",
            title="Not enough data for chart"
        )
        metrics = html.Div("Not enough data to compute indicators.", style={"color": "yellow"})
        return fig, metrics

    fig = generate_realtime_figure(df_ind, bb_data, macd_data, rsi_data)

    # Key Metrics: current price (last price) and total trades in last 10 seconds
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

    return fig, metrics
