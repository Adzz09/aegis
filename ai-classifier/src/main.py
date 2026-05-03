import sys
import os
import json
import random
import asyncio
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from confluent_kafka import Consumer, Producer
from shared.schemas.threat_score import ThreatScore, ThreatLevel
from shared.schemas.track import FusedTrack

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")

conf_consumer = {
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'ai-classifier',
    'auto.offset.reset': 'latest'
}
consumer = Consumer(conf_consumer)
consumer.subscribe(['fused.tracks'])

conf_producer = {'bootstrap.servers': KAFKA_BROKERS}
producer = Producer(conf_producer)

class HeuristicClassifier:
    """Heuristic-based classifier for the demo."""
    def classify(self, track: FusedTrack) -> ThreatScore:
        # Features for classification
        speed = (track.vel_x**2 + track.vel_y**2 + track.vel_z**2)**0.5
        dist_to_origin = (track.pos_x**2 + track.pos_y**2 + track.pos_z**2)**0.5
        
        # Heuristic rules
        score = 0.0
        label = "UNKNOWN"
        level = ThreatLevel.UNKNOWN

        if speed > 20.0: # High speed -> likely hostile drone
            score = random.uniform(0.7, 0.95)
            label = "HOSTILE_FPV"
            level = ThreatLevel.HOSTILE
        elif dist_to_origin < 500: # Very close to protected zone
            score = 0.98
            label = "HOSTILE_CRITICAL"
            level = ThreatLevel.CRITICAL
        elif speed < 5.0: # Slow / Hovering -> monitoring
            score = 0.4
            label = "MONITORING"
            level = ThreatLevel.CAUTION
        else: # Normal speed
            score = 0.1
            label = "BENIGN"
            level = ThreatLevel.BENIGN

        # Add some jitter/noise to the score
        score = min(1.0, max(0.0, score + random.uniform(-0.05, 0.05)))

        return ThreatScore(
            track_id=track.track_id,
            timestamp=datetime.utcnow(),
            score=score,
            level=level,
            classification_label=label,
            swarm_probability=0.8 if label.startswith("HOSTILE") else 0.1,
            estimated_impact_time_s=dist_to_origin / max(speed, 1.0) if speed > 0 else None
        )

classifier = HeuristicClassifier()

async def main():
    print(f"Starting AI Threat Classifier (Heuristic Mode)... connecting to {KAFKA_BROKERS}")
    
    try:
        while True:
            msg = consumer.poll(0.1)
            if msg is None:
                await asyncio.sleep(0.01)
                continue
            
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Process fused track
            payload = json.loads(msg.value().decode('utf-8'))
            track = FusedTrack(**payload)
            
            # Classification
            threat_score = classifier.classify(track)
            
            # Publish threat score
            producer.produce('threat.scores', threat_score.model_dump_json().encode('utf-8'))
            producer.flush()
            
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(main())
