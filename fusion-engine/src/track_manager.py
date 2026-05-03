import time
import uuid
import numpy as np
from datetime import datetime
from .kalman import DroneKalmanFilter
from shared.schemas.track import FusedTrack

class TrackManager:
    def __init__(self):
        self.tracks = {} # track_id -> {filter, last_update, status}
        self.association_threshold = 20.0 # meters

    def process_detection(self, detection):
        best_track_id = None
        min_dist = float('inf')

        # Simple Nearest Neighbor Association
        for track_id, track_data in self.tracks.items():
            kf = track_data['filter']
            pos, _ = kf.get_state()
            dist = np.linalg.norm(np.array([detection.pos_x, detection.pos_y, detection.pos_z]) - pos[:3].flatten())
            
            if dist < self.association_threshold and dist < min_dist:
                min_dist = dist
                best_track_id = track_id

        if best_track_id:
            # Update existing track
            self.tracks[best_track_id]['filter'].update([detection.pos_x, detection.pos_y, detection.pos_z])
            self.tracks[best_track_id]['last_update'] = time.time()
            self.tracks[best_track_id]['hits'] += 1
            if self.tracks[best_track_id]['hits'] >= 3:
                self.tracks[best_track_id]['status'] = 'confirmed'
        else:
            # Create new track
            new_id = f"TRK-{str(uuid.uuid4())[:6].upper()}"
            kf = DroneKalmanFilter()
            kf.kf.x[:3] = np.array([[detection.pos_x], [detection.pos_y], [detection.pos_z]])
            self.tracks[new_id] = {
                'filter': kf,
                'last_update': time.time(),
                'status': 'tentative',
                'hits': 1
            }

    def cleanup_tracks(self, timeout=2.0):
        now = time.time()
        to_delete = [tid for tid, data in self.tracks.items() if now - data['last_update'] > timeout]
        for tid in to_delete:
            del self.tracks[tid]

    def get_fused_tracks(self):
        fused = []
        for tid, data in self.tracks.items():
            if data['status'] == 'confirmed':
                x_raw, P = data['filter'].get_state()
                x = x_raw.flatten()
                fused.append(FusedTrack(
                    track_id=tid,
                    timestamp=datetime.utcnow(),
                    pos_x=float(x[0]),
                    pos_y=float(x[1]),
                    pos_z=float(x[2]),
                    vel_x=float(x[3]),
                    vel_y=float(x[4]),
                    vel_z=float(x[5]),
                    position_uncertainty_m=float(np.trace(P[:3, :3])**0.5),
                    velocity_uncertainty_mps=float(np.trace(P[3:, 3:])**0.5),
                    is_confirmed=True
                ))
        return fused
