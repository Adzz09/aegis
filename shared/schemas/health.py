from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

class ModuleStatus(str, Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"

class ModuleHealth(BaseModel):
    module_id: str
    status: ModuleStatus
    timestamp: datetime
    latency_ms: Optional[float] = None
    throughput: Optional[float] = None
    error_count: int = 0
    message: Optional[str] = None
    metrics: Dict = Field(default_factory=dict)
