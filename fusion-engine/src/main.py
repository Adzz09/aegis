import asyncio
import os
import json
import time
from confluent_kafka import Consumer, Producer
try:
    from .adapter import SensorAdapter
    from .track_manager import TrackManager
except ImportError:
    from adapter import SensorAdapter
    from track_manager import TrackManager
from shared.schemas.track import SensorEvent

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")

conf_consumer = {
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'fusion-engine',
    'auto.offset.reset': 'latest'
}
consumer = Consumer(conf_consumer)
consumer.subscribe(['sensor.radar', 'sensor.optical', 'sensor.rf'])

conf_producer = {'bootstrap.servers': KAFKA_BROKERS}
producer = Producer(conf_producer)

adapter = SensorAdapter()
track_manager = TrackManager()

async def main():
    print(f"Starting Sensor Fusion Engine... connecting to {KAFKA_BROKERS}")
    
    last_publish_time = time.time()
    try:
        while True:
            msg = consumer.poll(0.01) # Reduced poll timeout to be more responsive
            
            if msg is not None:
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                else:
                    # Process detection
                    payload = json.loads(msg.value().decode('utf-8'))
                    event = SensorEvent(**payload)
                    detection = adapter.normalize(event)
                    track_manager.process_detection(detection)
            
            # Periodically publish fused tracks and cleanup (e.g., every 0.1 seconds)
            now = time.time()
            if now - last_publish_time >= 0.1:
                track_manager.cleanup_tracks()
                for tid, data in track_manager.tracks.items():
                    data['filter'].predict()
                
                fused = track_manager.get_fused_tracks()
                for track in fused:
                    producer.produce('fused.tracks', track.model_dump_json().encode('utf-8'))
                producer.flush()
                last_publish_time = now
                
            if msg is None:
                await asyncio.sleep(0.01)
                
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(main())
