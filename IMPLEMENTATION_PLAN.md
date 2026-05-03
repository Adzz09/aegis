# AEGIS — Implementation Plan & Progress Tracker
### Counter-Swarm Defense Platform | MVP for YC Pitch
**Version:** 1.1 | **Last Updated:** 2026-05-02

> **North Star:** A fully functional simulation-backed C2 platform — demo-able live, on a laptop, in a YC interview room. 50-drone swarm attack, AI classification, interceptor assignments, all live. End-to-end latency < 500ms.

---

## Quick Reference — Tech Stack

| Layer | Technology |
|---|---|
| Simulation | Python 3.11+, AirSim (optional), asyncio |
| Message Bus | Redpanda (Kafka-compatible), `confluent-kafka-python` |
| Sensor Fusion | Python, FilterPy, NumPy, SciPy, Shapely |
| AI / ML | PyTorch 2.x, YOLOv8, scikit-learn, ONNX Runtime, W&B |
| Optimization | Google OR-Tools (CP-SAT) + Auction Algorithm |
| Backend API | FastAPI, Uvicorn, WebSockets, Pydantic v2, aiokafka, redis-py |
| State Cache | Redis 7 (`aegis:state` hash key) |
| Database | TimescaleDB (PostgreSQL) via `asyncpg` |
| Frontend | React 18, Vite, Three.js (R3F), Mapbox GL JS, TailwindCSS, Zustand, Recharts |
| Infra | Docker, Docker Compose |
| Dev Tools | Redpanda Console (`:8080`), Jupyter Lab, Pytest, Black, Ruff |

## Service Port Map

| Service | Port |
|---|---|
| Redpanda (Kafka) | 9092 |
| Redpanda Console UI | 8080 |
| Redis | 6379 |
| FastAPI Gateway | 8000 |
| TimescaleDB | 5432 |
| React Dashboard (Vite dev) | 5173 |
| Simulation Engine (gRPC) | 50051 |

## Kafka Topics

| Topic | Producer | Consumer(s) |
|---|---|---|
| `sensor.radar` | Simulation Engine | Fusion Engine |
| `sensor.optical` | Simulation Engine | Fusion Engine |
| `sensor.rf` | Simulation Engine | Fusion Engine |
| `fused.tracks` | Fusion Engine | AI Classifier, Gateway, TimescaleDB |
| `threat.scores` | AI Classifier | Optimizer, Gateway, TimescaleDB |
| `assignments` | Optimizer | Gateway, TimescaleDB |
| `system.health` | All modules | Gateway |
| `*.dlq` (dead-letter) | Any module | Monitoring / Logging |

---

## Phase 1: Foundation (Weeks 1–2)

**Goal:** Stand up the entire infrastructure, basic simulation, shared schemas, and a live map showing 10 moving dots.

### 1.1 — Repository Structure

- [ ] **Task 1.1.1:** Initialize the following directory layout:
  ```
  aegis/
  ├── docker-compose.yml
  ├── README.md
  ├── sim-engine/         (Dockerfile, requirements.txt, src/, tests/)
  ├── fusion-engine/      (Dockerfile, requirements.txt, src/, tests/)
  ├── ai-classifier/      (Dockerfile, requirements.txt, src/, training/, tests/)
  ├── optimizer/          (Dockerfile, requirements.txt, src/, tests/)
  ├── api-gateway/        (Dockerfile, requirements.txt, src/, tests/)
  ├── dashboard/          (Dockerfile, package.json, src/)
  └── shared/             (schemas/, utils/)
  ```
- [ ] **Task 1.1.2:** Create `shared/schemas/` with Pydantic v2 models for all data contracts:
  - `track.py` — `SensorEvent`, `FusedTrack` schemas
  - `threat_score.py` — `ThreatScore` schema
  - `assignment.py` — `AssignmentPlan`, `EngagementOrder` schemas
  - `health.py` — `ModuleHealth` schema
- [ ] **Task 1.1.3:** Create `shared/utils/geo.py` with Shapely-based helpers for zone intersection, range-circle creation, and lat/lon distance calculations.

### 1.2 — Infrastructure (Docker Compose)

- [ ] **Task 1.2.1:** Write `docker-compose.yml` with all services:
  ```yaml
  services:
    redpanda, redis, timescaledb,
    sim-engine, fusion-engine, ai-classifier,
    optimizer, api-gateway, dashboard, redpanda-console
  ```
