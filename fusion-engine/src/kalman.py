import numpy as np
from filterpy.kalman import KalmanFilter

class DroneKalmanFilter:
    def __init__(self, dt=0.1):
        # 6 states: [x, y, z, vx, vy, vz]
        self.kf = KalmanFilter(dim_x=6, dim_z=3)
        
        # State transition matrix F
        self.kf.F = np.array([
            [1, 0, 0, dt, 0, 0],
            [0, 1, 0, 0, dt, 0],
            [0, 0, 1, 0, 0, dt],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]
        ])
        
        # Measurement matrix H
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ])
        
        # Process noise Q
        self.kf.Q = np.eye(6) * 0.1
        
        # Measurement noise R
        self.kf.R = np.eye(3) * 5.0
        
        # Covariance matrix P
        self.kf.P *= 100.0
        
    def predict(self):
        self.kf.predict()
        
    def update(self, z):
        self.kf.update(z)
        
    def get_state(self):
        return self.kf.x, self.kf.P
