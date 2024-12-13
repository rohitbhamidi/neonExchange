import pytest
from unittest.mock import patch, MagicMock
from tradeSimulator.producer import DBProducer
from tradeSimulator.config import Config

@patch('tradeSimulator.db_handler.DBHandler')
def test_db_producer(mock_db_handler_class):
    # Mock DBHandler
    mock_db_handler = MagicMock()
    mock_db_handler_class.return_value = mock_db_handler

    # Updated trades data with all required fields
    trades = [{
        "ticker": "AAPL",
        "conditions": "normal",
        "correction": 0,
        "exchange": 1,
        "id": 123,
        "participant_timestamp": 1640995200000000000,
        "price": 150.0,
        "sequence_number": 1,
        "sip_timestamp": 1640995200000000000,
        "size": 100,
        "tape": 1,
        "trf_id": 0,
        "trf_timestamp": 1640995200000000000,
    }]

    # Inject the mocked DBHandler into DBProducer
    dbp = DBProducer(Config.get_singlestore_db_url())
    dbp.db = mock_db_handler  # Manually set the mocked DBHandler

    # Call produce_batch
    dbp.produce_batch(trades)

    # Assert that DBHandler.insert_trades was called with the correct trades data
    mock_db_handler.insert_trades.assert_called_once_with(trades)
