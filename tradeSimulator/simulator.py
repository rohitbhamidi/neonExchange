import logging
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from tradeSimulator.config import Config
from tradeSimulator.logger_config import setup_logging
from tradeSimulator.producer import get_producer
from tradeSimulator.utils import get_data_from_s2db, RateLimiter
from tenacity import retry, wait_exponential, stop_after_attempt
import random

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=5)
)
def load_data() -> pd.DataFrame:
    """
    Load the data from the local CSV file.
    If the file doesn't exist, download from S3.
    """
    try:
        df = pd.read_csv(Config.get_local_csv_path())
    except FileNotFoundError:
        logger.info("Downloading CSV from SingleStore...")
        get_data_from_s2db(
            file_path=Config.get_local_csv_path()
        )
        df = pd.read_csv(Config.get_local_csv_path(), compression='gzip')

    # Required columns for the trades schema
    required_cols = [
        "localTS", "localDate", "ticker", "conditions", "correction", "exchange",
        "id", "participant_timestamp", "price", "sequence_number", "sip_timestamp",
        "size", "tape", "trf_id", "trf_timestamp"
    ]

    # Ensure all required columns exist
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0
            logger.warning(f"Column {col} not found in CSV. Created dummy column with default values.")

    # Fill NaN values in 'conditions' with an empty string
    df['conditions'] = df['conditions'].fillna('')
    df['conditions'] = df['conditions'].astype(str)

    return df


def simulate_trades(throughput: int, mode: str, batch_size: int, num_threads: int):
    """
    Simulate real-time trades by randomly sampling rows from the CSV.
    Throughput: trades per second.
    """
    df = load_data()
    producer = get_producer(mode)
    total_trades = 0
    rate_limiter = RateLimiter(throughput)
    last_log_time = time.time()

    def send_batch(batch_trades):
        producer.produce_batch(batch_trades)
        return len(batch_trades)

    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            while True:
                # Sample batch_size random rows
                batch = df.sample(n=batch_size, replace=True)

                # Current time and nanosecond timestamp
                current_dt = datetime.now()
                current_ts_str = current_dt.strftime("%Y-%m-%d %H:%M:%S")
                current_date_str = current_dt.strftime("%Y-%m-%d")
                # Convert current UTC time to nanoseconds since epoch
                current_ts_ns = int(current_dt.timestamp() * 1_000_000_000)

                # Replace timestamp fields with current time
                batch['localTS'] = current_ts_str
                batch['localDate'] = current_date_str
                batch['participant_timestamp'] = current_ts_ns
                batch['sip_timestamp'] = current_ts_ns
                batch['trf_timestamp'] = current_ts_ns

                # Convert batch to dict for sending
                trades_list = batch.to_dict(orient='records')

                # Rate limit to desired throughput
                with rate_limiter:
                    future = executor.submit(send_batch, trades_list)
                    futures.append(future)

                # Log periodically
                now = time.time()
                if now - last_log_time > Config.get_log_interval():
                    logger.info(f"Sent {total_trades} trades so far at ~{throughput} tps.")
                    last_log_time = now

                # Process completed futures
                done_futures = [f for f in futures if f.done()]
                for f in done_futures:
                    res = f.result()
                    total_trades += res
                    futures.remove(f)
    except KeyboardInterrupt:
        logger.info("Stopping simulation due to keyboard interrupt.")
    finally:
        producer.close()
        logger.info(f"Simulation ended. Total trades sent: {total_trades}")


def main():
    setup_logging()
    logger.info("Starting trade simulation...")
    simulate_trades(
        throughput=Config.get_throughput(),
        mode=Config.get_mode(),
        batch_size=Config.get_batch_size(),
        num_threads=Config.get_num_threads()
    )
    logger.info("Trade simulation completed.")


if __name__ == '__main__':
    main()
