from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GPSSpoofStatus(str, Enum):
    """Status of GPS spoofing attack."""
    IDLE = "IDLE"
    SPOOFING = "SPOOFING"
    SWEEPING = "SWEEPING"
    FAULT = "FAULT"


class ProtocolTarget(str, Enum):
    """Target drone protocols."""
    MAVLINK = "mavlink"       # Pixhawk/Ardupilot
    DJI_OSD = "dji_osd"       # DJI OcuSync
    CUSTOM_RF = "custom_rf"   # Custom RF protocol


class AttackType(str, Enum):
    """Types of autonomy attacks."""
    GPS_SPOOF = "gps_spoof"
    PROTOCOL_INJECT = "protocol_inject"
    SWARM_DESYNC = "swarm_desync"
    ROUTE_POISON = "route_poison"


class GPSSpoofPayload(BaseModel):
    """GPS spoofing attack parameters."""
    attack_id: str
    spoofer_id: str
    
    # Target zone
    target_lat_center: float
    target_lon_center: float
    target_radius_m: float = 500
    
    # Fake position to inject
    fake_lat_offset: float     # Degrees to shift
    fake_lon_offset: float
    fake_alt_offset_m: float = 0
    
    # Attack parameters
    spoof_strength: int = Field(ge=1, le=10, default=5)
    sweep_rate: float = 0.1     # Degrees per second (for gradual shift)
    
    # Timing
    duration_s: int = 30
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class ProtocolInjectPayload(BaseModel):
    """Protocol injection attack parameters."""
    attack_id: str
    injector_id: str
    target_protocol: ProtocolTarget
    
    # Command to inject
    command_type: str  # "LAND", "RTL", "EMERGENCY_LAND", "RETURN_TO_HOME"
    target_drone_ids: List[str]
    
    # Injection parameters
    repeat_count: int = 3      # Send multiple times for reliability
    interval_ms: int = 100      # Between repeats
    
    # Optional: custom packet data
    custom_packet: Optional[bytes] = None
    
    duration_s: int = 10
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class SwarmDegradePayload(BaseModel):
    """Swarm mesh network degradation attack."""
    attack_id: str
    jammer_id: str
    
    # Attack type
    attack_type: AttackType      # "flood", "desync", "route_poison"
    
    # Target
    target_channel: int = 0     # Mesh channel to attack
    target_subnet: str = "192.168.1.0/24"
    
    # Intensity
    intensity: int = Field(ge=1, le=10, default=5)
    packet_rate: int = 1000     # Packets per second
    
    duration_s: int = 60
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class AttackStatus(BaseModel):
    """Status update from attack system."""
    attack_id: str
    attack_type: AttackType
    status: str  # "active", "complete", "failed"
    targets_affected: int = 0
    drones_fallout: int = 0     # Drones that lost navigation
    completed_at: Optional[datetime] = None


class AttackResult(BaseModel):
    """Result of an attack operation."""
    attack_id: str
    attack_type: str
    status: str
    success: bool
    drones_affected: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "attack_id": self.attack_id,
            "attack_type": self.attack_type,
            "status": self.status,
            "success": self.success,
            "drones_affected": self.drones_affected,
            "error_message": self.error_message
        }


# Attack capability enumeration for display
class AttackCapability:
    """Enumeration of attack capabilities."""
    
    GPS_SPOOF = "GPS Spoofing"
    PROTOCOL_INJECT = "Protocol Injection"
    SWARM_DESYNC = "Swarm De-synchronization"
    ROUTE_POISON = "Mesh Route Poisoning"
    
    ALL = [
        GPS_SPOOF,
        PROTOCOL_INJECT,
        SWARM_DESYNC,
        ROUTE_POISON
    ]
    
    @classmethod
    def get_risk_level(cls, attack_type: str) -> str:
        """Get risk level description."""
        risk_levels = {
            cls.GPS_SPOOF: "HIGH - Causes navigation loss",
            cls.PROTOCOL_INJECT: "MEDIUM - Requires protocol reverse-engineering",
            cls.SWARM_DESYNC: "MEDIUM - Effective against mesh networks",
            cls.ROUTE_POISON: "LOW - Requires network access"
        }
        return risk_levels.get(attack_type, "UNKNOWN")