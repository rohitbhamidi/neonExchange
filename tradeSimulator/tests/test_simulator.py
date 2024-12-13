import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from tradeSimulator.simulator import load_data, simulate_trades
from tradeSimulator.config import Config

def setup_module(module):
    # Cleanup the local CSV if it exists
    local_csv_path = Config.get_local_csv_path()
    if os.path.exists(local_csv_path):
        os.remove(local_csv_path)

# @patch('pandas.read_csv')
# @patch('tradeSimulator.utils.download_file_from_s3')  # Ensure the correct path to `download_file_from_s3` is mocked
# def test_load_data_fallback(mock_download, mock_read_csv):
#     # Simulate FileNotFoundError on the first read_csv call, and successful DataFrame return on the second
#     mock_read_csv.side_effect = [FileNotFoundError, pd.DataFrame({"ticker": ["AAPL"]})]

#     # Call the load_data function
#     df = load_data()

#     # Assert that the DataFrame is not empty after the second call
#     assert not df.empty, "DataFrame should not be empty after fallback logic."

#     # Ensure download_file_from_s3 was called once
#     mock_download.assert_called_once()

#     # Ensure read_csv was called twice
#     assert mock_read_csv.call_count == 2, "read_csv should have been called twice: once to fail, once to load data."


def test_load_data_local():
    # Create a dummy local CSV
    local_csv_path = Config.get_local_csv_path()
    df = pd.DataFrame({
        "ticker": ["AAPL"],
        "conditions": ["normal"],
        "correction": [0],
        "exchange": [1],
        "id": [123],
        "participant_timestamp": [1640995200000000000],
        "price": [150.0],
        "sequence_number": [1],
        "sip_timestamp": [1640995200000000000],
        "size": [100],
        "tape": [1],
        "trf_id": [0],
        "trf_timestamp": [1640995200000000000]
    })
    df.to_csv(local_csv_path, index=False)
    result = load_data()
    assert not result.empty
    assert "ticker" in result.columns

@patch('tradeSimulator.simulator.get_producer')
@patch('tradeSimulator.simulator.load_data')
def test_simulate_trades(mock_load_data, mock_get_producer):
    df = pd.DataFrame({
        "ticker": ["AAPL"] * 10,
        "conditions": ["normal"] * 10,
        "correction": [0] * 10,
        "exchange": [1] * 10,
        "id": range(10),
        "participant_timestamp": [1640995200000000000] * 10,
        "price": [150.0] * 10,
        "sequence_number": [1] * 10,
        "sip_timestamp": [1640995200000000000] * 10,
        "size": [100] * 10,
        "tape": [1] * 10,
        "trf_id": [0] * 10,
        "trf_timestamp": [1640995200000000000] * 10
    })
    mock_load_data.return_value = df

    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    # Run simulation for a short time and then stop
    # We'll simulate pressing Ctrl+C by raising KeyboardInterrupt
    with patch('time.sleep', side_effect=KeyboardInterrupt("Stop simulation")):
        try:
            simulate_trades(
                throughput=Config.get_throughput(),
                mode=Config.get_mode(),
                batch_size=Config.get_batch_size(),
                num_threads=Config.get_num_threads()
            )
        except KeyboardInterrupt:
            pass

    assert mock_producer.produce_batch.called
