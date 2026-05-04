import pytest
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.schemas.track import FusedTrack
from shared.schemas.threat_score import ThreatScore, ThreatLevel


class HeuristicClassifier:
    """Heuristic-based classifier from main.py."""
    def classify(self, track: FusedTrack) -> ThreatScore:
        import random
        
        # Features for classification
        speed = (track.vel_x**2 + track.vel_y**2 + track.vel_z**2)**0.5
        dist_to_origin = (track.pos_x**2 + track.pos_y**2 + track.pos_z**2)**0.5
        
        # Heuristic rules
        score = 0.0
        label = "UNKNOWN"
        level = ThreatLevel.UNKNOWN

        if speed > 20.0:  # High speed -> likely hostile drone
            score = random.uniform(0.7, 0.95)
            label = "HOSTILE_FPV"
            level = ThreatLevel.HOSTILE
        elif dist_to_origin < 500:  # Very close to protected zone
            score = 0.98
            label = "HOSTILE_CRITICAL"
            level = ThreatLevel.CRITICAL
        elif speed < 5.0:  # Slow / Hovering -> monitoring
            score = 0.4
            label = "MONITORING"
            level = ThreatLevel.CAUTION
        else:  # Normal speed
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


class TestHeuristicClassifier:
    """Tests for HeuristicClassifier class."""
    
    @pytest.fixture
    def classifier(self):
        return HeuristicClassifier()
    
    @pytest.fixture
    def fast_incoming_track(self):
        """Track moving fast toward protected zone."""
        return FusedTrack(
            track_id="TRK-001",
            timestamp=datetime.utcnow(),
            pos_x=100,
            pos_y=200,
            pos_z=50,
            vel_x=15,
            vel_y=-25,
            vel_z=0,
            position_uncertainty_m=3.0,
            velocity_uncertainty_mps=2.0,
            is_confirmed=True
        )
    
    @pytest.fixture
    def slow_track(self):
        """Track moving slowly."""
        return FusedTrack(
            track_id="TRK-002",
            timestamp=datetime.utcnow(),
            pos_x=500,
            pos_y=800,
            pos_z=100,
            vel_x=2,
            vel_y=3,
            vel_z=0,
            position_uncertainty_m=5.0,
            velocity_uncertainty_mps=1.0,
            is_confirmed=True
        )
    
    @pytest.fixture
    def close_track(self):
        """Track very close to protected zone."""
        return FusedTrack(
            track_id="TRK-003",
            timestamp=datetime.utcnow(),
            pos_x=50,
            pos_y=100,
            pos_z=20,
            vel_x=5,
            vel_y=8,
            vel_z=0,
            position_uncertainty_m=2.0,
            velocity_uncertainty_mps=1.5,
            is_confirmed=True
        )
    
    @pytest.fixture
    def medium_track(self):
        """Track at medium distance, normal speed."""
        return FusedTrack(
            track_id="TRK-004",
            timestamp=datetime.utcnow(),
            pos_x=1000,
            pos_y=1500,
            pos_z=200,
            vel_x=10,
            vel_y=12,
            vel_z=1,
            position_uncertainty_m=4.0,
            velocity_uncertainty_mps=2.0,
            is_confirmed=True
        )
    
    def test_classifies_fast_drone_as_hostile(self, classifier, fast_incoming_track):
        """Test high-speed drone is classified as HOSTILE."""
        result = classifier.classify(fast_incoming_track)
        
        assert result.level == ThreatLevel.HOSTILE
        assert result.classification_label == "HOSTILE_FPV"
        assert result.score > 0.6
    
    def test_classifies_slow_drone_as_caution(self, classifier, slow_track):
        """Test slow drone is classified as CAUTION."""
        result = classifier.classify(slow_track)
        
        assert result.level == ThreatLevel.CAUTION
        assert result.classification_label == "MONITORING"
    
    def test_classifies_close_drone_as_critical(self, classifier, close_track):
        """Test drone close to protected zone is CRITICAL."""
        result = classifier.classify(close_track)
        
        assert result.level == ThreatLevel.CRITICAL
        assert result.classification_label == "HOSTILE_CRITICAL"
    
    def test_classifies_medium_drone_as_benign(self, classifier, medium_track):
        """Test medium-distance, normal-speed drone is BENIGN."""
        result = classifier.classify(medium_track)
        
        assert result.level == ThreatLevel.BENIGN
        assert result.classification_label == "BENIGN"
    
    def test_classifier_preserves_track_id(self, classifier, fast_incoming_track):
        """Test result has same track ID."""
        result = classifier.classify(fast_incoming_track)
        
        assert result.track_id == fast_incoming_track.track_id
    
    def test_classifier_has_timestamp(self, classifier, fast_incoming_track):
        """Test result has timestamp."""
        result = classifier.classify(fast_incoming_track)
        
        assert result.timestamp is not None
    
    def test_classifier_calculates_swarm_probability(self, classifier, fast_incoming_track):
        """Test hostile tracks have high swarm probability."""
        result = classifier.classify(fast_incoming_track)
        
        # Hostile tracks should have swarm_probability > 0.5
        if result.classification_label.startswith("HOSTILE"):
            assert result.swarm_probability > 0.5
    
    def test_classifier_calculates_eta(self, classifier, fast_incoming_track):
        """Test ETA is calculated."""
        result = classifier.classify(fast_incoming_track)
        
        assert result.estimated_impact_time_s is not None
        assert result.estimated_impact_time_s > 0
    
    def test_score_within_bounds(self, classifier, fast_incoming_track):
        """Test score is always between 0 and 1."""
        for _ in range(10):
            result = classifier.classify(fast_incoming_track)
            assert 0.0 <= result.score <= 1.0
    
    def test_swarm_probability_within_bounds(self, classifier, fast_incoming_track):
        """Test swarm_probability is always between 0 and 1."""
        for _ in range(10):
            result = classifier.classify(fast_incoming_track)
            assert 0.0 <= result.swarm_probability <= 1.0
    
    def test_velocity_calculation(self, classifier):
        """Test classifier correctly calculates velocity."""
        # Track with known velocity
        track = FusedTrack(
            track_id="TRK-VEL",
            timestamp=datetime.utcnow(),
            pos_x=0,
            pos_y=0,
            pos_z=0,
            vel_x=3,
            vel_y=4,
            vel_z=0,
            position_uncertainty_m=1.0,
            velocity_uncertainty_mps=1.0,
            is_confirmed=True
        )
        
        # Speed should be 5 (3-4-5 triangle)
        result = classifier.classify(track)
        
        # With speed=5 and distance=0, should be CAUTION (< 5.0)
        assert result.level == ThreatLevel.CAUTION
    
    def test_no_floating_point_errors(self, classifier):
        """Test classifier handles various edge cases."""
        # Zero velocity
        track = FusedTrack(
            track_id="TRK-ZERO",
            timestamp=datetime.utcnow(),
            pos_x=1000,
            pos_y=1000,
            pos_z=100,
            vel_x=0,
            vel_y=0,
            vel_z=0,
            position_uncertainty_m=1.0,
            velocity_uncertainty_mps=0.0,
            is_confirmed=True
        )
        
        result = classifier.classify(track)
        
        # Should handle zero velocity without error
        assert result is not None
        assert result.estimated_impact_time_s is not None