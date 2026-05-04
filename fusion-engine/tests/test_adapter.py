import pytest
import sys
import os
import math
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapter import SensorAdapter, DetectionEvent
from shared.schemas.track import SensorEvent, SensorType


class TestSensorAdapter:
    """Tests for SensorAdapter class."""
    
    def test_adapter_initialization(self):
        """Test adapter initializes correctly."""
        adapter = SensorAdapter()
        
        assert adapter is not None
    
    def test_normalize_converts_polar_to_cartesian(self):
        """Test polar to Cartesian conversion."""
        adapter = SensorAdapter()
        
        # Create sensor event at 100m, 0 degrees azimuth, 0 elevation
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # At azimuth 90, elevation 0:
        # x = r * cos(el) * sin(az) = 100 * 1 * 1 = 100
        # y = r * cos(el) * cos(az) = 100 * 1 * 0 = 0
        # z = r * sin(el) = 100 * 0 = 0
        assert abs(result.pos_x - 100) < 0.001  # Allow floating point tolerance
        assert abs(result.pos_y - 0) < 0.001
        assert abs(result.pos_z - 0) < 0.001
    
    def test_normalize_handles_elevation(self):
        """Test conversion handles non-zero elevation."""
        adapter = SensorAdapter()
        
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=45,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # At 45 degrees elevation, z should be positive
        assert result.pos_z > 0
    
    def test_normalize_default_azimuth(self):
        """Test default azimuth of 0 for None."""
        adapter = SensorAdapter()
        
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=0,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # At azimuth 0:
        # x = 100 * 1 * 0 = 0
        # y = 100 * 1 * 1 = 100
        assert result.pos_x == 0
        assert result.pos_y == 100
    
    def test_normalize_uses_sensor_position(self):
        """Test sensor position is applied."""
        adapter = SensorAdapter()
        
        # Event from RADAR-01 at position (0, 0, 0)
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # Should be at x=100 (sensor at 0,0,0 adds nothing)
        assert result.pos_x == 100
    
    def test_normalize_optional_elevation(self):
        """Test None elevation defaults to 0."""
        adapter = SensorAdapter()
        
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=45,
            elevation_deg=None,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # Should not raise, elevation should default to 0
        assert result.pos_z == 0
    
    def test_detection_event_attributes(self):
        """Test DetectionEvent has expected attributes."""
        adapter = SensorAdapter()
        
        event = SensorEvent(
            sensor_id="RADAR-01",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        assert hasattr(result, 'track_id')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'pos_x')
        assert hasattr(result, 'pos_y')
        assert hasattr(result, 'pos_z')
        assert hasattr(result, 'sensor_id')
    
    def test_different_sensor_positions(self):
        """Test different sensors have different positions."""
        adapter = SensorAdapter()
        
        # Event from OPT-01 at (100, 100, 0)
        event = SensorEvent(
            sensor_id="OPT-01",
            sensor_type=SensorType.OPTICAL,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # Sensor at (100, 100, 0) + detection at (100, 0, 0) = (200, 100, 0)
        assert result.pos_x == 200
        assert result.pos_y == 100
    
    def test_rf_sensor_position(self):
        """Test RF sensor position."""
        adapter = SensorAdapter()
        
        event = SensorEvent(
            sensor_id="RF-01",
            sensor_type=SensorType.RF,
            timestamp=datetime.utcnow(),
            azimuth_deg=90,
            elevation_deg=0,
            range_m=100,
            snr_db=20
        )
        
        result = adapter.normalize(event)
        
        # Sensor at (-50, 50, 0) + detection at (100, 0, 0) = (50, 50, 0)
        assert abs(result.pos_x - 50) < 0.001
        assert abs(result.pos_y - 50) < 0.001