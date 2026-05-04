from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class InterceptorType(str, Enum):
    """Types of defensive platforms."""
    KINETIC = "KINETIC"           # Missiles, guns
    AEROSOL = "AEROSOL"          # Chemical dispensers
    STREAMER = "STREAMER"         # Adhesive streamers
    NET = "NET"                  # Net launchers
    EW = "EW"                    # Electronic warfare

class InterceptorStatus(str, Enum):
    """Status of defensive platform."""
    READY = "READY"
    RELOADING = "RELOADING"
    ENGAGING = "ENGAGING"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"

class Interceptor(BaseModel):
    """Defensive interceptor platform."""
    interceptor_id: str
    interceptor_type: InterceptorType
    location_x: float
    location_y: float
    location_z: float = 0.0
    capacity: int = 1                    # Drones per reload
    reload_time_s: int = 30               # Seconds to reload
    effective_range_m: float = 500.0    # Maximum engagement range
    current_load: int = 0                # Current drones engaged
    last_reload_time: Optional[datetime] = None
    status: InterceptorStatus = InterceptorStatus.READY

class CountermeasureType(str, Enum):
    """Types of non-kinetic countermeasures."""
    AEROSOL = "AEROSOL"
    STREAMER = "STREAMER"
    EW = "EW"
    GPS_SPOOF = "GPS_SPOOF"
    PROTOCOL_INJECT = "PROTOCOL_INJECT"

class CountermeasureOrder(BaseModel):
    """Order for non-kinetic countermeasure."""
    order_id: str
    countermeasure_type: CountermeasureType
    target_zone_x: float
    target_zone_y: float
    radius_m: float
    duration_s: int
    intensity: int = Field(ge=1, le=10, default=5)

class EngagementStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ENGAGING = "ENGAGING"
    INTERCEPTED = "INTERCEPTED"
    MISSED = "MISSED"
    ABORTED = "ABORTED"

class EngagementOrder(BaseModel):
    assignment_id: str
    track_id: str
    interceptor_id: str
    timestamp: datetime
    status: EngagementStatus
    eta_s: float
    engagement_range_m: float

class AssignmentPlan(BaseModel):
    plan_id: str
    timestamp: datetime
    assignments: List[EngagementOrder]
    unassigned_threats: List[str]
    countermeasure_orders: List[CountermeasureOrder] = Field(default_factory=list)
    plan_validity_ms: int = 500
