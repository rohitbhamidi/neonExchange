import singlestoredb as s2
import logging
from typing import List, Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from singlestoredb import DatabaseError
from tradeSimulator.config import Config

logger = logging.getLogger(__name__)

class DBHandler:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = s2.connect(self.db_url)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(DatabaseError)
    )
    def insert_trades(self, trades: List[Dict[str, Any]]):
        """
        Insert trades into the database using a parameterized batch insert.
        """
        if not trades:
            return

        # Construct insert query
        # trades table schema fields: conditions, correction, exchange, id, participant_timestamp,
        # price, sequence_number, sip_timestamp, size, tape, trf_id, trf_timestamp, ticker
        insert_query = """
        INSERT INTO live_trades
        (ticker, conditions, correction, exchange, id, participant_timestamp, price,
         sequence_number, sip_timestamp, size, tape, trf_id, trf_timestamp)
        VALUES (%(ticker)s, %(conditions)s, %(correction)s, %(exchange)s, %(id)s,
                %(participant_timestamp)s, %(price)s, %(sequence_number)s, %(sip_timestamp)s,
                %(size)s, %(tape)s, %(trf_id)s, %(trf_timestamp)s)
        """

        # Execute in batches
        conn = s2.connect(self.db_url)
        cur = conn.cursor()
        try:
            cur.executemany(insert_query, trades)
            conn.commit()
            logger.debug(f"Inserted {len(trades)} trades into the database.")
        except DatabaseError as e:
            logger.error(f"Database error inserting trades: {e}")
            raise
        finally:
            cur.close()
            conn.close()
