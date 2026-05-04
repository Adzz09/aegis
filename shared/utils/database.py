"""
TimescaleDB persistence utilities.

Provides database connection and persistence functions for sensor events,
fused tracks, threat scores, and assignments.
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/postgres"
)


def get_database_url() -> str:
    """Get database URL from environment."""
    return DATABASE_URL


class TimescaleDB:
    """TimescaleDB connection and query helpers."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or get_database_url()
        self.conn = None
        self._pool = None
    
    async def connect(self) -> None:
        """Connect to the database."""
        try:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5
            )
            print(f"Connected to TimescaleDB: {self.database_url}")
        except Exception as e:
            print(f"Warning: Could not connect to TimescaleDB: {e}")
            self._pool = None
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def execute(self, query: str, *args) -> Any:
        """Execute a query."""
        if not self._pool:
            return None
        
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Execute a query and fetch results."""
        if not self._pool:
            return []
        
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Execute a query and fetch one row."""
        if not self._pool:
            return None
        
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


# Singleton instance
_db_instance: Optional[TimescaleDB] = None


async def get_db() -> TimescaleDB:
    """Get the database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = TimescaleDB()
        await _db_instance.connect()
    return _db_instance


# SQL for hypertables (run these on startup)
HYPERTABLE_CREATE_SQL = [
    """
    CREATE TABLE IF NOT EXISTS sensor_events (
        id BIGSERIAL,
        sensor_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        azimuth_deg DOUBLE PRECISION,
        elevation_deg DOUBLE PRECISION,
        range_m DOUBLE PRECISION,
        snr_db DOUBLE PRECISION,
        raw_data JSONB,
        time TIMESTAMPTZ NOT NULL
    );
    """,
    """
    SELECT create_hypertable('sensor_events', 'time', 
        if_not_exists => TRUE, 
        migrate_data => TRUE);
    """,
    """
    CREATE TABLE IF NOT EXISTS fused_tracks (
        id BIGSERIAL,
        track_id TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        pos_x DOUBLE PRECISION,
        pos_y DOUBLE PRECISION,
        pos_z DOUBLE PRECISION,
        vel_x DOUBLE PRECISION,
        vel_y DOUBLE PRECISION,
        vel_z DOUBLE PRECISION,
        position_uncertainty_m DOUBLE PRECISION,
        velocity_uncertainty_mps DOUBLE PRECISION,
        classification TEXT,
        threat_score DOUBLE PRECISION,
        threat_level TEXT,
        is_confirmed BOOLEAN,
        source_sensors JSONB,
        time TIMESTAMPTZ NOT NULL
    );
    """,
    """
    SELECT create_hypertable('fused_tracks', 'time',
        if_not_exists => TRUE,
        migrate_data => TRUE);
    """,
    """
    CREATE TABLE IF NOT EXISTS threat_scores (
        id BIGSERIAL,
        track_id TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        score DOUBLE PRECISION NOT NULL,
        level TEXT NOT NULL,
        classification_label TEXT,
        swarm_probability DOUBLE PRECISION,
        estimated_impact_time_s DOUBLE PRECISION,
        confidence DOUBLE PRECISION,
        time TIMESTAMPTZ NOT NULL
    );
    """,
    """
    SELECT create_hypertable('threat_scores', 'time',
        if_not_exists => TRUE,
        migrate_data => TRUE);
    """,
    """
    CREATE TABLE IF NOT EXISTS assignments (
        id BIGSERIAL,
        plan_id TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        assignments JSONB,
        unassigned_threats JSONB,
        plan_validity_ms INTEGER,
        time TIMESTAMPTZ NOT NULL
    );
    """,
    """
    SELECT create_hypertable('assignments', 'time',
        if_not_exists => TRUE,
        migrate_data => TRUE);
    """,
    """
    CREATE TABLE IF NOT EXISTS system_health (
        id BIGSERIAL,
        module_id TEXT NOT NULL,
        status TEXT NOT NULL,
        latency_ms DOUBLE PRECISION,
        metrics JSONB,
        time TIMESTAMPTZ NOT NULL
    );
    """,
    """
    SELECT create_hypertable('system_health', 'time',
        if_not_exists => TRUE,
        migrate_data => TRUE);
    """,
]


async def init_database() -> None:
    """Initialize the database with hypertables."""
    db = await get_db()
    
    for sql in HYPERTABLE_CREATE_SQL:
        if sql.strip():
            try:
                await db.execute(sql)
            except Exception as e:
                # Table might already exist - that's ok
                print(f"Database init: {e}")
    
    print("Database initialized with hypertables.")


async def write_sensor_event(
    sensor_id: str,
    sensor_type: str,
    timestamp: datetime,
    azimuth_deg: float,
    elevation_deg: Optional[float],
    range_m: float,
    snr_db: float,
    raw_data: Optional[Dict] = None
) -> None:
    """Write a sensor event to the database."""
    db = await get_db()
    
    query = """
        INSERT INTO sensor_events 
        (sensor_id, sensor_type, timestamp, azimuth_deg, elevation_deg, range_m, snr_db, raw_data, time)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
    """
    
    try:
        await db.execute(
            query, 
            sensor_id, 
            sensor_type, 
            timestamp, 
            azimuth_deg, 
            elevation_deg, 
            range_m, 
            snr_db,
            json.dumps(raw_data) if raw_data else None
        )
    except Exception as e:
        print(f"Error writing sensor event: {e}")


async def write_fused_track(track) -> None:
    """Write a fused track to the database."""
    db = await get_db()
    
    query = """
        INSERT INTO fused_tracks 
        (track_id, timestamp, pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, 
         position_uncertainty_m, velocity_uncertainty_mps, classification, threat_score, 
         threat_level, is_confirmed, source_sensors, time)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW())
    """
    
    try:
        await db.execute(
            query,
            track.track_id,
            track.timestamp,
            track.pos_x,
            track.pos_y,
            track.pos_z,
            track.vel_x,
            track.vel_y,
            track.vel_z,
            track.position_uncertainty_m,
            track.velocity_uncertainty_mps,
            getattr(track, 'classification', 'UNKNOWN'),
            getattr(track, 'threat_score', 0.0),
            getattr(track, 'threat_level', 'UNKNOWN'),
            getattr(track, 'is_confirmed', False),
            json.dumps(getattr(track, 'source_sensors', []))
        )
    except Exception as e:
        print(f"Error writing fused track: {e}")


async def write_threat_score(threat) -> None:
    """Write a threat score to the database."""
    db = await get_db()
    
    query = """
        INSERT INTO threat_scores 
        (track_id, timestamp, score, level, classification_label, 
         swarm_probability, estimated_impact_time_s, confidence, time)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
    """
    
    try:
        await db.execute(
            query,
            threat.track_id,
            threat.timestamp,
            threat.score,
            threat.level.value if hasattr(threat.level, 'value') else str(threat.level),
            threat.classification_label,
            threat.swarm_probability,
            threat.estimated_impact_time_s,
            threat.confidence
        )
    except Exception as e:
        print(f"Error writing threat score: {e}")


async def write_assignment_plan(plan) -> None:
    """Write an assignment plan to the database."""
    db = await get_db()
    
    query = """
        INSERT INTO assignments 
        (plan_id, timestamp, assignments, unassigned_threats, plan_validity_ms, time)
        VALUES ($1, $2, $3, $4, $5, NOW())
    """
    
    try:
        # Convert assignments to JSON-serializable format
        assignments_json = [
            {
                "assignment_id": a.assignment_id,
                "track_id": a.track_id,
                "interceptor_id": a.interceptor_id,
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                "eta_s": a.eta_s,
                "engagement_range_m": a.engagement_range_m
            }
            for a in plan.assignments
        ]
        
        await db.execute(
            query,
            plan.plan_id,
            plan.timestamp,
            json.dumps(assignments_json),
            json.dumps(plan.unassigned_threats),
            plan.plan_validity_ms
        )
    except Exception as e:
        print(f"Error writing assignment plan: {e}")


async def get_track_history(
    track_id: str, 
    limit: int = 100
) -> List[Dict]:
    """Get track history from the database."""
    db = await get_db()
    
    query = """
        SELECT * FROM fused_tracks 
        WHERE track_id = $1 
        ORDER BY timestamp DESC 
        LIMIT $2
    """
    
    try:
        return await db.fetch(query, track_id, limit)
    except Exception as e:
        print(f"Error fetching track history: {e}")
        return []


async def get_recent_tracks(
    since: datetime,
    limit: int = 100
) -> List[Dict]:
    """Get recent tracks from the database."""
    db = await get_db()
    
    query = """
        SELECT * FROM fused_tracks 
        WHERE timestamp > $1 
        ORDER BY timestamp DESC 
        LIMIT $2
    """
    
    try:
        return await db.fetch(query, since, limit)
    except Exception as e:
        print(f"Error fetching recent tracks: {e}")
        return []


if __name__ == "__main__":
    # Can be run directly to initialize database
    asyncio.run(init_database())