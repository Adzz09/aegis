import pytest
import numpy as np
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.track_manager import TrackManager


class MockDetection:
    """Mock detection for testing."""
    def __init__(self, x, y, z, sensor_id="RADAR-01"):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z
        self.sensor_id = sensor_id


class TestTrackManager:
    """Tests for TrackManager class."""
    
    def test_track_manager_initialization(self):
        """TestTrackManager initializes with empty tracks."""
        tm = TrackManager()
        
        assert tm.tracks == {}
        assert tm.association_threshold == 20.0
    
    def test_creates_new_track(self):
        """Test creating a new track from detection."""
        tm = TrackManager()
        
        detection = MockDetection(100, 200, 50)
        tm.process_detection(detection)
        
        # Should have created a track
        assert len(tm.tracks) == 1
    
    def test_updates_existing_track(self):
        """Test updating existing track with new detection."""
        tm = TrackManager()
        
        # Create first detection
        detection1 = MockDetection(100, 200, 50)
        tm.process_detection(detection1)
        
        first_track_id = list(tm.tracks.keys())[0]
        
        # Update with nearby detection (should associate)
        detection2 = MockDetection(102, 198, 48)
        tm.process_detection(detection2)
        
        # Should still have only one track
        assert len(tm.tracks) == 1
        
        # Track should be updated (hits increased)
        assert tm.tracks[first_track_id]['hits'] >= 1
    
    def test_track_confirmed_after_hits(self):
        """Test track becomes confirmed after enough hits."""
        tm = TrackManager()
        
        # Create and update track multiple times
        for i in range(5):
            detection = MockDetection(100 + i, 200, 50)
            tm.process_detection(detection)
        
        track_id = list(tm.tracks.keys())[0]
        
        # After 3+ hits, should be confirmed
        assert tm.tracks[track_id]['status'] == 'confirmed'
    
    def test_cleanup_removes_stale_tracks(self):
        """Test cleanup removes tracks not updated in time."""
        tm = TrackManager()
        
        # Create a track
        detection = MockDetection(100, 200, 50)
        tm.process_detection(detection)
        
        assert len(tm.tracks) == 1
        
        # Manually set last_update to old time
        for track_data in tm.tracks.values():
            track_data['last_update'] = time.time() - 10.0  # 10 seconds ago
        
        # Run cleanup with 2 second timeout
        tm.cleanup_tracks(timeout=2.0)
        
        # Track should be removed
        assert len(tm.tracks) == 0
    
    def test_get_fused_tracks_only_confirmed(self):
        """Test get_fused_tracks only returns confirmed tracks."""
        tm = TrackManager()
        
        # Create confirmed track
        for i in range(5):
            detection = MockDetection(100 + i, 200, 50)
            tm.process_detection(detection)
        
        # Create unconfirmed track (only 1 hit)
        detection2 = MockDetection(500, 600, 100)
        tm.process_detection(detection2)
        
        fused = tm.get_fused_tracks()
        
        # Should only return the confirmed track
        assert len(fused) == 1
    
    def test_fused_track_has_position(self):
        """Test fused track has position data."""
        tm = TrackManager()
        
        # Create confirmed track
        for i in range(5):
            detection = MockDetection(100, 200, 50)
            tm.process_detection(detection)
        
        fused = tm.get_fused_tracks()
        
        assert len(fused) == 1
        track = fused[0]
        
        assert track.pos_x is not None
        assert track.pos_y is not None
        assert track.pos_z is not None
    
    def test_fused_track_has_velocity(self):
        """Test fused track has velocity data."""
        tm = TrackManager()
        
        # Create confirmed track
        for i in range(5):
            detection = MockDetection(100 + i*2, 200 + i, 50)
            tm.process_detection(detection)
        
        fused = tm.get_fused_tracks()
        
        assert len(fused) == 1
        track = fused[0]
        
        # Velocity should be non-zero (drones are moving)
        velocity = np.sqrt(track.vel_x**2 + track.vel_y**2 + track.vel_z**2)
        assert velocity > 0
    
    def test_multiple_sensor_contribution(self):
        """Test track can have multiple sensor contributions."""
        tm = TrackManager()
        
        # Detection from sensor 1
        det1 = MockDetection(100, 200, 50, sensor_id="RADAR-01")
        tm.process_detection(det1)
        
        # Detection from sensor 2
        det2 = MockDetection(102, 198, 48, sensor_id="OPT-01")
        tm.process_detection(det2)
        
        # Should still be one track
        assert len(tm.tracks) == 1
    
    def test_association_distance_threshold(self):
        """Test detections beyond threshold create new tracks."""
        tm = TrackManager()
        
        # Create first track
        det1 = MockDetection(100, 200, 50)
        tm.process_detection(det1)
        
        # Try detection far away (threshold is 20m)
        det2 = MockDetection(200, 300, 100)  # > 20m away
        tm.process_detection(det2)
        
        # Should have two tracks
        assert len(tm.tracks) == 2
    
    def test_track_id_format(self):
        """Test track IDs have correct format."""
        tm = TrackManager()
        
        detection = MockDetection(100, 200, 50)
        tm.process_detection(detection)
        
        track_id = list(tm.tracks.keys())[0]
        
        assert track_id.startswith("TRK-")
    
    def test_uncertainty_calculation(self):
        """Test position uncertainty is calculated."""
        tm = TrackManager()
        
        # Create confirmed track with some updates
        for i in range(3):
            detection = MockDetection(100 + np.random.randn()*5, 
                                   200 + np.random.randn()*5, 
                                   50 + np.random.randn()*2)
            tm.process_detection(detection)
        
        fused = tm.get_fused_tracks()
        
        if fused:
            assert fused[0].position_uncertainty_m is not None
            assert fused[0].position_uncertainty_m > 0