- [ ] **Task 1.2.2:** Verify `docker-compose up` brings all infrastructure services online (Redpanda, Redis, TimescaleDB).
- [ ] **Task 1.2.3:** Confirm Redpanda Console is accessible at `http://localhost:8080` for topic/message inspection.
- [ ] **Task 1.2.4:** Create all Kafka topics upfront (including `system.health` and dead-letter queues `*.dlq`).

### 1.3 — Swarm Simulation Engine (Skeleton)

- [ ] **Task 1.3.1:** Implement `SwarmOrchestrator` — spawns N drone agents, assigns attack vectors, manages formation behavior.
- [ ] **Task 1.3.2:** Implement `DroneAgent` state machine: `idle → navigating → attacking → evading → destroyed`.
- [ ] **Task 1.3.3:** Implement `SensorSimulator` wrapping each drone's telemetry through radar noise model, optical FOV constraints, and RF propagation model.
- [ ] **Task 1.3.4:** Implement `KafkaProducer` publishing sensor events to `sensor.radar`, `sensor.optical`, `sensor.rf`.
- [ ] **Task 1.3.5:** Validate output schema for each producer against the `SensorEvent` Pydantic model in `shared/schemas/`.
- [ ] **Task 1.3.6:** Start with 10 drones. Make swarm count configurable (target: 1–1000).

### 1.4 — API Gateway (Skeleton)

- [ ] **Task 1.4.1:** Initialize FastAPI app with `uvicorn`. Setup HTTPS (WSS) for all endpoints.
- [ ] **Task 1.4.2:** Implement `state_manager.py` — async Redis client maintaining `aegis:state` hash. Read every 100ms.
- [ ] **Task 1.4.3:** Implement `ws_handler.py` — WebSocket endpoint `WS /ws/state` pushing state to all clients at 10Hz.
- [ ] **Task 1.4.4:** Implement `GET /api/health` endpoint returning per-module status placeholders.
- [ ] **Task 1.4.5:** Implement `system.health` Kafka consumer — each module publishes heartbeats; gateway aggregates into `aegis:state`.
- [ ] **Task 1.4.6:** Implement graceful WebSocket reconnect logic on the gateway side.

### 1.5 — Dashboard (Skeleton)

- [ ] **Task 1.5.1:** Bootstrap React 18 + Vite project: `npm create vite@latest dashboard -- --template react`.
- [ ] **Task 1.5.2:** Install core dependencies: `tailwindcss`, `zustand`, `three`, `@react-three/fiber`, `@react-three/drei`, `mapbox-gl`, `react-map-gl`, `recharts`.
- [ ] **Task 1.5.3:** Apply Design System CSS variables (full `:root {}` block from `03_DesignSystem_CounterSwarm.md`) to `index.css`.
- [ ] **Task 1.5.4:** Configure `tailwind.config.js` with custom colors, fonts (`JetBrains Mono`, `Inter`), and animations from the Design System doc.
- [ ] **Task 1.5.5:** Load Google Fonts (`Inter`, `JetBrains Mono`) in `index.html`.
- [ ] **Task 1.5.6:** Implement `useAegisStore.js` (Zustand) to hold the full WebSocket system state.
- [ ] **Task 1.5.7:** Implement `ws/websocket.js` — connects to `WS /ws/state`, feeds messages into Zustand store.
- [ ] **Task 1.5.8:** Implement Layout Grid (`App.jsx`):
  - Topbar (48px): AEGIS wordmark, Alert Timeline placeholder, System Health placeholder
  - Left Nav (200px): `Overview`, `Tracks`, `Sensors`, `Defenders`, `History`, `Settings`
  - Central Tactical Map (fills remaining space)
  - Threat Panel (right, 280px)
  - Assignment Panel (bottom, 160px)
- [ ] **Task 1.5.9:** Render Mapbox GL base map in the Tactical Map area with dark terrain style.
- [ ] **Task 1.5.10:** Render basic Three.js track dots from WebSocket state (positions only, no color-coding yet).

### ✅ Phase 1 Checkpoint
> **Demo:** Live map showing 10 simulated moving dots fed from the Simulation Engine → Kafka → API Gateway → WebSocket → Dashboard. No fusion, no AI yet.
> **Ship this as a GIF to Twitter.**

