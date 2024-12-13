import logging
from confluent_kafka import Producer
from typing import Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, retry_if_result

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    def __init__(self, broker: str, topic: str):
        self.topic = topic
        self.producer = Producer({'bootstrap.servers': broker})

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(Exception)
    )
    def send_trade(self, trade: Dict[str, Any]):
        """
        Send a single trade to Kafka.
        """
        # Convert trade to a JSON string
        import json
        payload = json.dumps(trade)
        self.producer.produce(self.topic, value=payload, callback=self.delivery_report)
        self.producer.poll(0)

    def flush(self):
        self.producer.flush()
