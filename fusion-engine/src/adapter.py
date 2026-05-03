from datetime import datetime
from typing import Dict
from shared.schemas.track import SensorEvent, SensorType

class DetectionEvent:
    def __init__(self, track_id: str, timestamp: datetime, pos_x: float, pos_y: float, pos_z: float, sensor_id: str):
        self.track_id = track_id
        self.timestamp = timestamp
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.sensor_id = sensor_id

class SensorAdapter:
    def normalize(self, event: SensorEvent) -> DetectionEvent:
        # Simple coordinate transformation for MVP
        # In a real system, this would involve complex mapping from polar to Cartesian
        # and handling sensor biases.
        
        # r, az, el -> x, y, z
        import math
        r = event.range_m
        az = math.radians(event.azimuth_deg)
        el = math.radians(event.elevation_deg or 0)
        
        x = r * math.cos(el) * math.sin(az)
        y = r * math.cos(el) * math.cos(az)
        z = r * math.sin(el)
        
        # Apply known sensor positions to convert relative -> global coordinates
        sensor_positions = {
            "RADAR-01": (0, 0, 0),
            "OPT-01": (100, 100, 0),
            "RF-01": (-50, 50, 0)
        }
        
        sx, sy, sz = sensor_positions.get(event.sensor_id, (0, 0, 0))
        
        return DetectionEvent(
            track_id=f"DET-{event.sensor_id}-{event.timestamp.timestamp()}",
            timestamp=event.timestamp,
            pos_x=x + sx,
            pos_y=y + sy,
            pos_z=z + sz,
            sensor_id=event.sensor_id
        )
