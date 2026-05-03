from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

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
    plan_validity_ms: int = 500
