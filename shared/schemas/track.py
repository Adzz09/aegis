from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class SensorType(str, Enum):
    RADAR = "RADAR"
    OPTICAL = "OPTICAL"
    RF = "RF"

class SensorEvent(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    timestamp: datetime
    azimuth_deg: float
    elevation_deg: Optional[float] = None
    range_m: float
    snr_db: float
    raw_data: Optional[Dict] = None

class FusedTrack(BaseModel):
    track_id: str
    timestamp: datetime
    pos_x: float
    pos_y: float
    pos_z: float
    vel_x: float
    vel_y: float
    vel_z: float
    position_uncertainty_m: float
    velocity_uncertainty_mps: float
    classification: str = "UNKNOWN"
    threat_score: float = 0.0
    threat_level: Optional[str] = "UNKNOWN"
    is_confirmed: bool = False
    source_sensors: List[str] = Field(default_factory=list)
