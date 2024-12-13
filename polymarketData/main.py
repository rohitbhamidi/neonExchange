import logging
import threading
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config
from api_client import PolygonAPIClient
from db_handler import SingleStoreDBHandler
from models import TickerEvent, TickerNews, TickerDetail, RelatedCompany, StockFundamental
from utils import RateLimiter

def setup_logging():
    log_filename = datetime.datetime.now().strftime("app_%Y%m%d_%H%M%S.txt")
    logging.basicConfig(level=Config.LOG_LEVEL,
                        format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s',
                        handlers=[
                            logging.FileHandler(log_filename),
                            logging.StreamHandler()
                        ])

def process_ticker(ticker: str, api_client: PolygonAPIClient, db_handler: SingleStoreDBHandler):
    logger = logging.getLogger(__name__)
    logger.info(f"Processing ticker: {ticker}")

    # Fetch ticker events
    events_data = api_client.get_ticker_events(ticker)
    if events_data:
        events = []
        name = events_data.get('results', {}).get('name', '')
        for event in events_data.get('results', {}).get('events', []):
            ticker_event = TickerEvent(
                ticker=event.get('ticker_change', {}).get('ticker', ticker),
                event_date=event.get('date'),
                event_type=event.get('type'),
                event_data=event,
                name=name
            )
            events.append(ticker_event)
        db_handler.insert_ticker_events(events)

    # Fetch ticker details
    details_data = api_client.get_ticker_details(ticker)
    if details_data:
        ticker_detail = TickerDetail(
            ticker=details_data.get('ticker'),
            name=details_data.get('name'),
            market=details_data.get('market'),
            locale=details_data.get('locale'),
            primary_exchange=details_data.get('primary_exchange'),
            type=details_data.get('type'),
            active=details_data.get('active'),
            currency_name=details_data.get('currency_name'),
            cik=details_data.get('cik'),
            composite_figi=details_data.get('composite_figi'),
            share_class_figi=details_data.get('share_class_figi'),
            market_cap=details_data.get('market_cap'),
            phone_number=details_data.get('phone_number'),
            address=details_data.get('address'),
            description=details_data.get('description'),
            sic_code=details_data.get('sic_code'),
            sic_description=details_data.get('sic_description'),
            ticker_root=details_data.get('ticker_root'),
            homepage_url=details_data.get('homepage_url'),
            total_employees=details_data.get('total_employees'),
            list_date=details_data.get('list_date'),
            branding=details_data.get('branding'),
            share_class_shares_outstanding=details_data.get('share_class_shares_outstanding'),
            weighted_shares_outstanding=details_data.get('weighted_shares_outstanding'),
        )
        db_handler.insert_ticker_details(ticker_detail)

    # Fetch related companies
    related_companies_data = api_client.get_related_companies(ticker)
    if related_companies_data:
        related_companies = []
        for related_ticker in related_companies_data:
            rc = RelatedCompany(stock_symbol=ticker, related_ticker=related_ticker)
            related_companies.append(rc)
        db_handler.insert_related_companies(related_companies)

    # Fetch stock fundamentals
    fundamentals_data = api_client.get_stock_fundamentals(ticker)
    if fundamentals_data:
        fundamentals = []
        for record in fundamentals_data:
            fundamental = StockFundamental(
                ticker=ticker,
                company_name=record.get('company_name'),
                cik=record.get('cik'),
                start_date=record.get('start_date'),
                end_date=record.get('end_date'),
                filing_date=record.get('filing_date'),
                fiscal_period=record.get('fiscal_period'),
                fiscal_year=record.get('fiscal_year'),
                source_filing_url=record.get('source_filing_url'),
                financials=record.get('financials'),
            )
            fundamentals.append(fundamental)
        db_handler.insert_stock_fundamentals(fundamentals)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting data ingestion process.")

    rate_limiter = RateLimiter(Config.RATE_LIMIT)
    api_client = PolygonAPIClient(Config.API_KEY, rate_limiter)
    db_handler = SingleStoreDBHandler(Config.DB_URL)

    db_handler.create_tables()
    tickers = db_handler.get_distinct_tickers()

    if not tickers:
        logger.error("No tickers found to process.")
        return

    max_workers = Config.MAX_WORKERS

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for ticker in tickers:
            futures.append(executor.submit(process_ticker, ticker, api_client, db_handler))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Exception occurred: {e}")

    # Fetch and insert ticker news
    news_data = api_client.get_ticker_news(limit=100)
    if news_data:
        news_list = []
        for news_item in news_data:
            news = TickerNews(
                id=news_item.get('id'),
                article_url=news_item.get('article_url'),
                amp_url=news_item.get('amp_url'),
                title=news_item.get('title'),
                author=news_item.get('author'),
                published_utc=news_item.get('published_utc'),
                tickers=news_item.get('tickers', []),
                description=news_item.get('description'),
                keywords=news_item.get('keywords', []),
                image_url=news_item.get('image_url'),
                publisher=news_item.get('publisher', {}),
                related_insights=news_item.get('insights', [])
            )
            news_list.append(news)
        db_handler.insert_ticker_news(news_list)

    logger.info("Data ingestion process completed.")

if __name__ == '__main__':
    main()
