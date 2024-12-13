import os
from unittest.mock import patch
from tradeSimulator.config import Config
from importlib import reload

def test_config_defaults():
    # Test that defaults are loaded if env vars not set
    assert Config.get_log_level() == "INFO"
    assert Config.get_throughput() == 1000
    assert Config.get_mode() == "db"
    assert Config.get_num_threads() == 8
    assert Config.get_batch_size() == 1000


@patch.dict(os.environ, {"MODE": "kafka", "THROUGHPUT": "50000"})
def test_config_overridden():
    # With environment variables
    assert Config.get_mode() == "kafka"
    assert Config.get_throughput() == 50000
