import pandas as pd
from dash import html, dcc, Input, Output, callback
import plotly.express as px
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config
import dash_bootstrap_components as dbc
import logging
import io
from dash.dependencies import State

db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def layout():
    return html.Div(
        className="page-content",
        children=[
            html.H1("Analytics", style={"color":"#FFFFFF","fontSize":"24px","marginBottom":"20px"}),
            html.Div(
                className="filter-section",
                children=[
                    html.Label("Tickers:", style={"color":"#E0E0E0"}),
                    dcc.Input(id='analytics-ticker-input', type='text', value='AAPL', className='filter-input', placeholder='e.g. AAPL, MSFT'),
                    html.Button("Update", id='analytics-update-button', className='download-btn', n_clicks=0),
                    html.Button("Download CSV", id="analytics-download-button", className='download-btn', style={"marginLeft":"10px"})
                ]
            ),
            # Average Trade Volume
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Average Trade Volume per Ticker", style={"marginBottom":"10px","color":"#FFFFFF","fontSize":"18px"}),
                    dcc.Graph(id='analytics-avg-volume-chart', style={"height":"300px"})
                ]
            ),
            # Most Traded Tickers
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Most Traded Tickers", style={"marginBottom":"10px","color":"#FFFFFF","fontSize":"18px"}),
                    dcc.Graph(id='analytics-most-traded-chart', style={"height":"300px"})
                ]
            ),
            # Price Trend
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Price Trend for Selected Tickers", style={"marginBottom":"10px","color":"#FFFFFF","fontSize":"18px"}),
                    dcc.Graph(id='analytics-price-trend-chart', style={"height":"300px"})
                ]
            ),
            # Latest Ticker Events
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Latest Ticker Events", style={"marginBottom":"10px","color":"#FFFFFF","fontSize":"18px"}),
                    html.Div(id='analytics-latest-events', style={"maxHeight":"200px","overflowY":"auto"})
                ]
            ),
            # Trade Distribution by Exchange
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Trade Distribution by Exchange", style={"marginBottom":"10px","color":"#FFFFFF","fontSize":"18px"}),
                    dcc.Graph(id='analytics-exchange-distribution-chart', style={"height":"300px"})
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
    ticker_value = ticker_value.strip().upper() if ticker_value else "AAPL"
    tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]

    logger.info(f"Fetching analytics data for {tickers}")
    agg_data = db_handler.fetch_aggregated_data(tickers)
    df_agg = pd.DataFrame(agg_data, columns=["ticker","avg_size","trade_count"]) if agg_data else pd.DataFrame({"ticker":[],"avg_size":[],"trade_count":[]})

    # Average Trade Volume Chart
    if df_agg.empty:
        fig_avg_vol = px.bar(title="No Data")
    else:
        fig_avg_vol = px.bar(df_agg, x="ticker", y="avg_size", title="Average Trade Volume")
        fig_avg_vol.update_traces(marker_color="#7A45D1")

    fig_avg_vol.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E")

    # Most Traded Tickers
    df_order = df_agg.sort_values(by="trade_count", ascending=False)
    if df_order.empty:
        fig_most_traded = px.bar(title="No Data")
    else:
        fig_most_traded = px.bar(df_order, x="ticker", y="trade_count", title="Most Traded Tickers")
        fig_most_traded.update_traces(marker_color="#A980FF")
    fig_most_traded.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E")

    # Price Trend
    price_data = db_handler.fetch_live_trades(tickers, limit=500)
    df_price = pd.DataFrame(price_data, columns=["localTS","ticker","price","size","exchange"]) if price_data else pd.DataFrame()
    if df_price.empty:
        fig_price_trend = px.line(title="No Price Data")
    else:
        df_price.sort_values("localTS", inplace=True)
        fig_price_trend = px.line(df_price, x="localTS", y="price", color="ticker", title="Price Trend")
    fig_price_trend.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E")

    # Latest Events
    events_data = db_handler.fetch_latest_events(tickers, limit=20)
    df_events = pd.DataFrame(events_data, columns=["ticker","event_date","event_type","name"]) if events_data else pd.DataFrame()
    if df_events.empty:
        events_content = html.Div("No recent events found.", style={"color":"red"})
    else:
        table_rows = []
        for _, row in df_events.iterrows():
            table_rows.append(html.Tr([
                html.Td(row['ticker']),
                html.Td(str(row['event_date'])),
                html.Td(row['event_type']),
                html.Td(row['name'])
            ]))
        events_content = html.Table(
            className="data-table",
            children=[
                html.Thead(html.Tr([html.Th("Ticker"), html.Th("Event Date"), html.Th("Event Type"), html.Th("Name")])),
                html.Tbody(table_rows)
            ]
        )

    # Exchange Distribution
    exchange_data = db_handler.fetch_exchange_distribution(tickers)
    df_exchange = pd.DataFrame(exchange_data, columns=["ticker","exchange","count_ex"]) if exchange_data else pd.DataFrame()
    if df_exchange.empty:
        fig_exchange_dist = px.bar(title="No Data")
    else:
        fig_exchange_dist = px.bar(df_exchange, x="ticker", y="count_ex", color="exchange", barmode="stack", title="Trade Distribution by Exchange")
    fig_exchange_dist.update_layout(template="plotly_dark",paper_bgcolor="#1C1B1E",plot_bgcolor="#1C1B1E")

    return fig_avg_vol, fig_most_traded, fig_price_trend, events_content, fig_exchange_dist

@callback(
    Output("analytics-download-data", "data"),
    Input("analytics-download-button", "n_clicks"),
    State("analytics-ticker-input", "value"),
    prevent_initial_call=True
)
def download_analytics(n_clicks, ticker_value):
    ticker_value = ticker_value.strip().upper() if ticker_value else "AAPL"
    tickers = [t.strip().upper() for t in ticker_value.split(",") if t.strip()]
    data = db_handler.fetch_aggregated_data(tickers)
    df = pd.DataFrame(data, columns=["ticker","avg_size","trade_count"]) if data else pd.DataFrame({"ticker":[],"avg_size":[],"trade_count":[]})

    return dcc.send_data_frame(df.to_csv, "analytics_data.csv")
