import json
import logging
from typing import Dict, Any, Callable
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import threading
import time

logger = logging.getLogger(__name__)

class KafkaEventClient:
    def __init__(self, bootstrap_servers: str = "kafka:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        self._setup_producer()
    
    def _setup_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def publish_event(self, topic: str, event_data: Dict[str, Any], key: str = "None"):
        """Publish an event to a Kafka topic"""
        if self.producer is None:
            logger.error("Kafka producer is not initialized. Cannot publish event.")
            return False
        try:
            future = self.producer.send(topic, value=event_data, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(f"Event published to {topic} at partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
    
    def subscribe_to_topic(self, topic: str, group_id: str, message_handler: Callable):
        """Subscribe to a Kafka topic and handle messages"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            self.consumers[topic] = consumer
            
            def consume_messages():
                try:
                    for message in consumer:
                        logger.info(f"Received message from {topic}: {message.value}")
                        message_handler(message.value)
                except Exception as e:
                    logger.error(f"Error consuming messages from {topic}: {e}")
                finally:
                    consumer.close()
            
            # Start consumer in a separate thread
            thread = threading.Thread(target=consume_messages, daemon=True)
            thread.start()
            logger.info(f"Started consuming from topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise
    
    def close(self):
        """Close all Kafka connections"""
        if self.producer:
            self.producer.close()
        
        for consumer in self.consumers.values():
            consumer.close()
        
        logger.info("Kafka connections closed")

# Event topics
TOPICS = {
    "TRADE_BOOKED": "trade.booked",
    "TRADE_VALIDATED": "trade.validated",
    "TRADE_VALIDATION_FAILED": "trade.validation.failed",
    "TRADE_ENRICHED": "trade.enriched",
    "TRADE_ENRICHMENT_FAILED": "trade.enrichment.failed",
    "RISK_CHECK_COMPLETED": "risk.check.completed",
    "RISK_CHECK_FAILED": "risk.check.failed",
    "TRADE_ALLOCATED": "trade.allocated",
    "TRADE_ALLOCATION_FAILED": "trade.allocation.failed",
    "TRADE_STATUS_UPDATED": "trade.status.updated",
    "EXCEPTION_RAISED": "exception.raised",
    "EXCEPTION_RESOLVED": "exception.resolved"
} 