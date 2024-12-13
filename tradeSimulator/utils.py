import logging
import time
import threading
import boto3
from botocore.config import Config as BotoConfig
from tradeSimulator.config import Config
from typing import Generator
import math
import pandas as pd
import singlestoredb as s2

logger = logging.getLogger(__name__)

def get_data_from_s2db(file_path: str) -> None:
    """
    Load the data from SingleStore and save it as a CSV file.
    """
    try:
        # Establish a connection to SingleStore
        db_url = Config.get_singlestore_db_url()
        conn = s2.connect(db_url)
        
        # Load data from SingleStore
        df = pd.read_sql_query(
            "SELECT * FROM trades LIMIT 5000",
            conn
        )
        
        # Save data to CSV file
        df.to_csv(file_path, index=False)
        
        logger.info(f"Loaded data from SingleStore and saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to load data from SingleStore: {e}")
        raise

class RateLimiter:
    def __init__(self, rate_per_second: int):
        self.rate_per_second = rate_per_second
        self.interval = 1.0 / rate_per_second
        self.next_execution_time = time.monotonic()

    def __enter__(self):
        current_time = time.monotonic()
        if current_time < self.next_execution_time:
            time.sleep(self.next_execution_time - current_time)
        self.next_execution_time += self.interval  # Increment the next execution time

    def __exit__(self, exc_type, exc_value, traceback):
        pass

