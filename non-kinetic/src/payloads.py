from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AerosolType(str, Enum):
    """Types of aerosol payloads."""
    SILICON = "silicon"           # Silicone spray - gums up motors
    OIL = "oil"                   # Light oil - clogs rotors
    DRY_POWDER = "dry_powder"     # Talc/limestone - fouls sensors
    WATER_MIST = "water_mist"     # Dense mist - obscures vision


class StreamerType(str, Enum):
    """Types of streamer payloads."""
    ADHESIVE = "adhesive"         # Glue-coated streamers
    KITE_STRING = "kite_string"  # Thin line entangles propellers
    WIRE = "wire"                 # Thin wire - cuts propellers


class EWType(str, Enum):
    """Types of electronic warfare."""
    NOISE = "noise"               # Broadband noise
    SWEEP = "sweep"               # Frequency sweep jamming
    PULSE = "pulse"               # Pulsed disruption
    DEAUTH = "deauth"            # WiFi deauthentication


class DispenserStatus(str, Enum):
    """Status of aerosol dispenser."""
    IDLE = "IDLE"
    DISPENSING = "DISPENSING"
    RELOADING = "RELOADING"
    FAULT = "FAULT"


class AerosolDispenser(BaseModel):
    """Aerosol dispenser platform."""
    dispenser_id: str
    location_x: float
    location_y: float
    location_z: float
    aerosol_type: AerosolType
    capacity_uses: int = 100      # Uses per reload
    current_uses: int = 0
    reload_time_s: int = 10
    spray_radius_m: float = 50
    effectiveness: float = 0.8  # 0-1 scale


class StreamerLauncher(BaseModel):
    """Streamer launcher platform."""
    launcher_id: str
    location_x: float
    location_y: float
    location_z: float
    streamer_type: StreamerType
    barrel_count: int = 8         # Number of barrels
    capacity_per_barrel: int = 2 # Streamers per barrel
    current_load: int = 0
    reload_time_s: int = 15
    effective_range_m: float = 100
    streamer_length_m: float = 5


class ECMStatus(str, Enum):
    """Status of EW/jammer platform."""
    IDLE = "IDLE"
    STANDBY = "STANDBY"
    JAMMING = "JAMMING"
    SWEEPING = "SWEEPING"
    FAULT = "FAULT"


class EWPlatform(BaseModel):
    """Electronic warfare / jamming platform."""
    platform_id: str
    location_x: float
    location_y: float
    location_z: float
    ew_type: EWType
    freq_start_mhz: float = 2400   # 2.4 GHz band start
    freq_end_mhz: float = 2500    # 2.5 GHz band end
    max_power_dbm: int = 30       # 1 Watt
    status: ECMStatus = ECMStatus.IDLE


class CountermeasureRequest(BaseModel):
    """Request for countermeasure deployment."""
    request_id: str
    countermeasure_type: str  # "aerosol", "streamer", "ew"
    target_x: float
    target_y: float
    radius_m: float
    duration_s: int
    intensity: int = Field(ge=1, le=10, default=5)
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class CountermeasureStatus(BaseModel):
    """Status update from countermeasure system."""
    request_id: str
    status: str  # "dispensing", "complete", "failed"
    drones_affected: int = 0
    completed_at: Optional[datetime] = None