---

## Phase 2: Sensor Fusion Engine (Weeks 3–4)

**Goal:** Merge noisy, multi-sensor streams into clean, unified track objects visible on the dashboard.

### 2.1 — Sensor Adapter

- [ ] **Task 2.1.1:** Implement `SensorAdapter` — normalizes each sensor stream (radar, optical, RF) into a common `DetectionEvent` schema before fusion.
- [ ] **Task 2.1.2:** Handle latency mismatch: timestamp-align sensor events from different sources.

### 2.2 — Kalman Filter

- [ ] **Task 2.2.1:** Implement `KalmanFilter` using FilterPy — 6-state: `[x, y, z, vx, vy, vz]`.
- [ ] **Task 2.2.2:** Handle asynchronous, multi-rate sensor updates correctly (predict-only steps between measurements).
- [ ] **Task 2.2.3:** Tune process noise (`Q`) and measurement noise (`R`) matrices for realistic drone kinematics.

### 2.3 — Track Manager

- [ ] **Task 2.3.1:** Implement `TrackManager` maintaining the set of all active tracks.
- [ ] **Task 2.3.2:** Implement nearest-neighbor + Mahalanobis distance gating for detection-to-track association.
- [ ] **Task 2.3.3:** Implement track lifecycle: **Tentative** (new, unconfirmed) → **Confirmed** (enough detections) → **Deleted** (no update in >2 seconds).
- [ ] **Task 2.3.4:** Handle occlusion: do not immediately delete a track if a sensor goes offline momentarily.

### 2.4 — Integration & Persistence

- [ ] **Task 2.4.1:** Integrate Fusion Engine with Kafka — consume all `sensor.*` topics, publish `FusedTrack` objects to `fused.tracks`.
- [ ] **Task 2.4.2:** Validate all published `fused.tracks` messages against the shared Pydantic `FusedTrack` schema. Route schema violations to `fused.tracks.dlq`.
- [ ] **Task 2.4.3:** Create TimescaleDB hypertables: `sensor_events`, `fused_tracks`, `system_health`.
- [ ] **Task 2.4.4:** Write all `fused.tracks` events to the `fused_tracks` TimescaleDB table via `asyncpg`.
- [ ] **Task 2.4.5:** Publish `system.health` heartbeats from the Fusion Engine at 1Hz.

### 2.5 — Dashboard Update

- [ ] **Task 2.5.1:** Update Gateway to consume `fused.tracks` and merge into `aegis:state`.
- [ ] **Task 2.5.2:** Update Dashboard Three.js layer to render fused tracks (noise visibly reduced vs. raw detections).
- [ ] **Task 2.5.3:** Display track uncertainty ellipse (`position_uncertainty_m`) as a semi-transparent ring around each dot.

### ✅ Phase 2 Checkpoint
> **Demo:** Dashboard shows fused tracks, not raw sensor noise. Position uncertainty rings visible. Noise visibly reduced.

---

## Phase 3: AI Threat Classifier (Weeks 5–6)

**Goal:** Classify each track in real time, assign threat scores, and color-code the dashboard.

### 3.1 — Training Data Generation

- [ ] **Task 3.1.1:** Generate synthetic training data from the Simulation Engine — cover all 5 label classes: `BENIGN`, `UNKNOWN`, `HOSTILE_FPV`, `HOSTILE_FIXED_WING`, `SWARM_NODE`.
- [ ] **Task 3.1.2:** Augment with open ADS-B data and public drone flight datasets for `BENIGN` class.
- [ ] **Task 3.1.3:** Set up Weights & Biases (W&B, free tier) for experiment tracking across training runs.

### 3.2 — Model Training

- [ ] **Task 3.2.1:** Implement Branch A (Kinematic MLP) in PyTorch — features: velocity, altitude, approach angle, track history.
- [ ] **Task 3.2.2:** Implement Branch B (Behavioral Transformer) in PyTorch — input: last 30 frames of track state. Detects swarm coordination patterns.
- [ ] **Task 3.2.3:** Implement lightweight ensemble head fusing both branch outputs.
- [ ] **Task 3.2.4:** Train on GPU (Google Colab T4 or Kaggle P100 — free tier). Log all runs to W&B.
- [ ] **Task 3.2.5:** Validate classification accuracy >90% on held-out test swarm scenarios (PRD success metric).
- [ ] **Task 3.2.6:** Export trained model to ONNX format via `torch.onnx.export()`.

