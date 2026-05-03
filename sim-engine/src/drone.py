import math
import uuid
import time
from enum import Enum

class DroneState(Enum):
    IDLE = "idle"
    NAVIGATING = "navigating"
    ATTACKING = "attacking"
    EVADING = "evading"
    DESTROYED = "destroyed"

class DroneAgent:
    def __init__(self, drone_id=None, start_pos=(0, 0, 0), target_pos=(0, 0, 0), speed=15.0):
        self.drone_id = drone_id or f"DRN-{str(uuid.uuid4())[:8].upper()}"
        self.pos_x, self.pos_y, self.pos_z = start_pos
        self.target_x, self.target_y, self.target_z = target_pos
        self.vel_x, self.vel_y, self.vel_z = 0, 0, 0
        self.speed = speed
        self.state = DroneState.NAVIGATING
        self.last_update = time.time()

    def update(self, dt):
        if self.state == DroneState.DESTROYED:
            return

        # Simple linear movement towards target
        dx = self.target_x - self.pos_x
        dy = self.target_y - self.pos_y
        dz = self.target_z - self.pos_z
        dist = math.sqrt(dx**2 + dy**2 + dz**2)

        if dist < 5:
            self.state = DroneState.ATTACKING
            # Small jitter when attacking
            self.vel_x = (math.sin(time.time()) * 2)
            self.vel_y = (math.cos(time.time()) * 2)
            self.vel_z = 0
        else:
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed
            self.vel_z = (dz / dist) * self.speed

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        self.pos_z += self.vel_z * dt
        self.last_update = time.time()

    def get_state(self):
        return {
            "drone_id": self.drone_id,
            "pos": (self.pos_x, self.pos_y, self.pos_z),
            "vel": (self.vel_x, self.vel_y, self.vel_z),
            "state": self.state.value
        }
