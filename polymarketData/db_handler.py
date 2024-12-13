import singlestoredb as s2
import logging
from typing import Any, Dict, List
from models import TickerEvent, TickerNews, TickerDetail, RelatedCompany, StockFundamental
import json

logger = logging.getLogger(__name__)

class SingleStoreDBHandler:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def create_connection(self):
        return s2.connect(self.db_url)

    def create_tables(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            self.create_ticker_events_table(cursor)
            self.create_ticker_news_table(cursor)
            self.create_ticker_details_table(cursor)
            self.create_related_companies_table(cursor)
            self.create_stock_fundamentals_table(cursor)
            conn.commit()
            logger.info("Tables created successfully.")
        except Exception as e:
            logger.error(f"Exception while creating tables: {e}")
        finally:
            conn.close()

    def create_ticker_events_table(self, cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ticker_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(32),
            event_date DATE,
            event_type VARCHAR(100),
            event_data JSON,
            name VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)

    def create_ticker_news_table(self, cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ticker_news (
            id VARCHAR(512) PRIMARY KEY,
            article_url TEXT,
            amp_url TEXT,
            title TEXT,
            author VARCHAR(512),
            published_utc DATETIME,
            tickers JSON,
            description TEXT,
            keywords JSON,
            image_url TEXT,
            publisher JSON,
            related_insights JSON
        );
        """
        cursor.execute(create_table_query)

    def create_ticker_details_table(self, cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ticker_details (
            ticker VARCHAR(32) PRIMARY KEY,
            name VARCHAR(512),
            market VARCHAR(50),
            locale VARCHAR(10),
            primary_exchange VARCHAR(50),
            type VARCHAR(50),
            active BOOLEAN,
            currency_name VARCHAR(50),
            cik VARCHAR(32),
            composite_figi VARCHAR(32),
            share_class_figi VARCHAR(32),
            market_cap BIGINT,
            phone_number VARCHAR(50),
            address JSON,
            description TEXT,
            sic_code VARCHAR(32),
            sic_description VARCHAR(512),
            ticker_root VARCHAR(32),
            homepage_url TEXT,
            total_employees INT,
            list_date DATE,
            branding JSON,
            share_class_shares_outstanding BIGINT,
            weighted_shares_outstanding BIGINT
        );
        """
        cursor.execute(create_table_query)

    def create_related_companies_table(self, cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS related_companies (
            stock_symbol VARCHAR(32),
            related_ticker VARCHAR(32),
            PRIMARY KEY (stock_symbol, related_ticker)
        );
        """
        cursor.execute(create_table_query)

    def create_stock_fundamentals_table(self, cursor):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stock_fundamentals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(32),
            company_name VARCHAR(512),
            cik VARCHAR(32),
            start_date DATE,
            end_date DATE,
            filing_date DATE,
            fiscal_period VARCHAR(10),
            fiscal_year VARCHAR(10),
            source_filing_url TEXT,
            financials JSON
        );
        """
        cursor.execute(create_table_query)

    def get_distinct_tickers(self) -> List[str]:
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT DISTINCT ticker FROM trades;"
            cursor.execute(query)
            tickers = [row[0] for row in cursor.fetchall()]
            logger.info(f"Retrieved {len(tickers)} tickers from trades table.")
            return tickers
        except Exception as e:
            logger.error(f"Exception while retrieving tickers: {e}")
            return []
        finally:
            conn.close()

    def insert_ticker_events(self, events: List[TickerEvent]):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO ticker_events (ticker, event_date, event_type, event_data, name)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            event_type=VALUES(event_type),
            event_data=VALUES(event_data),
            name=VALUES(name)
            """
            for event in events:
                cursor.execute(insert_query, (
                    event.ticker,
                    event.event_date,
                    event.event_type,
                    json.dumps(event.event_data),
                    event.name
                ))
            conn.commit()
            logger.info(f"Inserted {len(events)} ticker events.")
        except Exception as e:
            logger.error(f"Exception while inserting ticker events: {e}")
        finally:
            conn.close()

    def insert_ticker_news(self, news_list: List[TickerNews]):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO ticker_news (id, article_url, amp_url, title, author, published_utc, tickers, description, keywords, image_url, publisher, related_insights)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            article_url=VALUES(article_url),
            amp_url=VALUES(amp_url),
            title=VALUES(title),
            author=VALUES(author),
            published_utc=VALUES(published_utc),
            tickers=VALUES(tickers),
            description=VALUES(description),
            keywords=VALUES(keywords),
            image_url=VALUES(image_url),
            publisher=VALUES(publisher),
            related_insights=VALUES(related_insights)
            """
            for news in news_list:
                cursor.execute(insert_query, (
                    news.id,
                    news.article_url,
                    news.amp_url,
                    news.title,
                    news.author,
                    news.published_utc,
                    json.dumps(news.tickers),
                    news.description,
                    json.dumps(news.keywords),
                    news.image_url,
                    json.dumps(news.publisher),
                    json.dumps(news.related_insights)
                ))
            conn.commit()
            logger.info(f"Inserted {len(news_list)} news articles.")
        except Exception as e:
            logger.error(f"Exception while inserting ticker news: {e}")
        finally:
            conn.close()

    def insert_ticker_details(self, details: TickerDetail):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO ticker_details (ticker, name, market, locale, primary_exchange, type, active, currency_name,
            cik, composite_figi, share_class_figi, market_cap, phone_number, address, description, sic_code, sic_description,
            ticker_root, homepage_url, total_employees, list_date, branding, share_class_shares_outstanding, weighted_shares_outstanding)
            VALUES (%(ticker)s, %(name)s, %(market)s, %(locale)s, %(primary_exchange)s, %(type)s, %(active)s, %(currency_name)s,
            %(cik)s, %(composite_figi)s, %(share_class_figi)s, %(market_cap)s, %(phone_number)s, %(address)s, %(description)s,
            %(sic_code)s, %(sic_description)s, %(ticker_root)s, %(homepage_url)s, %(total_employees)s, %(list_date)s, %(branding)s,
            %(share_class_shares_outstanding)s, %(weighted_shares_outstanding)s)
            ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            market=VALUES(market),
            locale=VALUES(locale),
            primary_exchange=VALUES(primary_exchange),
            type=VALUES(type),
            active=VALUES(active),
            currency_name=VALUES(currency_name),
            cik=VALUES(cik),
            composite_figi=VALUES(composite_figi),
            share_class_figi=VALUES(share_class_figi),
            market_cap=VALUES(market_cap),
            phone_number=VALUES(phone_number),
            address=VALUES(address),
            description=VALUES(description),
            sic_code=VALUES(sic_code),
            sic_description=VALUES(sic_description),
            ticker_root=VALUES(ticker_root),
            homepage_url=VALUES(homepage_url),
            total_employees=VALUES(total_employees),
            list_date=VALUES(list_date),
            branding=VALUES(branding),
            share_class_shares_outstanding=VALUES(share_class_shares_outstanding),
            weighted_shares_outstanding=VALUES(weighted_shares_outstanding)
            """
            data = {
                'ticker': details.ticker,
                'name': details.name,
                'market': details.market,
                'locale': details.locale,
                'primary_exchange': details.primary_exchange,
                'type': details.type,
                'active': details.active,
                'currency_name': details.currency_name,
                'cik': details.cik,
                'composite_figi': details.composite_figi,
                'share_class_figi': details.share_class_figi,
                'market_cap': details.market_cap,
                'phone_number': details.phone_number,
                'address': json.dumps(details.address),
                'description': details.description,
                'sic_code': details.sic_code,
                'sic_description': details.sic_description,
                'ticker_root': details.ticker_root,
                'homepage_url': details.homepage_url,
                'total_employees': details.total_employees,
                'list_date': details.list_date,
                'branding': json.dumps(details.branding),
                'share_class_shares_outstanding': details.share_class_shares_outstanding,
                'weighted_shares_outstanding': details.weighted_shares_outstanding,
            }
            cursor.execute(insert_query, data)
            conn.commit()
            logger.info(f"Inserted ticker details for {details.ticker}.")
        except Exception as e:
            logger.error(f"Exception while inserting ticker details for {details.ticker}: {e}")
        finally:
            conn.close()

    def insert_related_companies(self, related_companies: List[RelatedCompany]):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO related_companies (stock_symbol, related_ticker)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            related_ticker=VALUES(related_ticker)
            """
            for rc in related_companies:
                cursor.execute(insert_query, (rc.stock_symbol, rc.related_ticker))
            conn.commit()
            logger.info(f"Inserted {len(related_companies)} related companies.")
        except Exception as e:
            logger.error(f"Exception while inserting related companies: {e}")
        finally:
            conn.close()

    def insert_stock_fundamentals(self, fundamentals: List[StockFundamental]):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO stock_fundamentals (ticker, company_name, cik, start_date, end_date, filing_date,
            fiscal_period, fiscal_year, source_filing_url, financials)
            VALUES (%(ticker)s, %(company_name)s, %(cik)s, %(start_date)s, %(end_date)s, %(filing_date)s,
            %(fiscal_period)s, %(fiscal_year)s, %(source_filing_url)s, %(financials)s)
            """
            for fundamental in fundamentals:
                data = {
                    'ticker': fundamental.ticker,
                    'company_name': fundamental.company_name,
                    'cik': fundamental.cik,
                    'start_date': fundamental.start_date,
                    'end_date': fundamental.end_date,
                    'filing_date': fundamental.filing_date,
                    'fiscal_period': fundamental.fiscal_period,
                    'fiscal_year': fundamental.fiscal_year,
                    'source_filing_url': fundamental.source_filing_url,
                    'financials': json.dumps(fundamental.financials),
                }
                cursor.execute(insert_query, data)
            conn.commit()
            logger.info(f"Inserted {len(fundamentals)} stock fundamentals for {fundamental.ticker}.")
        except Exception as e:
            logger.error(f"Exception while inserting stock fundamentals: {e}")
        finally:
            conn.close()
