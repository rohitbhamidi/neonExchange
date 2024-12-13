import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import HTTPError, ConnectionError, Timeout
from typing import Any, Dict, List, Optional
from utils import RateLimiter

logger = logging.getLogger(__name__)

class PolygonAPIClient:
    def __init__(self, api_key: str, rate_limiter: RateLimiter):
        self.api_key = api_key
        self.base_url = 'https://api.polygon.io'
        self.rate_limiter = rate_limiter

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((HTTPError, ConnectionError, Timeout))
    )
    def get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        with self.rate_limiter():
            url = f"{self.base_url}{endpoint}"
            params['apiKey'] = self.api_key
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()


    def get_ticker_events(self, ticker: str) -> Optional[Dict[str, Any]]:
        endpoint = f"/vX/reference/tickers/{ticker}/events"
        params = {}
        try:
            data = self.get(endpoint, params)
            if data.get('status') == 'OK':
                return data
            else:
                logger.error(f"Failed to fetch ticker events for {ticker}: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching ticker events for {ticker}: {e}")
            return None

    def get_ticker_news(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        endpoint = "/v2/reference/news"
        params = {'limit': limit}
        try:
            data = self.get(endpoint, params)
            if data.get('status') == 'OK':
                return data.get('results', [])
            else:
                logger.error(f"Failed to fetch ticker news: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching ticker news: {e}")
            return None

    def get_ticker_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        endpoint = f"/v3/reference/tickers/{ticker}"
        params = {}
        try:
            data = self.get(endpoint, params)
            if data.get('status') == 'OK':
                return data.get('results', {})
            else:
                logger.error(f"Failed to fetch ticker details for {ticker}: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching ticker details for {ticker}: {e}")
            return None

    def get_related_companies(self, ticker: str) -> Optional[List[str]]:
        endpoint = f"/v1/related-companies/{ticker}"
        params = {}
        try:
            data = self.get(endpoint, params)
            if data.get('status') == 'OK':
                results = data.get('results', [])
                related_tickers = [item['ticker'] for item in results]
                return related_tickers
            else:
                logger.error(f"Failed to fetch related companies for {ticker}: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching related companies for {ticker}: {e}")
            return None

    def get_stock_fundamentals(self, ticker: str, timeframe: str = 'quarterly', limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        endpoint = "/vX/reference/financials"
        params = {
            'ticker': ticker,
            'timeframe': timeframe,
            'include_sources': 'false',
            'order': 'desc',
            'limit': limit,
            'sort': 'filing_date',
        }
        try:
            data = self.get(endpoint, params)
            if data.get('status') == 'OK':
                return data.get('results', [])
            else:
                logger.error(f"Failed to fetch financials for {ticker}: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return None
