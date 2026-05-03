from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ThreatLevel(str, Enum):
    BENIGN = "BENIGN"
    UNKNOWN = "UNKNOWN"
    CAUTION = "CAUTION"
    HOSTILE = "HOSTILE"
    CRITICAL = "CRITICAL"
    ENGAGED = "ENGAGED"

class ThreatScore(BaseModel):
    track_id: str
    timestamp: datetime
    score: float = Field(ge=0.0, le=1.0)
    level: ThreatLevel
    classification_label: str
    swarm_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_impact_time_s: Optional[float] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