### 3.3 — Inference Service

- [ ] **Task 3.3.1:** Implement inference pipeline using ONNX Runtime (lower-latency than PyTorch for serving).
- [ ] **Task 3.3.2:** Implement `feature_engineering.py` — extract kinematic features and 30-frame history window from each track.
- [ ] **Task 3.3.3:** Implement AI Classifier service — consume `fused.tracks`, run ONNX inference, publish `ThreatScore` to `threat.scores`. Latency target: <100ms per track.
- [ ] **Task 3.3.4:** Validate `threat.scores` messages against shared Pydantic `ThreatScore` schema. Route violations to `threat.scores.dlq`.
- [ ] **Task 3.3.5:** Write all threat scores to the `threat_scores` TimescaleDB hypertable.
- [ ] **Task 3.3.6:** Publish `system.health` heartbeats from the AI Classifier including average inference latency.

### 3.4 — Dashboard Update

- [ ] **Task 3.4.1:** Update Gateway to consume `threat.scores` and merge into `aegis:state`.
- [ ] **Task 3.4.2:** Apply threat-level color coding to all track dots on the Three.js map using the Design System's threat scale colors (`#10B981` → `#F59E0B` → `#F97316` → `#EF4444` → `#DC2626`).
- [ ] **Task 3.4.3:** Add pulsing animation to `HOSTILE` and `CRITICAL` threat dots (1.5s and 0.6s cycles per Design System spec).
- [ ] **Task 3.4.4:** Add radar sweep ring animations (`expand-fade`, 2s ease-out) for active sensors on the map.
- [ ] **Task 3.4.5:** Build `ThreatPanel.jsx` (right sidebar, 280px) — ranked list of confirmed threats with: Track ID, classification badge, threat score, ETA countdown, click-to-focus-map.
- [ ] **Task 3.4.6:** Implement threat-level status badges (`BENIGN`, `UNKNOWN`, `CAUTION`, `HOSTILE`, `CRITICAL`, `ENGAGED`) using the Design System `.badge` CSS spec.
- [ ] **Task 3.4.7:** Implement `ThreatRow` component with critical row pulse animation (`row-pulse`, 1s cycle) per Design System spec.
- [ ] **Task 3.4.8:** Display `swarm_probability` and `estimated_impact_time_s` on each threat row.

### ✅ Phase 3 Checkpoint
> **Demo:** Drone swarm approaches the protected zone. Threat scores rise in real time. Map dots turn red. Threat panel populates. Investor can immediately read what's happening.

---

## Phase 4: Threat Assignment Optimizer & Full Demo (Weeks 7–8)

**Goal:** AI-driven countermeasure assignment working end-to-end. Scenario launcher live. Full demo ready.

### 4.1 — Assignment Solver

- [ ] **Task 4.1.1:** Formulate the threat assignment problem as min-cost bipartite matching in Google OR-Tools CP-SAT.
- [ ] **Task 4.1.2:** Model constraints: one countermeasure per target at a time, engagement feasibility (range via Shapely, heading, reload time).
- [ ] **Task 4.1.3:** Implement optimization objective: minimize total expected threat damage to protected zones; prioritize high-score threats and those with shortest `estimated_impact_time_s`.
- [ ] **Task 4.1.4:** Implement the **Auction Algorithm** as a fallback for low-latency re-planning when the CP-SAT solver cannot complete within the 300ms window. (`auction_algorithm.py`)
- [ ] **Task 4.1.5:** Validate assignment plan validity: `plan_validity_ms` must be 500ms (triggers re-plan automatically).
- [ ] **Task 4.1.6:** Track and publish `unassigned_threats` in the plan — these represent gaps in defensive coverage.

### 4.2 — Optimizer Service Integration

- [ ] **Task 4.2.1:** Implement Optimizer service — consume `threat.scores`, read current interceptor state from Redis.
- [ ] **Task 4.2.2:** Publish `AssignmentPlan` objects to the `assignments` Kafka topic. Validate against Pydantic schema; route violations to `assignments.dlq`.
- [ ] **Task 4.2.3:** Write all assignment plans to the `assignments` TimescaleDB hypertable.
- [ ] **Task 4.2.4:** Publish `system.health` heartbeats from the Optimizer including re-plan cycle latency.

