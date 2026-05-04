import pytest
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kalman import DroneKalmanFilter


class TestDroneKalmanFilter:
    """Tests for DroneKalmanFilter class."""
    
    def test_kalman_initialization(self):
        """Test Kalman filter initializes with correct state dimension."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Should have 6 states: [x, y, z, vx, vy, vz]
        assert kf.kf.dim_x == 6
        assert kf.kf.dim_z == 3
    
    def test_kalman_state_transition_matrix(self):
        """Test state transition matrix F is set correctly."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Check diagonal elements for position updates
        assert kf.kf.F[0, 0] == 1  # x -> x
        assert kf.kf.F[0, 3] == 0.1  # x += vx * dt
        assert kf.kf.F[1, 1] == 1  # y -> y
        assert kf.kf.F[2, 2] == 1  # z -> z
        assert kf.kf.F[3, 3] == 1  # vx stays
        assert kf.kf.F[4, 4] == 1  # vy stays
        assert kf.kf.F[5, 5] == 1  # vz stays
    
    def test_kalman_measurement_matrix(self):
        """Test measurement matrix H is correct."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Should only observe position, not velocity
        assert kf.kf.H.shape == (3, 6)
        assert kf.kf.H[0, 0] == 1  # observe x
        assert kf.kf.H[1, 1] == 1  # observe y
        assert kf.kf.H[2, 2] == 1  # observe z
        assert kf.kf.H[0, 3] == 0  # don't observe vx
    
    def test_kalman_has_process_noise(self):
        """Test process noise Q is set."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Q should be non-zero
        assert np.sum(kf.kf.Q) > 0
        assert kf.kf.Q.shape == (6, 6)
    
    def test_kalman_has_measurement_noise(self):
        """Test measurement noise R is set."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # R should be non-zero
        assert np.sum(kf.kf.R) > 0
        assert kf.kf.R.shape == (3, 3)
    
    def test_kalman_update_changes_state(self):
        """Test update method changes filter state."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Initial state should be near zero
        x_before = kf.kf.x.copy()
        
        # Update with measurement
        kf.update([100, 200, 50])
        
        x_after = kf.kf.x
        
        # State should have changed
        assert not np.array_equal(x_before, x_after)
    
    def test_kalman_predict_changes_covariance(self):
        """Test predict method changes covariance."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Get initial covariance trace
        P_before = np.trace(kf.kf.P)
        
        kf.predict()
        
        P_after = np.trace(kf.kf.P)
        
        # Covariance should increase (uncertainty grows without measurement)
        assert P_after >= P_before
    
    def test_get_state_returns_x_and_p(self):
        """Test get_state returns state and covariance."""
        kf = DroneKalmanFilter(dt=0.1)
        
        x, P = kf.get_state()
        
        assert x is not None
        assert P is not None
        assert x.shape == (6, 1)
        assert P.shape == (6, 6)
    
    def test_kalman_filters_noisy_measurements(self):
        """Test Kalman filter smooths noisy measurements."""
        kf = DroneKalmanFilter(dt=0.1)
        
        # Set initial state
        kf.kf.x[:3] = np.array([[100], [200], [50]])
        
        # Update with noisy measurements
        measurements = [
            [105, 195, 52],
            [98, 205, 48],
            [102, 198, 51],
            [100, 200, 50],
        ]
        
        for z in measurements:
            kf.update(z)
        
        x, _ = kf.get_state()
        x_final = x.flatten()
        
        # Should be close to true position (100, 200, 50)
        assert abs(x_final[0] - 100) < 5
        assert abs(x_final[1] - 200) < 5
        assert abs(x_final[2] - 50) < 5
    
    def test_kalman_dt_parameter(self):
        """Test DT parameter affects state transition."""
        kf_fast = DroneKalmanFilter(dt=0.5)
        kf_slow = DroneKalmanFilter(dt=0.1)
        
        # FAST should have larger position update per step
        assert kf_fast.kf.F[0, 3] == 0.5  # dt = 0.5
        assert kf_slow.kf.F[0, 3] == 0.1  # dt = 0.1