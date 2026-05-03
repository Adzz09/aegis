import redis.asyncio as redis
import os
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class StateManager:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)

    async def get_system_state(self):
        # In a real app, we'd aggregate from multiple keys
        # For MVP, we'll store the whole state in a JSON string or hash
        state_json = await self.redis.get("aegis:state")
        if state_json:
            return json.loads(state_json)
        return {
            "tracks": {},
            "threats": [],
            "assignments": [],
            "systemHealth": {},
            "metrics": {}
        }

    async def update_module_health(self, module_id, status):
        state = await self.get_system_state()
        state["systemHealth"][module_id] = status
        await self.redis.set("aegis:state", json.dumps(state))
