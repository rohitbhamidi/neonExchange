import pytest
from unittest.mock import patch, MagicMock
from singlestoredb import DatabaseError
from tradeSimulator.db_handler import DBHandler

@patch('singlestoredb.connect')
def test_insert_trades_success(mock_connect):
    # Mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate successful insert
    trades = [{
        "ticker": "AAPL",
        "conditions": "test",
        "correction": 0,
        "exchange": 1,
        "id": 12345,
        "participant_timestamp": 1640995200000000000,
        "price": 150.0,
        "sequence_number": 1,
        "sip_timestamp": 1640995200000000000,
        "size": 100,
        "tape": 1,
        "trf_id": 0,
        "trf_timestamp": 1640995200000000000
    }]
    db_handler = DBHandler("mock_db_url")
    db_handler.insert_trades(trades)

    # Assert that `executemany` was called with the correct arguments
    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()

@patch('singlestoredb.connect')
def test_insert_trades_db_error(mock_connect):
    # Mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Raise DatabaseError for the first 3 attempts, then succeed
    def side_effect(*args, **kwargs):
        nonlocal attempts
        if attempts < 3:
            attempts += 1
            raise DatabaseError("Mock DB error")
        return None

    attempts = 0
    mock_cursor.executemany.side_effect = side_effect

    trades = [{
        "ticker": "AAPL",
        "conditions": "test",
        "correction": 0,
        "exchange": 1,
        "id": 12345,
        "participant_timestamp": 1640995200000000000,
        "price": 150.0,
        "sequence_number": 1,
        "sip_timestamp": 1640995200000000000,
        "size": 100,
        "tape": 1,
        "trf_id": 0,
        "trf_timestamp": 1640995200000000000
    }]

    db_handler = DBHandler("mock_db_url")

    # Test with retries
    db_handler.insert_trades(trades)

    # Ensure `executemany` was called multiple times (retries occurred)
    assert mock_cursor.executemany.call_count == 4  # 3 failures + 1 success
    mock_conn.commit.assert_called_once()
