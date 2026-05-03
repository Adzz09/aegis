import asyncio
import json
from aiokafka import AIOKafkaConsumer

async def test_consumer():
    consumer = AIOKafkaConsumer(
        'fused.tracks',
        bootstrap_servers='localhost:19092',
        group_id="test-consumer-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode('utf-8'))
            print("Received:", payload['track_id'])
    except Exception as e:
        print(f"CRASH: {e}")
    finally:
        await consumer.stop()

asyncio.run(test_consumer())
