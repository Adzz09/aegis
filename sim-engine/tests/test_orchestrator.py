import pytest
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import SwarmOrchestrator
from src.drone import DroneState
from shared.schemas.track import SensorType


class TestSwarmOrchestrator:
    """Tests for SwarmOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator creates correct number of drones."""
        orchestrator = SwarmOrchestrator(drone_count=10)
        
        assert len(orchestrator.drones) == 10
        assert len(orchestrator.sensors) == 2  # RADAR + OPTICAL
    
    def test_orchestrator_sensors_created(self):
        """Test orchestrator creates expected sensor types."""
        orchestrator = SwarmOrchestrator(drone_count=5)
        
        sensor_types = [s.sensor_type for s in orchestrator.sensors]
        
        assert SensorType.RADAR in sensor_types
        assert SensorType.OPTICAL in sensor_types
    
    def test_trigger_scenario(self):
        """Test scenario trigger creates new drones."""
        orchestrator = SwarmOrchestrator(drone_count=5)
        
        assert len(orchestrator.drones) == 5
        
        orchestrator.trigger_scenario(drone_count=50)
        
        assert len(orchestrator.drones) == 50
    
    def test_trigger_scenario_message(self):
        """Test scenario trigger prints confirmation message."""
        orchestrator = SwarmOrchestrator(drone_count=5)
        
        # Should not raise exception
        orchestrator.trigger_scenario(drone_count=25)
        
        # Drones should be created with varied speeds for FPV drones
        speeds = [d.speed for d in orchestrator.drones]
        assert all(15 <= s <= 35 for s in speeds)
    
    def test_orchestrator_not_running_initially(self):
        """Test orchestrator is not running on initialization."""
        orchestrator = SwarmOrchestrator(drone_count=5)
        
        assert orchestrator.running is False
    
    @pytest.mark.asyncio
    async def test_run_produces_detections(self):
        """Test orchestrator run loop produces sensor detections."""
        orchestrator = SwarmOrchestrator(drone_count=2)
        
        detections_result = []
        
        async def capture_callback(detections):
            detections_result.extend(detections)
        
        # Run for a short time
        orchestrator.running = True
        
        # Patch sleep to avoid actual waiting
        original_sleep = asyncio.sleep
        async def quick_sleep(duration):
            orchestrator.running = False
            return original_sleep(0)
        
        asyncio.sleep = quick_sleep
        
        try:
            await orchestrator.run(capture_callback)
        finally:
            asyncio.sleep = original_sleep
        
        # Should have produced some detections
        assert len(detections_result) > 0
    
    def test_drone_positions_initialized_correctly(self):
        """Test drones are initialized at varied positions."""
        orchestrator = SwarmOrchestrator(drone_count=20)
        
        positions = [(d.pos_x, d.pos_y, d.pos_z) for d in orchestrator.drones]
        
        # All drones should be far from target (target is at 0,0,0)
        for pos in positions:
            # Drones start at y between 2000-3000
            assert 2000 <= pos[1] <= 3000
    
    def test_sensors_have_positions(self):
        """Test sensors have defined positions."""
        orchestrator = SwarmOrchestrator(drone_count=5)
        
        for sensor in orchestrator.sensors:
            assert sensor.pos_x is not None
            assert sensor.pos_y is not None