# import json
# from unittest.mock import MagicMock, patch
# from tradeSimulator.kafka_producer import KafkaProducerClient
# from tradeSimulator.config import Config
# from tenacity import RetryError
# import pytest

# @patch('confluent_kafka.Producer')
# def test_send_trade_success(mock_producer_class):
#     mock_producer = MagicMock()
#     mock_producer_class.return_value = mock_producer

#     # Updated to use methods from Config for broker and topic
#     kp = KafkaProducerClient(broker=Config.get_kafka_broker(), topic=Config.get_kafka_topic())
#     trade = {"ticker": "AAPL", "price": 150.0}
#     kp.send_trade(trade)

#     mock_producer.produce.assert_called_once()
#     args, kwargs = mock_producer.produce.call_args
#     assert args[0] == Config.get_kafka_topic()  # Topic should match the one retrieved from Config
#     assert json.loads(kwargs['value']) == trade

#     kp.flush()
#     mock_producer.flush.assert_called_once()

# @patch('confluent_kafka.Producer')
# def test_send_trade_error(mock_producer_class):
#     mock_producer = MagicMock()
#     mock_producer_class.return_value = mock_producer

#     def raise_exception(*args, **kwargs):
#         raise Exception("Kafka send error")

#     mock_producer.produce.side_effect = raise_exception

#     # Updated to use methods from Config for broker and topic
#     kp = KafkaProducerClient(broker=Config.get_kafka_broker(), topic=Config.get_kafka_topic())
#     trade = {"ticker": "AAPL", "price": 150.0}

#     # The retry logic should raise after attempts
#     with pytest.raises(RetryError):
#         kp.send_trade(trade)
