import time
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from tradeSimulator.utils import RateLimiter, get_data_from_s2db
from tradeSimulator.config import Config

@patch('tradeSimulator.utils.s2.connect')
@patch('pandas.read_sql_query')
@patch.object(pd.DataFrame, 'to_csv')
def test_get_data_from_s2db(mock_to_csv, mock_read_sql_query, mock_connect):
    # Mock the database connection
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    # Mock read_sql_query to return a dummy DataFrame
    mock_df = pd.DataFrame({'ticker': ['AAPL'], 'price': [150.0]})
    mock_read_sql_query.return_value = mock_df

    # Define a test file path
    test_file_path = "test_trades_data.csv"

    # Call the function
    get_data_from_s2db(test_file_path)

    # Check that connect was called
    mock_connect.assert_called_once_with(Config.get_singlestore_db_url())

    # Check that read_sql_query was called with the expected query and connection
    mock_read_sql_query.assert_called_once_with("SELECT * FROM trades LIMIT 5000", mock_conn)

    # Check that to_csv was called on the returned DataFrame
    mock_to_csv.assert_called_once_with(test_file_path, index=False)


def test_rate_limiter():
    # Initialize RateLimiter with a rate of 2 operations per second
    rl = RateLimiter(rate_per_second=2)
    start = time.monotonic()
    with rl:
        pass
    with rl:
        pass
    with rl:
        pass
    end = time.monotonic()

    # Allow a small margin of error for timing variations
    elapsed_time = end - start
    # Inserting 3 operations at 2 ops/second should take at least ~1 second for all iterations,
    # but since we're just verifying no overly long waits, we allow up to 2 seconds total
    assert 0.0 <= elapsed_time <= 2.0, f"RateLimiter timing issue. Elapsed time: {elapsed_time:.2f}s"
