import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.drone import DroneAgent, DroneState


class TestDroneAgent:
    """Tests for DroneAgent class."""
    
    def test_drone_initialization(self):
        """Test that a drone is initialized with correct defaults."""
        drone = DroneAgent(
            drone_id="TEST-001",
            start_pos=(0, 1000, 100),
            target_pos=(0, 0, 0),
            speed=20.0
        )
        
        assert drone.drone_id == "TEST-001"
        assert drone.pos_x == 0
        assert drone.pos_y == 1000
        assert drone.pos_z == 100
        assert drone.speed == 20.0
        assert drone.state == DroneState.NAVIGATING
    
    def test_drone_id_generation(self):
        """Test that drone ID is auto-generated when not provided."""
        drone = DroneAgent(start_pos=(0, 1000, 100), target_pos=(0, 0, 0))
        
        assert drone.drone_id is not None
        assert drone.drone_id.startswith("DRN-")
    
    def test_drone_update_navigating(self):
        """Test drone moves toward target when in NAVIGATING state."""
        drone = DroneAgent(
            start_pos=(0, 1000, 100),
            target_pos=(0, 0, 0),
            speed=10.0
        )
        
        # Update with 1 second delta
        drone.update(1.0)
        
        # Should have moved closer to target (y should decrease)
        assert drone.pos_y < 1000
        assert drone.state == DroneState.NAVIGATING
    
    def test_drone_reaches_target(self):
        """Test drone switches to ATTACKING state when reaching target."""
        drone = DroneAgent(
            start_pos=(0, 10, 0),  # Very close to target
            target_pos=(0, 0, 0),
            speed=10.0
        )
        
        # Update multiple times to reach target
        for _ in range(10):
            drone.update(0.1)
        
        assert drone.state == DroneState.ATTACKING
    
    def test_drone_destroyed_state(self):
        """Test drone doesn't move when destroyed."""
        drone = DroneAgent(
            start_pos=(0, 1000, 100),
            target_pos=(0, 0, 0),
            speed=10.0
        )
        
        # Destroy the drone
        drone.state = DroneState.DESTROYED
        
        # Update should not change position
        original_x = drone.pos_x
        original_y = drone.pos_y
        drone.update(1.0)
        
        assert drone.pos_x == original_x
        assert drone.pos_y == original_y
    
    def test_get_state_returns_correct_dict(self):
        """Test get_state method returns expected structure."""
        drone = DroneAgent(
            drone_id="TEST-002",
            start_pos=(100, 200, 50),
            target_pos=(0, 0, 0),
            speed=15.0
        )
        
        state = drone.get_state()
        
        assert state["drone_id"] == "TEST-002"
        assert state["pos"] == (100, 200, 50)
        assert "vel" in state
        assert state["state"] == "navigating"
    
    def test_velocity_increases_with_speed(self):
        """Test higher speed results in higher velocity."""
        slow_drone = DroneAgent(
            start_pos=(0, 1000, 0),
            target_pos=(0, 0, 0),
            speed=5.0
        )
        
        fast_drone = DroneAgent(
            start_pos=(0, 1000, 0),
            target_pos=(0, 0, 0),
            speed=25.0
        )
        
        slow_drone.update(1.0)
        fast_drone.update(1.0)
        
        # Fast drone should cover more distance
        assert fast_drone.pos_y < slow_drone.pos_y