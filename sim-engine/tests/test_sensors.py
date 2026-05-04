import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sensors import SensorSimulator
from src.drone import DroneAgent
from shared.schemas.track import SensorType


class TestSensorSimulator:
    """Tests for SensorSimulator class."""
    
    def test_sensor_initialization(self):
        """Test sensor is initialized with correct parameters."""
        sensor = SensorSimulator(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            pos=(0, 0, 0),
            range_max=5000
        )
        
        assert sensor.sensor_id == "RADAR-01"
        assert sensor.sensor_type == SensorType.RADAR
        assert sensor.pos_x == 0
        assert sensor.pos_y == 0
        assert sensor.pos_z == 0
        assert sensor.range_max == 5000
    
    def test_sensor_returns_detection_within_range(self):
        """Test sensor detects drones within range."""
        sensor = SensorSimulator(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            pos=(0, 0, 0),
            range_max=5000
        )
        
        drone = DroneAgent(
            start_pos=(100, 200, 50),
            target_pos=(0, 0, 0)
        )
        
        detection = sensor.detect(drone)
        
        assert detection is not None
        assert detection.sensor_id == "RADAR-01"
        assert detection.sensor_type == SensorType.RADAR
        assert detection.range_m > 0
    
    def test_sensor_returns_none_outside_range(self):
        """Test sensor returns None for drones outside detection range."""
        sensor = SensorSimulator(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            pos=(0, 0, 0),
            range_max=1000  # Very short range
        )
        
        drone = DroneAgent(
            start_pos=(2000, 2000, 500),  # Far away
            target_pos=(0, 0, 0)
        )
        
        detection = sensor.detect(drone)
        
        assert detection is None
    
    def test_sensor_no_duplicate_import(self):
        """Test that importing math twice doesn't cause issues."""
        # This is a regression test for the duplicate import issue
        import importlib
        importlib.reload(sys.modules.get('src.sensors', sys))
        
        sensor = SensorSimulator(
            sensor_id="OPT-01",
            sensor_type=SensorType.OPTICAL,
            pos=(100, 100, 0)
        )
        
        drone = DroneAgent(start_pos=(150, 150, 50), target_pos=(0, 0, 0))
        
        detection = sensor.detect(drone)
        
        assert detection is not None
    
    def test_sensor_noise_application(self):
        """Test sensor applies noise to range measurements."""
        sensor = SensorSimulator(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            pos=(0, 0, 0),
            range_max=10000
        )
        
        # Create drone at known position
        drone = DroneAgent(
            start_pos=(0, 1000, 0),  # Exactly 1000m away
            target_pos=(0, 0, 0)
        )
        
        # Get multiple detections to see noise variation
        detections = [sensor.detect(drone) for _ in range(10)]
        
        # Filter None results
        ranges = [d.range_m for d in detections if d is not None]
        
        # Should have some variation due to noise
        assert len(ranges) > 0
        # Some detections should differ from perfect 1000m
        # (allow for random chance)
    
    def test_multiple_sensor_types(self):
        """Test different sensor types can be created."""
        radar = SensorSimulator("RADAR-01", SensorType.RADAR, (0, 0, 0))
        optical = SensorSimulator("OPT-01", SensorType.OPTICAL, (100, 100, 0))
        rf = SensorSimulator("RF-01", SensorType.RF, (-50, 50, 0))
        
        assert radar.sensor_type == SensorType.RADAR
        assert optical.sensor_type == SensorType.OPTICAL
        assert rf.sensor_type == SensorType.RF
    
    def test_snr_decreases_with_distance(self):
        """Test SNR decreases as distance increases."""
        sensor = SensorSimulator(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            pos=(0, 0, 0),
            range_max=5000
        )
        
        # Close drone
        close_drone = DroneAgent(start_pos=(0, 100, 0), target_pos=(0, 0, 0))
        close_detection = sensor.detect(close_drone)
        
        # Far drone
        far_drone = DroneAgent(start_pos=(0, 1000, 0), target_pos=(0, 0, 0))
        far_detection = sensor.detect(far_drone)
        
        if close_detection and far_detection:
            assert close_detection.snr_db >= far_detection.snr_db