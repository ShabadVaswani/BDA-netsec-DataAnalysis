import json
from typing import Any, Dict, Iterable, Optional

from confluent_kafka import Producer


class KafkaEventWriter:
    def __init__(self, brokers: Iterable[str], client_id: str) -> None:
        self.producer = Producer(
            {
                "bootstrap.servers": ",".join(brokers),
                "client.id": client_id,
            }
        )

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        key: Optional[str] = None,
    ) -> None:
        self.producer.produce(
            topic=topic,
            key=key,
            value=json.dumps(payload, default=str),
        )

    def flush(self) -> None:
        self.producer.flush()
