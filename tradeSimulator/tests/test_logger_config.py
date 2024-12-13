import logging
from unittest.mock import patch, MagicMock
from tradeSimulator.logger_config import setup_logging
from tradeSimulator.config import Config

@patch("tradeSimulator.config.Config.get_log_level", return_value="DEBUG")
@patch("logging.StreamHandler")
@patch("logging.Formatter")
def test_setup_logging(mock_formatter, mock_stream_handler, mock_get_log_level):
    # Mock the Formatter and StreamHandler to avoid real logging setup
    mock_handler = MagicMock()
    mock_stream_handler.return_value = mock_handler

    # Call the function
    setup_logging()

    # Assert the logger was set to the mocked log level
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

    # Assert StreamHandler was added with the correct formatter
    mock_stream_handler.assert_called_once()
    mock_formatter.assert_called_once_with(
        '%(asctime)s %(levelname)s [%(threadName)s] %(name)s - %(funcName)s:%(lineno)d %(message)s'
    )
    mock_handler.setFormatter.assert_called_once_with(mock_formatter.return_value)
