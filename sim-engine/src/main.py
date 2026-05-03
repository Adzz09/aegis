import asyncio
import os
import json
from confluent_kafka import Producer
from aiokafka import AIOKafkaConsumer
try:
    from .orchestrator import SwarmOrchestrator
except ImportError:
    from orchestrator import SwarmOrchestrator

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")

conf = {'bootstrap.servers': KAFKA_BROKERS}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')

async def kafka_callback(detections):
    for event in detections:
        topic = f"sensor.{event.sensor_type.value.lower()}"
        payload = event.model_dump_json()
        producer.produce(topic, payload.encode('utf-8'), callback=delivery_report)
    producer.flush()

async def command_listener(orchestrator):
    consumer = AIOKafkaConsumer(
        'sim.commands',
        bootstrap_servers=KAFKA_BROKERS,
        group_id="sim-engine"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode('utf-8'))
            if payload.get("command") == "trigger_swarm":
                count = payload.get("drone_count", 50)
                orchestrator.trigger_scenario(count)
    finally:
        await consumer.stop()

async def main():
    print(f"Starting Swarm Simulation Engine... connecting to {KAFKA_BROKERS}")
    orchestrator = SwarmOrchestrator(drone_count=10)
    asyncio.create_task(command_listener(orchestrator))
    await orchestrator.run(kafka_callback)

if __name__ == "__main__":
    asyncio.run(main())
