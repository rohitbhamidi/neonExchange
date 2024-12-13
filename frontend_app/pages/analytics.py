import pandas as pd
from dash import html, dcc, Input, Output, callback
import plotly.express as px
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config
import dash_bootstrap_components as dbc
import io
import base64

db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)

def layout():
    """
    Layout for the Analytics page.
    """
    return html.Div(
        children=[
            html.H2("Analytics Dashboard", style={"marginBottom": "20px"}),
            html.Div(
                children=[
                    html.Label("Filter by Ticker(s):", style={"display": "block"}),
                    dcc.Input(id='analytics-ticker-input', type='text', placeholder='e.g. AAPL,MSFT', style={"width": "300px", "marginRight": "10px"}),
                    dbc.Button("Update", id='analytics-update-button', color="primary"),
                    html.Br(), html.Br(),
                    dbc.Button("Download Analytics CSV", id="analytics-download-button", color="secondary")
                ],
                style={"marginBottom": "20px"}
            ),

            html.Div(
                children=[
                    html.H4("Average Trade Volume (Size) per Ticker", style={"marginBottom": "10px"}),
                    dcc.Graph(id='analytics-avg-volume-chart', style={"marginBottom": "30px"})
                ]
            ),

            html.Div(
                children=[
                    html.H4("Ordered Most Traded Tickers", style={"marginBottom": "10px"}),
                    dcc.Graph(id='analytics-most-traded-chart', style={"marginBottom": "30px"})
                ]
            ),

            html.Div(
                children=[
                    html.H4("Price Trend for Selected Tickers", style={"marginBottom": "10px"}),
                    dcc.Graph(id='analytics-price-trend-chart', style={"marginBottom": "30px"})
                ]
            ),

            html.Div(
                children=[
                    html.H4("Latest Ticker Events", style={"marginBottom": "10px"}),
                    html.Div(id='analytics-latest-events', style={"marginBottom": "30px"})
                ]
            ),

            html.Div(
                children=[
                    html.H4("Trade Distribution by Exchange", style={"marginBottom": "10px"}),
                    dcc.Graph(id='analytics-exchange-distribution-chart', style={"marginBottom": "30px"})
                ]
            ),
            dcc.Download(id="analytics-download-data")
        ]
    )

@callback(
    Output('analytics-avg-volume-chart', 'figure'),
    Output('analytics-most-traded-chart', 'figure'),
    Output('analytics-price-trend-chart', 'figure'),
    Output('analytics-latest-events', 'children'),
    Output('analytics-exchange-distribution-chart', 'figure'),
    Input('analytics-update-button', 'n_clicks'),
    Input('analytics-ticker-input', 'value')
)
def update_analytics(n_clicks, ticker_value):
    if ticker_value:
        tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]
    else:
        tickers = ["AAPL"]

    agg_data = db_handler.fetch_aggregated_data(tickers)
    df_agg = pd.DataFrame(agg_data, columns=["ticker", "avg_size", "trade_count"])
    if df_agg.empty:
        df_agg = pd.DataFrame({"ticker": [], "avg_size": [], "trade_count": []})

    fig_avg_vol = px.bar(df_agg, x="ticker", y="avg_size", title="Average Trade Volume per Ticker")
    fig_avg_vol.update_layout(template="plotly_dark", paper_bgcolor="#121212", plot_bgcolor="#121212")

    df_order = df_agg.sort_values(by="trade_count", ascending=False)
    fig_most_traded = px.bar(df_order, x="ticker", y="trade_count", title="Most Traded Tickers")
    fig_most_traded.update_layout(template="plotly_dark", paper_bgcolor="#121212", plot_bgcolor="#121212")

    price_data = db_handler.fetch_live_trades(tickers, limit=500)
    df_price = pd.DataFrame(price_data, columns=["localTS", "ticker", "price", "size", "exchange"])
    df_price.sort_values(by="localTS", inplace=True)
    if df_price.empty:
        fig_price_trend = px.line(title="No Price Data")
        fig_price_trend.update_layout(template="plotly_dark", paper_bgcolor="#121212", plot_bgcolor="#121212")
    else:
        fig_price_trend = px.line(df_price, x="localTS", y="price", color="ticker", title="Price Trend")
        fig_price_trend.update_layout(template="plotly_dark", paper_bgcolor="#121212", plot_bgcolor="#121212")

    events_data = db_handler.fetch_latest_events(tickers, limit=20)
    df_events = pd.DataFrame(events_data, columns=["ticker", "event_date", "event_type", "name"])
    if df_events.empty:
        events_content = html.Div("No recent events found.", style={"color": "red"})
    else:
        events_rows = []
        for _, row in df_events.iterrows():
            events_rows.append(html.Div(f"{row['event_date']}: {row['ticker']} - {row['event_type']} ({row['name']})", style={"marginBottom": "5px"}))
        events_content = html.Div(events_rows)

    exchange_data = db_handler.fetch_exchange_distribution(tickers)
    df_exchange = pd.DataFrame(exchange_data, columns=["ticker", "exchange", "count_ex"])
    if df_exchange.empty:
        fig_exchange_dist = px.bar(title="No Data for Exchange Distribution")
    else:
        fig_exchange_dist = px.bar(df_exchange, x="ticker", y="count_ex", color="exchange", barmode='stack', title="Trade Distribution by Exchange")
    fig_exchange_dist.update_layout(template="plotly_dark", paper_bgcolor="#121212", plot_bgcolor="#121212")

    return fig_avg_vol, fig_most_traded, fig_price_trend, events_content, fig_exchange_dist

@callback(
    Output("analytics-download-data", "data"),
    Input("analytics-download-button", "n_clicks"),
    Input("analytics-ticker-input", "value"),
    prevent_initial_call=True
)
def download_analytics(n_clicks, ticker_value):
    if ticker_value:
        tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]
    else:
        tickers = ["AAPL"]

    agg_data = db_handler.fetch_aggregated_data(tickers)
    df = pd.DataFrame(agg_data, columns=["ticker", "avg_size", "trade_count"])
    if df.empty:
        df = pd.DataFrame({"ticker":[], "avg_size":[], "trade_count":[]})

    return dcc.send_data_frame(df.to_csv, "analytics_data.csv")
