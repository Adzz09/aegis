"""
Non-Kinetic Countermeasures Controller

Controls aerosol dispensers, streamer launchers, and EW platforms.
Coordinates with the optimizer to deploy appropriate countermeasures.
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from confluent_kafka import Consumer, Producer
from shared.schemas.assignment import AssignmentPlan

from .payloads import (
    AerosolDispenser, AerosolType, StreamerLauncher, StreamerType,
    EWPlatform, EWType, ECMStatus, CountermeasureRequest
)


class NonKineticController:
    """
    Controller for non-kinetic countermeasures.
    
    Monitors threats and deploys:
    - Aerosol dispensers (area denial)
    - Streamer launchers (entanglement)
    - EW/jammers (electronic disruption)
    """
    
    def __init__(self, kafka_brokers: str = "localhost:19092"):
        self.kafka_brokers = kafka_brokers
        
        # Initialize aerosol dispensers
        self.aerosol_dispensers = {
            "AERO-01": AerosolDispenser(
                dispenser_id="AERO-01",
                location_x=0, location_y=0, location_z=10,
                aerosol_type=AerosolType.SILICON,
                capacity_uses=100,
                spray_radius_m=50,
                effectiveness=0.8
            ),
            "AERO-02": AerosolDispenser(
                dispenser_id="AERO-02",
                location_x=500, location_y=500, location_z=10,
                aerosol_type=AerosolType.DRY_POWDER,
                capacity_uses=100,
                spray_radius_m=75,
                effectiveness=0.7
            ),
        }
        
        # Initialize streamer launchers
        self.streamer_launchers = {
            "STREAM-01": StreamerLauncher(
                launcher_id="STREAM-01",
                location_x=-200, location_y=200, location_z=5,
                streamer_type=StreamerType.ADHESIVE,
                barrel_count=8,
                effective_range_m=80
            ),
            "STREAM-02": StreamerLauncher(
                launcher_id="STREAM-02",
                location_x=200, location_y=200, location_z=5,
                streamer_type=StreamerType.KITE_STRING,
                barrel_count=8,
                effective_range_m=100
            ),
        }
        
        # Initialize EW platforms
        self.ew_platforms = {
            "EW-01": EWPlatform(
                platform_id="EW-01",
                location_x=0, location_y=0, location_z=15,
                ew_type=EWType.SWEEP,
                freq_start_mhz=2400,
                freq_end_mhz=2500,
                max_power_dbm=30
            ),
            "EW-02": EWPlatform(
                platform_id="EW-02",
                location_x=300, location_y=-300, location_z=15,
                ew_type=EWType.NOISE,
                freq_start_mhz=5725,
                freq_end_mhz=5850,
                max_power_dbm=30
            ),
        }
        
        # Track active deployments
        self.active_deployments: Dict[str, CountermeasureRequest] = {}
        
    def evaluate_countermeasures(
        self, 
        threats: List[dict],
        zone_center_x: float = 0,
        zone_center_y: float = 0,
        zone_radius: float = 500
    ) -> List[CountermeasureRequest]:
        """
        Evaluate threats and create countermeasure requests.
        Returns list of deployments to execute.
        """
        deployments = []
        
        if not threats:
            return deployments
            
        # Count high-threat threats in each category
        critical_count = sum(1 for t in threats if t.get('score', 0) > 0.9)
        hostile_count = sum(1 for t in threats if 0.5 < t.get('score', 0) <= 0.9)
        
        # Decision logic for countermeasures
        
        # High-density swarm approaching - use aerosol area denial
        if critical_count >= 10 and hostile_count >= 20:
            # Find best aerosol dispenser
            for disp in self.aerosol_dispensers.values():
                if disp.current_uses < disp.capacity_uses:
                    request = CountermeasureRequest(
                        request_id=f"CM-{uuid.uuid4().hex[:6]}",
                        countermeasure_type="aerosol",
                        target_x=zone_center_x,
                        target_y=zone_center_y,
                        radius_m=disp.spray_radius_m,
                        duration_s=30,
                        intensity=min(10, critical_count // 5 + 5)
                    )
                    deployments.append(request)
                    disp.current_uses += request.duration_s // 5
                    break
        
        # Medium swarm - use streamer launchers
        elif 3 <= critical_count < 10 or hostile_count >= 15:
            for launch in self.streamer_launchers.values():
                if launch.current_load < launch.barrel_count * launch.capacity_per_barrel:
                    request = CountermeasureRequest(
                        request_id=f"CM-{uuid.uuid4().hex[:6]}",
                        countermeasure_type="streamer",
                        target_x=zone_center_x + (hash(str(threats[0])) % 200 - 100),
                        target_y=zone_center_y + (hash(str(threats[1])) % 200 - 100),
                        radius_m=launch.effective_range_m,
                        duration_s=15,
                        intensity=min(10, hostile_count // 3 + 3)
                    )
                    deployments.append(request)
                    launch.current_load += len(threats) // 5 + 1
                    break
        
        # Scattered threats - use targeted EW
        elif hostile_count >= 5:
            for ew in self.ew_platforms.values():
                if ew.status == ECMStatus.IDLE:
                    request = CountermeasureRequest(
                        request_id=f"CM-{uuid.uuid4().hex[:6]}",
                        countermeasure_type="ew",
                        target_x=zone_center_x,
                        target_y=zone_center_y,
                        radius_m=200,
                        duration_s=20,
                        intensity=min(10, hostile_count // 2 + 2)
                    )
                    deployments.append(request)
                    ew.status = ECMStatus.JAMMING
                    break
        
        return deployments
    
    def execute_aerosol(self, request: CountermeasureRequest) -> dict:
        """Execute aerosol dispersion."""
        dispenser = self.aerosol_dispensers.get("AERO-01")
        if not dispenser:
            return {"status": "failed", "reason": "no_dispenser"}
        
        # Simulate dispersion
        drones_affected = int(request.radius_m / 10 * dispenser.effectiveness)
        
        return {
            "status": "dispensing",
            "dispenser_id": dispenser.dispenser_id,
            "aerosol_type": dispenser.aerosol_type.value,
            "target_x": request.target_x,
            "target_y": request.target_y,
            "radius_m": request.radius_m,
            "Duration_s": request.duration_s,
            "drones_affected": drones_affected
        }
    
    def execute_streamer(self, request: CountermeasureRequest) -> dict:
        """Execute streamer launch."""
        launcher = self.streamer_launchers.get("STREAM-01")
        if not launcher:
            return {"status": "failed", "reason": "no_launcher"}
        
        # Simulate streamer launch
        drones_affected = launcher.barrel_count * launcher.capacity_per_barrel // 2
        
        return {
            "status": "firing",
            "launcher_id": launcher.launcher_id,
            "streamer_type": launcher.streamer_type.value,
            "target_x": request.target_x,
            "target_y": request.target_y,
            "barrels_fired": min(launcher.barrel_count, request.intensity),
            "drones_affected": drones_affected
        }
    
    def execute_ew(self, request: CountermeasureRequest) -> dict:
        """Execute EW jamming."""
        platform = self.ew_platforms.get("EW-01")
        if not platform:
            return {"status": "failed", "reason": "no_platform"}
        
        return {
            "status": "jamming",
            "platform_id": platform.platform_id,
            "freq_range_mhz": f"{platform.freq_start_mhz}-{platform.freq_end_mhz}",
            "target_zone": f"({request.target_x}, {request.target_y})",
            "radius_m": request.radius_m,
            "intensity": request.intensity,
            "drones_affected": request.intensity * 5
        }
    
    def get_status(self) -> dict:
        """Get current status of all platforms."""
        return {
            "aerosol_dispensers": [
                {
                    "id": d.dispenser_id,
                    "type": d.aerosol_type.value,
                    "location": (d.location_x, d.location_y),
                    "remaining_uses": d.capacity_uses - d.current_uses,
                    "status": "ready" if d.current_uses < d.capacity_uses else "empty"
                }
                for d in self.aerosol_dispensers.values()
            ],
            "streamer_launchers": [
                {
                    "id": l.launcher_id,
                    "type": l.streamer_type.value,
                    "location": (l.location_x, l.location_y),
                    "remaining": l.barrel_count * l.capacity_per_barrel - l.current_load,
                    "status": "ready" if l.current_load < l.barrel_count * l.capacity_per_barrel else "empty"
                }
                for l in self.streamer_launchers.values()
            ],
            "ew_platforms": [
                {
                    "id": p.platform_id,
                    "type": p.ew_type.value,
                    "location": (p.location_x, p.location_y),
                    "frequency_mhz": f"{p.freq_start_mhz}-{p.freq_end_mhz}",
                    "status": p.status.value
                }
                for p in self.ew_platforms.values()
            ]
        }


async def main():
    """Main entry point for non-kinetic controller."""
    controller = NonKineticController()
    
    print("Non-Kinetic Countermeasures Controller starting...")
    print(f"Initialized: {len(controller.aerosol_dispensers)} aerosol dispensers")
    print(f"Initialized: {len(controller.streamer_launchers)} streamer launchers")
    print(f"Initialized: {len(controller.ew_platforms)} EW platforms")
    
    # Print status
    status = controller.get_status()
    print("\nPlatform Status:")
    for platform_type, platforms in status.items():
        print(f"  {platform_type}:")
        for p in platforms:
            print(f"    - {p['id']}: {p['status']}")


if __name__ == "__main__":
    asyncio.run(main())