### 4.3 — API Gateway — Full REST Endpoints

- [ ] **Task 4.3.1:** Implement `GET /api/tracks` — return current confirmed tracks from `aegis:state`.
- [ ] **Task 4.3.2:** Implement `GET /api/tracks/{id}/history` — query track history from TimescaleDB via `asyncpg`.
- [ ] **Task 4.3.3:** Implement `GET /api/assignments/current` — return current assignment plan from `aegis:state`.
- [ ] **Task 4.3.4:** Implement `POST /api/sim/scenario` — load a new swarm scenario into the Simulation Engine (demo use only). Must support triggering a 50-drone swarm attack.
- [ ] **Task 4.3.5:** Ensure all REST endpoints return proper Pydantic-validated responses and OpenAPI docs are auto-generated.

### 4.4 — Dashboard Update

- [ ] **Task 4.4.1:** Build `AssignmentPanel.jsx` (bottom bar, 160px) — displays current engagement assignments, countermeasure status, engagement timelines. Format: `[INTERCEPTOR_01] → [TRK-00042]  ETA: 23s  STATUS: ENGAGING`.
- [ ] **Task 4.4.2:** Render interceptor positions and engagement envelopes on Three.js map (violet, 20% opacity fill, per Design System `MAP_COLORS`).
- [ ] **Task 4.4.3:** Render interception beam lines (`0xA78BFA`) connecting engaged interceptors to their target tracks.
- [ ] **Task 4.4.4:** Render predicted trajectory arcs for hostile tracks (`0xEF4444`) and benign tracks (`0x42A5F5`).
- [ ] **Task 4.4.5:** Render protected zone perimeter rings (blue border `0x1E88E5`, 12% opacity fill).
- [ ] **Task 4.4.6:** Update track dot color to `ENGAGED` (`#8B5CF6`, violet glow) when an assignment is active.
- [ ] **Task 4.4.7:** Build the Scenario Launcher UI — a button in the dashboard that calls `POST /api/sim/scenario` to trigger the 50-drone swarm attack demo.

### ✅ Phase 4 Checkpoint
> **Demo:** Full YC demo dry run. 50-drone swarm attack triggered from UI. AI classification colors all tracks. Interceptors assigned. Assignment Panel live. Unassigned threats visible in red. End-to-end working.

---

## Phase 5: Polish & Performance (Weeks 9–10)

**Goal:** Latency targets hit. UI looks like a real defense product. Demo rehearsed and recorded.

### 5.1 — Dashboard UI Polish

- [ ] **Task 5.1.1:** Implement `AlertTimeline.jsx` (top bar) — scrolling chronological alert feed. Critical alerts pulse red (`pulse-red` animation). New alerts slide in from the right (250ms, ease-out per Design System).
- [ ] **Task 5.1.2:** Implement `SystemHealth.jsx` (top right) — per-module health dots (`online` green glow, `degraded` amber, `offline` pulsing red), Kafka consumer lag indicator, model inference latency display, WebSocket connection status.
- [ ] **Task 5.1.3:** Implement Left Nav panel (`200px`) with sections: `Overview`, `Tracks`, `Sensors`, `Defenders`, `History`, `Settings`. Use Design System Surface/Void backgrounds and monospace labels.
- [ ] **Task 5.1.4:** Add Recharts-based metric graphs in `SystemHealth` or a dedicated panel: inference latency timeline, Kafka consumer lag over time, end-to-end latency graph.
- [ ] **Task 5.1.5:** Apply the AEGIS wordmark: `AEGIS` in JetBrains Mono 700, color `#42A5F5`, letter-spacing 0.2em. Sub-label `COUNTER-SWARM DEFENSE` in 10px, `#475569`.
- [ ] **Task 5.1.6:** Polish all panel headers using the `.panel-card__header` CSS spec (monospace, 11px, uppercase, letter-spacing 0.12em, `--color-text-muted`).
- [ ] **Task 5.1.7:** Implement Three.js terrain and grid in `MAP_COLORS` palette (`terrain: 0x0D1A2D`, `terrain_grid: 0x1A2D4A`).
- [ ] **Task 5.1.8:** Add track creation animation (200ms, ease-out) and track destruction animation (400ms, ease-in, fade to gray `#6B7280`).

