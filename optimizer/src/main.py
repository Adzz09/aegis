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
from shared.schemas.assignment import AssignmentPlan, EngagementOrder, EngagementStatus

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

class GreedyOptimizer:
    def __init__(self):
        self.interceptors = ["INT-01", "INT-02", "INT-03", "INT-04"]
        self.active_assignments = {} # track_id -> interceptor_id

    def optimize(self, threats):
        assignments = []
        unassigned = []
        
        # Sort threats by score descending
        sorted_threats = sorted(threats, key=lambda x: x.score, reverse=True)
        
        available_interceptors = set(self.interceptors) - set(self.active_assignments.values())
        
        for threat in sorted_threats:
            if threat.level in [ThreatLevel.HOSTILE, ThreatLevel.CRITICAL]:
                if threat.track_id in self.active_assignments:
                    # Already assigned
                    assignments.append(self.create_order(threat, self.active_assignments[threat.track_id]))
                elif available_interceptors:
                    # Assign new interceptor
                    interceptor_id = available_interceptors.pop()
                    self.active_assignments[threat.track_id] = interceptor_id
                    assignments.append(self.create_order(threat, interceptor_id))
                else:
                    unassigned.append(threat.track_id)
            else:
                # Not a hostile threat, remove assignment if exists
                if threat.track_id in self.active_assignments:
                    del self.active_assignments[threat.track_id]

        return AssignmentPlan(
            plan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            assignments=assignments,
            unassigned_threats=unassigned
        )

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

optimizer = GreedyOptimizer()

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
