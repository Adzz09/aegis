import asyncio
import sys
import os
import json
import uuid
import time
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from confluent_kafka import Consumer, Producer
import redis
from shared.schemas.threat_score import ThreatScore, ThreatLevel
from shared.schemas.assignment import (
    AssignmentPlan, EngagementOrder, EngagementStatus,
    Interceptor, InterceptorType, InterceptorStatus
)

# Optional TimescaleDB persistence
try:
    from shared.utils.database import write_assignment_plan, init_database
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    write_assignment_plan = None
    init_database = None

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

conf_consumer = {
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'optimizer',
    'auto.offset.reset': 'latest'
}
consumer = Consumer(conf_consumer)
consumer.subscribe(['threat.scores'])

conf_producer = {'bootstrap.servers': KAFKA_BROKERS}
producer = Producer(conf_producer)

r = redis.from_url(REDIS_URL)


class HighCapacityOptimizer:
    """
    Optimizer with high-capacity interceptor support.
    
    Supports:
    - Standard interceptors (1 drone per engagement)
    - High-capacity interceptors (50+ drones per load)
    - Aerosol/streamer systems (area denial)
    """
    
    def __init__(self):
        # High-capacity + standard interceptors
        self.interceptors = {
            "INT-01": Interceptor(
                interceptor_id="INT-01",
                interceptor_type=InterceptorType.KINETIC,
                location_x=5, location_y=2, location_z=0,
                capacity=1, reload_time_s=30, effective_range_m=500,
                status=InterceptorStatus.READY
            ),
            "INT-02": Interceptor(
                interceptor_id="INT-02",
                interceptor_type=InterceptorType.KINETIC,
                location_x=-5, location_y=2, location_z=0,
                capacity=1, reload_time_s=30, effective_range_m=500,
                status=InterceptorStatus.READY
            ),
            "INT-03": Interceptor(
                interceptor_id="INT-03",
                interceptor_type=InterceptorType.KINETIC,
                location_x=5, location_y=-5, location_z=0,
                capacity=1, reload_time_s=30, effective_range_m=500,
                status=InterceptorStatus.READY
            ),
            "INT-04": Interceptor(
                interceptor_id="INT-04",
                interceptor_type=InterceptorType.KINETIC,
                location_x=-5, location_y=-5, location_z=0,
                capacity=1, reload_time_s=30, effective_range_m=500,
                status=InterceptorStatus.READY
            ),
            # High-capacity interceptor (Phase 2)
            "HC-01": Interceptor(
                interceptor_id="HC-01",
                interceptor_type=InterceptorType.KINETIC,
                location_x=0, location_y=10, location_z=0,
                capacity=50, reload_time_s=60, effective_range_m=1000,
                status=InterceptorStatus.READY
            ),
            # Aerosol system (Phase 2)
            "AERO-01": Interceptor(
                interceptor_id="AERO-01",
                interceptor_type=InterceptorType.AEROSOL,
                location_x=0, location_y=0, location_z=10,
                capacity=100, reload_time_s=5, effective_range_m=200,
                status=InterceptorStatus.READY
            ),
        }
        
        # track_id -> list of assigned interceptors
        self.active_assignments = {}  # track_id -> [interceptor_ids]
        
    def optimize(self, threats):
        assignments = []
        unassigned = []
        
        # Sort threats by threat score (highest first), then by distance (closest first)
        sorted_threats = sorted(
            threats, 
            key=lambda t: (t.score, -(t.estimated_impact_time_s or 999)),
            reverse=True
        )
        
        for threat in sorted_threats:
            if threat.level not in [ThreatLevel.HOSTILE, ThreatLevel.CRITICAL]:
                # Non-hostile - clean up any assignments
                if threat.track_id in self.active_assignments:
                    self._release_interceptors(threat.track_id)
                continue
                
            # Find best interceptor for this threat
            assigned = self._assign_interceptor(threat)
            
            if assigned:
                for int_id, order in assigned.items():
                    assignments.append(order)
            else:
                unassigned.append(threat.track_id)
        
        return AssignmentPlan(
            plan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            assignments=assignments,
            unassigned_threats=unassigned
        )
    
    def _assign_interceptor(self, threat):
        """Assign best interceptor to a threat."""
        assigned = {}
        
        for int_id, interceptor in self.interceptors.items():
            # Skip if not ready or reloading
            if interceptor.status != InterceptorStatus.READY:
                continue
                
            # Skip if at capacity
            if interceptor.current_load >= interceptor.capacity:
                continue
            
            # Calculate distance
            threat_dist = self._calculate_distance(
                interceptor.location_x, interceptor.location_y,
                0, 0  # Assuming threat at origin for now
            )
            
            # Skip if out of range
            if threat_dist > interceptor.effective_range_m:
                continue
            
            # Assign this interceptor
            order = EngagementOrder(
                assignment_id=f"ASG-{str(uuid.uuid4())[:6]}",
                track_id=threat.track_id,
                interceptor_id=int_id,
                timestamp=datetime.utcnow(),
                status=EngagementStatus.ENGAGING,
                eta_s=threat.estimated_impact_time_s or 30.0,
                engagement_range_m=threat_dist
            )
            
            # Update interceptor load
            self.interceptors[int_id].current_load += 1
            if self.interceptors[int_id].current_load >= self.interceptors[int_id].capacity:
                self.interceptors[int_id].status = InterceptorStatus.RELOADING
            
            # Track assignment
            if threat.track_id not in self.active_assignments:
                self.active_assignments[threat.track_id] = []
            self.active_assignments[threat.track_id].append(int_id)
            
            assigned[int_id] = order
            break  # One interceptor per threat is enough
        
        return assigned if assigned else None
    
    def _release_interceptors(self, track_id):
        """Release interceptors when threat is neutralized."""
        if track_id not in self.active_assignments:
            return
            
        for int_id in self.active_assignments[track_id]:
            if int_id in self.interceptors:
                self.interceptors[int_id].current_load = max(0, self.interceptors[int_id].current_load - 1)
                if self.interceptors[int_id].current_load < self.interceptors[int_id].capacity:
                    self.interceptors[int_id].status = InterceptorStatus.READY
        
        del self.active_assignments[track_id]
    
    def _calculate_distance(self, x1, y1, x2, y2):
        """Calculate 2D distance in meters."""
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    def create_order(self, threat, interceptor_id):
        return EngagementOrder(
            assignment_id=f"ASG-{str(uuid.uuid4())[:6]}",
            track_id=threat.track_id,
            interceptor_id=interceptor_id,
            timestamp=datetime.utcnow(),
            status=EngagementStatus.ENGAGING,
            eta_s=threat.estimated_impact_time_s or 30.0,
            engagement_range_m=500.0
        )

async def main():
    print(f"Starting Threat Assignment Optimizer... connecting to {KAFKA_BROKERS}")
    
    current_threats = {} # track_id -> ThreatScore

    try:
        while True:
            msg = consumer.poll(0.1)
            if msg:
                if not msg.error():
                    payload = json.loads(msg.value().decode('utf-8'))
                    threat = ThreatScore(**payload)
                    current_threats[threat.track_id] = threat

            # Run optimization cycle at 2Hz
            plan = optimizer.optimize(list(current_threats.values()))
            
            # Publish assignment plan
            producer.produce('assignments', plan.model_dump_json().encode('utf-8'))
            producer.flush()
            
            # Cleanup old threats (simulated)
            now = time.time()
            to_delete = [tid for tid, t in current_threats.items() if (datetime.utcnow() - t.timestamp).total_seconds() > 2.0]
            for tid in to_delete:
                del current_threats[tid]
                if tid in optimizer.active_assignments:
                    del optimizer.active_assignments[tid]

            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(main())
