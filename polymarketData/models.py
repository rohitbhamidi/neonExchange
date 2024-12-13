from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class TickerEvent:
    ticker: str
    event_date: str
    event_type: str
    event_data: Dict[str, Any]
    name: str

@dataclass
class TickerNews:
    id: str
    article_url: str
    amp_url: str
    title: str
    author: str
    published_utc: str
    tickers: List[str]
    description: str
    keywords: List[str]
    image_url: str
    publisher: Dict[str, Any]
    related_insights: List[Dict[str, Any]]

@dataclass
class TickerDetail:
    ticker: str
    name: str
    market: str
    locale: str
    primary_exchange: str
    type: str
    active: bool
    currency_name: str
    cik: str
    composite_figi: str
    share_class_figi: str
    market_cap: int
    phone_number: str
    address: Dict[str, Any]
    description: str
    sic_code: str
    sic_description: str
    ticker_root: str
    homepage_url: str
    total_employees: int
    list_date: str
    branding: Dict[str, Any]
    share_class_shares_outstanding: int
    weighted_shares_outstanding: int

@dataclass
class RelatedCompany:
    stock_symbol: str
    related_ticker: str

@dataclass
class StockFundamental:
    ticker: str
    company_name: str
    cik: str
    start_date: str
    end_date: str
    filing_date: str
    fiscal_period: str
    fiscal_year: str
    source_filing_url: str
    financials: Dict[str, Any]
