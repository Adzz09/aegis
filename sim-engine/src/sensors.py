import math
import random
import time
from datetime import datetime
import sys
import os

# Add shared to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.schemas.track import SensorEvent, SensorType

class SensorSimulator:
    def __init__(self, sensor_id, sensor_type, pos=(0, 0, 0), range_max=5000):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.pos_x, self.pos_y, self.pos_z = pos
        self.range_max = range_max
        self.noise_std = 5.0 # meters

    def detect(self, drone):
        dx = drone.pos_x - self.pos_x
        dy = drone.pos_y - self.pos_y
        dz = drone.pos_z - self.pos_z
        dist = (dx**2 + dy**2 + dz**2)**0.5

        if dist > self.range_max:
            return None

        # Add noise
        noisy_dist = dist + random.gauss(0, self.noise_std)
        
        # Calculate angles
        azimuth = math.degrees(math.atan2(dx, dy))
        elevation = math.degrees(math.atan2(dz, math.sqrt(dx**2 + dy**2)))

        return SensorEvent(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            timestamp=datetime.utcnow(),
            azimuth_deg=azimuth,
            elevation_deg=elevation,
            range_m=noisy_dist,
            snr_db=max(10, 40 - (dist / 100)) # Simple path loss model
        )

import math # Needed for atan2
