import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel
from .state_manager import StateManager
from contextlib import asynccontextmanager

# Define globals before lifespan so they are accessible
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")
producer = None
state_manager = StateManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKERS)
    await producer.start()
    
    # Startup: Start background tasks
    consumer_task = asyncio.create_task(kafka_consumer_task())
    prune_task = asyncio.create_task(state_pruning_task())
    yield
    # Shutdown: Clean up tasks
    consumer_task.cancel()
    prune_task.cancel()
    await producer.stop()

app = FastAPI(title="AEGIS API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def kafka_consumer_task():
    consumer = AIOKafkaConsumer(
        'fused.tracks', 'threat.scores', 'assignments',
        bootstrap_servers=KAFKA_BROKERS,
        group_id="api-gateway"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode('utf-8'))
            topic = msg.topic
            
            # Update Redis State
            state = await state_manager.get_system_state()
            
            if topic == 'fused.tracks':
                tid = payload['track_id']
                # Preserve existing threat fields if already scored
                existing = state['tracks'].get(tid, {})
                merged = {**payload}
                for field in ('threat_score', 'threat_level', 'classification'):
                    if field in existing:
                        merged[field] = existing[field]
                state['tracks'][tid] = merged
            elif topic == 'threat.scores':
                tid = payload['track_id']
                if tid in state['tracks']:
                    state['tracks'][tid]['threat_score'] = payload['score']
                    state['tracks'][tid]['threat_level'] = payload['level']
                    state['tracks'][tid]['classification'] = payload['classification_label']
            elif topic == 'assignments':
                # payload is the full AssignmentPlan; extract the list of EngagementOrders
                state['assignments'] = payload.get('assignments', [])
            
            await state_manager.redis.set("aegis:state", json.dumps(state))
    finally:
        await consumer.stop()

async def state_pruning_task():
    from datetime import datetime, timezone
    while True:
        try:
            state = await state_manager.get_system_state()
            now = datetime.now(timezone.utc)
            to_delete = []
            
            for tid, tdata in state['tracks'].items():
                ts_str = tdata.get('timestamp')
                if ts_str:
                    try:
                        # Handle both aware and naive iso formats
                        t = datetime.fromisoformat(ts_str)
                        if t.tzinfo is None:
                            t = t.replace(tzinfo=timezone.utc)
                        if (now - t).total_seconds() > 3.0:
                            to_delete.append(tid)
                    except Exception:
                        pass
                        
            if to_delete:
                for tid in to_delete:
                    del state['tracks'][tid]
                await state_manager.redis.set("aegis:state", json.dumps(state))
                
            await asyncio.sleep(1.0)
        except Exception as e:
            print(f"State pruning error: {e}")
            await asyncio.sleep(1.0)

@app.get("/api/health")
async def health():
    return await state_manager.get_system_state()

class ScenarioRequest(BaseModel):
    drone_count: int = 50

@app.post("/api/sim/scenario")
async def trigger_scenario(request: ScenarioRequest = None):
    count = request.drone_count if request else 50
    if producer:
        command = {
            "command": "trigger_swarm",
            "drone_count": count
        }
        await producer.send_and_wait('sim.commands', json.dumps(command).encode('utf-8'))
        return {"status": "success", "message": f"Triggered swarm of {count} drones"}
    return {"status": "error", "message": "Producer not initialized"}

@app.websocket("/ws/state")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Dashboard connected")
    try:
        while True:
            state = await state_manager.get_system_state()
            await websocket.send_text(json.dumps(state))
            await asyncio.sleep(0.1) # 10Hz
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except Exception as e:
        print(f"WS Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
