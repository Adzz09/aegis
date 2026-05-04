import pytest
import sys
import os
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.schemas.threat_score import ThreatScore, ThreatLevel
from shared.schemas.assignment import AssignmentPlan, EngagementOrder, EngagementStatus


class GreedyOptimizer:
    """Greedy assignment optimizer from main.py."""
    def __init__(self):
        self.interceptors = ["INT-01", "INT-02", "INT-03", "INT-04"]
        self.active_assignments = {}
    
    def optimize(self, threats):
        assignments = []
        unassigned = []
        
        # Sort threats by score descending
        sorted_threats = sorted(threats, key=lambda x: x.score, reverse=True)
        
        available_interceptors = set(self.interceptors) - set(self.active_assignments.values())
        
        for threat in sorted_threats:
            if threat.level in [ThreatLevel.HOSTILE, ThreatLevel.CRITICAL]:
                if threat.track_id in self.active_assignments:
                    assignments.append(self.create_order(threat, self.active_assignments[threat.track_id]))
                elif available_interceptors:
                    interceptor_id = available_interceptors.pop()
                    self.active_assignments[threat.track_id] = interceptor_id
                    assignments.append(self.create_order(threat, interceptor_id))
                else:
                    unassigned.append(threat.track_id)
            else:
                if threat.track_id in self.active_assignments:
                    del self.active_assignments[threat.track_id]
        
        return AssignmentPlan(
            plan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            assignments=assignments,
            unassigned_threats=unassigned,
            plan_validity_ms=500
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


class TestGreedyOptimizer:
    """Tests for GreedyOptimizer class."""
    
    @pytest.fixture
    def optimizer(self):
        return GreedyOptimizer()
    
    @pytest.fixture
    def hostile_threat(self):
        return ThreatScore(
            track_id="TRK-001",
            timestamp=datetime.utcnow(),
            score=0.9,
            level=ThreatLevel.HOSTILE,
            classification_label="HOSTILE_FPV",
            swarm_probability=0.8,
            estimated_impact_time_s=30.0
        )
    
    @pytest.fixture
    def critical_threat(self):
        return ThreatScore(
            track_id="TRK-002",
            timestamp=datetime.utcnow(),
            score=0.98,
            level=ThreatLevel.CRITICAL,
            classification_label="HOSTILE_CRITICAL",
            swarm_probability=0.95,
            estimated_impact_time_s=10.0
        )
    
    @pytest.fixture
    def benign_threat(self):
        return ThreatScore(
            track_id="TRK-003",
            timestamp=datetime.utcnow(),
            score=0.1,
            level=ThreatLevel.BENIGN,
            classification_label="BENIGN",
            swarm_probability=0.05,
            estimated_impact_time_s=None
        )
    
    def test_optimizer_initializes_with_interceptors(self, optimizer):
        """Test optimizer has 4 interceptors."""
        assert len(optimizer.interceptors) == 4
        assert "INT-01" in optimizer.interceptors
        assert "INT-02" in optimizer.interceptors
        assert "INT-03" in optimizer.interceptors
        assert "INT-04" in optimizer.interceptors
    
    def test_assigns_hostile_to_interceptor(self, optimizer, hostile_threat):
        """Test hostile threat gets assigned to interceptor."""
        plan = optimizer.optimize([hostile_threat])
        
        assert len(plan.assignments) == 1
        assert plan.assignments[0].interceptor_id in optimizer.interceptors
        assert plan.assignments[0].track_id == hostile_threat.track_id
    
    def test_assigns_critical_first(self, optimizer, hostile_threat, critical_threat):
        """Test critical threats are prioritized."""
        plan = optimizer.optimize([hostile_threat, critical_threat])
        
        # Critical should be assigned first
        first_assignment = plan.assignments[0]
        assert first_assignment.track_id == critical_threat.track_id
    
    def test_no_assignment_for_benign(self, optimizer, benign_threat):
        """Test benign threats are not assigned."""
        plan = optimizer.optimize([benign_threat])
        
        assert len(plan.assignments) == 0
    
    def test_unassigned_when_no_interceptors(self, optimizer):
        """Test threats remain unassigned when all interceptors busy."""
        # Fill all interceptors
        for i in range(4):
            threat = ThreatScore(
                track_id=f"TRK-{i:03d}",
                timestamp=datetime.utcnow(),
                score=0.9,
                level=ThreatLevel.HOSTILE,
                classification_label="HOSTILE_FPV",
                swarm_probability=0.8,
                estimated_impact_time_s=30.0
            )
            optimizer.optimize([threat])
        
        # Now all interceptors are busy, try to assign another
        fifth_threat = ThreatScore(
            track_id="TRK-005",
            timestamp=datetime.utcnow(),
            score=0.9,
            level=ThreatLevel.HOSTILE,
            classification_label="HOSTILE_FPV",
            swarm_probability=0.8,
            estimated_impact_time_s=30.0
        )
        
        plan = optimizer.optimize([fifth_threat])
        
        # Should be unassigned
        assert "TRK-005" in plan.unassigned_threats
    
    def test_plan_has_id(self, optimizer, hostile_threat):
        """Test plan has a plan ID."""
        plan = optimizer.optimize([hostile_threat])
        
        assert plan.plan_id is not None
    
    def test_plan_has_timestamp(self, optimizer, hostile_threat):
        """Test plan has a timestamp."""
        plan = optimizer.optimize([hostile_threat])
        
        assert plan.plan_timestamp is not None
    
    def test_plan_validity_ms(self, optimizer, hostile_threat):
        """Test plan validity is 500ms."""
        plan = optimizer.optimize([hostile_threat])
        
        assert plan.plan_validity_ms == 500
    
    def test_engagement_order_attributes(self, optimizer, hostile_threat):
        """Test engagement order has required attributes."""
        plan = optimizer.optimize([hostile_threat])
        
        order = plan.assignments[0]
        
        assert order.assignment_id is not None
        assert order.track_id is not None
        assert order.interceptor_id is not None
        assert order.status == EngagementStatus.ENGAGING
        assert order.eta_s > 0
        assert order.engagement_range_m > 0
    
    def test_removes_assignment_for_non_hostile(self, optimizer, hostile_threat):
        """Test assignment is removed when threat becomes benign."""
        # First assign the hostile
        optimizer.optimize([hostile_threat])
        
        assert len(optimizer.active_assignments) == 1
        
        # Now classify as benign
        benign_threat = ThreatScore(
            track_id=hostile_threat.track_id,
            timestamp=datetime.utcnow(),
            score=0.1,
            level=ThreatLevel.BENIGN,
            classification_label="BENIGN",
            swarm_probability=0.05,
            estimated_impact_time_s=None
        )
        
        optimizer.optimize([benign_threat])
        
        # Assignment should be removed
        assert len(optimizer.active_assignments) == 0
    
    def test_eta_from_threat(self, optimizer, hostile_threat):
        """Test engagement order uses ETA from threat."""
        plan = optimizer.optimize([hostile_threat])
        
        expected_eta = hostile_threat.estimated_impact_time_s or 30.0
        assert plan.assignments[0].eta_s == expected_eta
    
    def test_multiple_threats_sorted_by_score(self, optimizer):
        """Test multiple threats are sorted by score."""
        # Create threats with different scores
        threats = [
            ThreatScore(
                track_id="TRK-LOW",
                timestamp=datetime.utcnow(),
                score=0.3,
                level=ThreatLevel.CAUTION,
                classification_label="MONITORING",
                swarm_probability=0.2,
                estimated_impact_time_s=60.0
            ),
            ThreatScore(
                track_id="TRK-HIGH",
                timestamp=datetime.utcnow(),
                score=0.95,
                level=ThreatLevel.HOSTILE,
                classification_label="HOSTILE_FPV",
                swarm_probability=0.9,
                estimated_impact_time_s=15.0
            ),
            ThreatScore(
                track_id="TRK-MED",
                timestamp=datetime.utcnow(),
                score=0.6,
                level=ThreatLevel.CAUTION,
                classification_label="MONITORING",
                swarm_probability=0.4,
                estimated_impact_time_s=45.0
            ),
        ]
        
        plan = optimizer.optimize(threats)
        
        # Highest score should be assigned first
        assert plan.assignments[0].track_id == "TRK-HIGH"