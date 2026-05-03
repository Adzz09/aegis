import asyncio
import time
import json
import random
try:
    from .drone import DroneAgent
    from .sensors import SensorSimulator
except ImportError:
    from drone import DroneAgent
    from sensors import SensorSimulator
from shared.schemas.track import SensorType

class SwarmOrchestrator:
    def __init__(self, drone_count=10):
        self.drones = [
            DroneAgent(
                start_pos=(random.uniform(-1000, 1000), random.uniform(2000, 3000), random.uniform(100, 500)),
                target_pos=(0, 0, 0)
            ) for _ in range(drone_count)
        ]
        self.sensors = [
            SensorSimulator("RADAR-01", SensorType.RADAR, pos=(0, 0, 0)),
            SensorSimulator("OPT-01", SensorType.OPTICAL, pos=(100, 100, 0)),
        ]
        self.running = False

    def trigger_scenario(self, drone_count=50):
        self.drones = [
            DroneAgent(
                start_pos=(random.uniform(-1000, 1000), random.uniform(2000, 3000), random.uniform(100, 500)),
                target_pos=(0, 0, 0),
                speed=random.uniform(22.0, 35.0)
            ) for _ in range(drone_count)
        ]
        print(f"Scenario triggered with {drone_count} drones.")

    async def run(self, callback):
        self.running = True
        last_time = time.time()
        
        while self.running:
            now = time.time()
            dt = now - last_time
            last_time = now

            # Update drones
            for drone in self.drones:
                drone.update(dt)

            # Generate sensor detections
            detections = []
            for sensor in self.sensors:
                for drone in self.drones:
                    event = sensor.detect(drone)
                    if event:
                        detections.append(event)
            
            # Send detections to Kafka via callback
            if detections:
                await callback(detections)

            await asyncio.sleep(0.1) # 10Hz simulation

