import asyncio
import json
import time
import logging
from aiokafka import AIOKafkaConsumer
from ..config import settings
from ..ml.fusion import score_event
from ..db.database import insert_anomaly

async def kafka_consumer_loop(app_state):
    print(f"Connecting to Kafka at {settings.KAFKA_BOOTSTRAP}")
    
    # Retry loop for Kafka connection
    retries = 5
    consumer = None
    while retries > 0:
        try:
            consumer = AIOKafkaConsumer(
                "sensor-events", "financial-events",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                group_id="anomaly-detectors-v1",
                auto_offset_reset="latest",
                enable_auto_commit=False,
                value_deserializer=lambda v: json.loads(v.decode())
            )
            await consumer.start()
            print("Kafka Consumer started successfully.")
            break
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}. Retrying...")
            retries -= 1
            await asyncio.sleep(5)
            
    if not consumer:
        print("Could not connect to Kafka. Consumer loop aborting.")
        return

    try:
        async for msg in consumer:
            try:
                event_data = msg.value
                
                scored_event = await score_event(app_state, event_data)
                if scored_event is None:
                    await consumer.commit()
                    continue
                    
                await app_state.ws_manager.broadcast(scored_event)
                
                if scored_event.is_anomaly:
                    app_state.anomaly_counter += 1
                    await insert_anomaly(scored_event)
                    
                app_state.event_counter += 1
                await consumer.commit()
            except Exception as e:
                logging.error(f"Failed to process message offset={msg.offset}: {e}", exc_info=True)
                continue
    except asyncio.CancelledError:
        print("Consumer loop cancelled.")
    finally:
        await consumer.stop()
