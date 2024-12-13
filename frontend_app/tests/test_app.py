import unittest
from unittest.mock import patch
from frontend_app.db_handler import SingleStoreDBHandler
from frontend_app.config import Config

class TestApp(unittest.TestCase):
    def setUp(self):
        self.db_handler = SingleStoreDBHandler(Config.SINGLESTORE_DB_URL)

    @patch.object(SingleStoreDBHandler, 'fetch_live_trades', return_value=[])
    def test_no_data_for_realtime(self, mock_fetch):
        trades = self.db_handler.fetch_live_trades(['FAKE'])
        self.assertEqual(trades, [])

    @patch.object(SingleStoreDBHandler, 'fetch_aggregated_data', return_value=[])
    def test_no_data_for_analytics(self, mock_fetch):
        data = self.db_handler.fetch_aggregated_data(['FAKE'])
        self.assertEqual(data, [])

if __name__ == '__main__':
    unittest.main()
