import singlestoredb as s2

class SingleStoreDBHandler:
    """
    Database handler for SingleStore. Provides methods to query the database.
    Modified to handle limit=None for full history fetch.
    """
    def __init__(self, db_url: str):
        self.db_url = db_url

    def create_connection(self):
        return s2.connect(self.db_url)

    def fetch_live_trades(self, tickers, limit=200):
        """
        Fetch latest trades for given tickers from live_trades.
        If limit is None, fetch full history (no LIMIT clause).
        """
        if not tickers:
            return []
        placeholders = ",".join(["%s"] * len(tickers))
        if limit is None:
            query = f"""
                SELECT localTS, ticker, price, size, exchange
                FROM live_trades
                WHERE ticker IN ({placeholders})
                ORDER BY localTS
            """
            params = tickers
        else:
            query = f"""
                SELECT localTS, ticker, price, size, exchange
                FROM live_trades
                WHERE ticker IN ({placeholders})
                ORDER BY localTS
                LIMIT {limit}
            """
            params = tickers

        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
            return rows
        except:
            return []
        finally:
            conn.close()

    def fetch_aggregated_data(self, tickers):
        if not tickers:
            return []
        query = f"""
            SELECT ticker, AVG(size) as avg_size, COUNT(*) as trade_count
            FROM live_trades
            WHERE ticker IN ({",".join(["%s"] * len(tickers))})
            GROUP BY ticker
        """
        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except:
            return []
        finally:
            conn.close()

    def fetch_exchange_distribution(self, tickers):
        if not tickers:
            return []
        query = f"""
            SELECT ticker, exchange, COUNT(*) as count_ex
            FROM live_trades
            WHERE ticker IN ({",".join(["%s"] * len(tickers))})
            GROUP BY ticker, exchange
        """
        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except:
            return []
        finally:
            conn.close()

    def fetch_latest_events(self, tickers, limit=20):
        if not tickers:
            return []
        query = f"""
            SELECT ticker, event_date, event_type, name
            FROM ticker_events
            WHERE ticker IN ({",".join(["%s"] * len(tickers))})
            ORDER BY event_date DESC
            LIMIT {limit}
        """
        conn = self.create_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, tickers)
                rows = cur.fetchall()
            return rows
        except:
            return []
        finally:
            conn.close()
