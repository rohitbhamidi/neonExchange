import logging
from typing import List, Dict, Any
from tradeSimulator.config import Config
from tradeSimulator.db_handler import DBHandler
from tradeSimulator.kafka_producer import KafkaProducerClient
import json

logger = logging.getLogger(__name__)

class ProducerInterface:
    def produce_batch(self, trades: List[Dict[str, Any]]):
        raise NotImplementedError("Must be implemented by subclass.")

    def close(self):
        pass


class DBProducer(ProducerInterface):
    def __init__(self, db_url: str):
        self.db = DBHandler(db_url)

    def produce_batch(self, trades: List[Dict[str, Any]]):
        self.db.insert_trades(trades)


class KafkaProducerAdapter(ProducerInterface):
    def __init__(self, broker: str, topic: str):
        self.kp = KafkaProducerClient(broker, topic)

    def produce_batch(self, trades: List[Dict[str, Any]]):
        for trade in trades:
            self.kp.send_trade(trade)

    def close(self):
        self.kp.flush()


def get_producer(mode: str) -> ProducerInterface:
    if mode == "db":
        return DBProducer(Config.get_singlestore_db_url())
    elif mode == "kafka":
        return KafkaProducerAdapter(Config.get_kafka_broker(), Config.get_kafka_topic())
    else:
        raise ValueError(f"Unsupported mode: {mode}")
