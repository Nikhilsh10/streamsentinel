import os
import sys
import json
import time
import logging
import random
from kafka import KafkaProducer
from kafka.errors import KafkaError

from generator import generate_random_event

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", 20))
ANOMALY_RATE = float(os.getenv("ANOMALY_RATE", 0.05))

def create_producer():
    retries = 5
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8'),
                api_version=(2, 5, 0)
            )
            logger.info("Successfully connected to Kafka")
            return producer
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka, retrying... ({e})")
            retries -= 1
            time.sleep(5)
    
    logger.error("Could not connect to Kafka after multiple retries. Exiting.")
    sys.exit(1)

def main():
    logger.info(f"Starting producer: {EVENTS_PER_SECOND} events/sec, connecting to {KAFKA_BOOTSTRAP}")
    producer = create_producer()
    
    base_sleep = 1.0 / EVENTS_PER_SECOND
    
    try:
        while True:
            event = generate_random_event(anomaly_rate=ANOMALY_RATE)
            topic = f"{event['stream']}-events"
            
            # Key ensures partition affinity
            key = event.get('device_id') or event.get('user_id')
            
            producer.send(
                topic,
                key=key,
                value=event,
                headers=[("schema_version", b"1.0"), ("producer_id", b"synthetic-gen")]
            )
            
            # Add ±10% random jitter to sleep time
            jitter = random.uniform(-0.1 * base_sleep, 0.1 * base_sleep)
            time.sleep(max(0, base_sleep + jitter))
            
    except KeyboardInterrupt:
        logger.info("Stopping producer...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()
