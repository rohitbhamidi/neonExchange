import singlestoredb as s2

class SingleStoreDBHandler:
    """
    Database handler for SingleStore. Provides methods to query the database.
    """
    def __init__(self, db_url: str):
        self.db_url = db_url

    def create_connection(self):
        """
        Creates and returns a new database connection.
        """
        return s2.connect(self.db_url)

    def fetch_live_trades(self, tickers, limit=100):
        """
        Fetch latest live trades for given tickers.
        :param tickers: list of tickers to filter by
        :param limit: maximum number of records to return
        :return: list of tuples representing trade rows
        """
        if not tickers:
            return []

        query = """
            SELECT localTS, ticker, price, size, exchange
            FROM live_trades
            WHERE ticker IN ({})
            ORDER BY localTS DESC
            LIMIT {}
        """.format(",".join(["%s"] * len(tickers)), limit)

        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except Exception:
            # Handle errors gracefully
            return []
        finally:
            conn.close()

    def fetch_aggregated_data(self, tickers):
        """
        Fetch aggregated analytics data for given tickers from the live_trades table.
        Example: average trade volume per ticker over a recent time period.
        """
        if not tickers:
            return []

        # Example aggregation: average size grouped by ticker
        query = """
            SELECT ticker, AVG(size) as avg_size, COUNT(*) as trade_count
            FROM live_trades
            WHERE ticker IN ({})
            GROUP BY ticker
        """.format(",".join(["%s"] * len(tickers)))

        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except Exception:
            return []
        finally:
            conn.close()

    def fetch_exchange_distribution(self, tickers):
        """
        Fetch distribution of trades by exchange for selected tickers.
        Returns grouped count by ticker and exchange.
        """
        if not tickers:
            return []

        query = """
            SELECT ticker, exchange, COUNT(*) as count_ex
            FROM live_trades
            WHERE ticker IN ({})
            GROUP BY ticker, exchange
        """.format(",".join(["%s"] * len(tickers)))

        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except Exception:
            return []
        finally:
            conn.close()

    def fetch_latest_events(self, tickers, limit=20):
        """
        Fetch the latest ticker events for selected tickers.
        """
        if not tickers:
            return []
        query = """
            SELECT ticker, event_date, event_type, name
            FROM ticker_events
            WHERE ticker IN ({})
            ORDER BY event_date DESC
            LIMIT {}
        """.format(",".join(["%s"] * len(tickers)), limit)
        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except Exception:
            return []
        finally:
            conn.close()