### 5.2 — Performance & Latency

- [ ] **Task 5.2.1:** Benchmark end-to-end latency (sensor event → dashboard render). Target: **<500ms**. Display live in System Health panel.
- [ ] **Task 5.2.2:** Benchmark per-module latencies:
  - Sensor event → fused track: **<100ms**
  - Fused track → threat score: **<100ms**
  - Threat score → assignment plan: **<300ms**
  - Dashboard render cycle: **10Hz (100ms)**
- [ ] **Task 5.2.3:** Profile Python hot paths in fusion engine and classifier. If benchmarks show Python is the bottleneck in track association, implement Rust extension via PyO3/Maturin.
- [ ] **Task 5.2.4:** Validate Redis `aegis:state` read/write cycle stays under 1ms.
- [ ] **Task 5.2.5:** Validate the optimizer re-plan cycle completes within 300ms for 50 threats. If not, confirm Auction Algorithm fallback is activating correctly.

### 5.3 — Reliability & Security

- [ ] **Task 5.3.1:** Confirm HTTPS on all REST endpoints and WSS on all WebSocket connections.
- [ ] **Task 5.3.2:** Implement dead-letter queue (`*.dlq`) monitoring — log all schema violations to stdout with module name and message sample.
- [ ] **Task 5.3.3:** Test graceful WebSocket reconnect from the Dashboard (simulate gateway restart).
- [ ] **Task 5.3.4:** Validate Simulation Engine stays at 99% uptime during a 30-minute sustained demo run.

### 5.4 — Demo Rehearsal

- [ ] **Task 5.4.1:** Write the full demo script:
  - T+0s: Open dashboard. "SYSTEMS ONLINE" shown in green. All health dots green.
  - T+10s: Trigger 50-drone swarm scenario from UI.
  - T+15s: First tracks appear on map — yellow (UNKNOWN).
  - T+20s: AI classifier engages — tracks turn orange/red. Threat panel populates.
  - T+30s: Optimizer assigns interceptors. Assignment panel fills. Violet envelopes visible.
  - T+45s: First interceptions. Tracks turn gray. Swarm count dropping.
  - T+60s: Remaining hostile tracks continue inbound. Alert timeline fires critical alerts.
  - T+90s: Demo ends with clear before/after — swarm neutralized or overrun.
- [ ] **Task 5.4.2:** Ensure demo runs flawlessly in under 3 minutes without crashing.
- [ ] **Task 5.4.3:** Verify the "wow moment" is clearly visible within 30 seconds of starting.
- [ ] **Task 5.4.4:** Record demo video. Capture as GIF for Twitter/LinkedIn.
- [ ] **Task 5.4.5:** Submit YC application.

### ✅ Phase 5 Checkpoint
> **Final state:** All latency targets met and displayed live. UI looks like a real defense product. Full 50-drone scenario runs flawlessly in under 3 minutes. Video recorded. YC application submitted.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Simulation too unrealistic for investors | Medium | High | Research real swarm attack patterns; cite real-world incidents |
| Redpanda too complex to stand up quickly | Low | Medium | Use `docker run -p 9092:9092 redpandadata/redpanda` — single binary, no JVM |
| AI model underperforms on demo day | Medium | High | Hardcode a "cheat mode" — preloaded scenarios with known-good classification outcomes |
| Optimizer exceeds 300ms for large scenarios | Medium | Medium | Auction Algorithm fallback already planned in Task 4.1.4 |
| Export control concerns | Low | High | Keep everything in simulation; no real RF, no real targeting |
| Solo developer bandwidth | High | High | Ruthlessly cut scope — MVP is modules 1–6 only. Nothing else. |

---

## Success Metrics (YC Demo Day Targets)

| Metric | Target |
|---|---|
| Simultaneous simulated drones tracked | 50+ |
| End-to-end latency | <500ms (live in dashboard) |
| AI classification accuracy | >90% on test scenarios |
| Assignment plan cycle time | <300ms |
| Demo runtime (no crash) | 3 minutes |
| Investor "understands it" time | <30 seconds |
| LOI / MOU from defense partner | ≥1 |

---

*Document Version: 1.1 | AEGIS Founding Team | Classification: Unclassified — Public*
