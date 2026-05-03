# AEGIS — Counter-Swarm Defense Platform
## Product Requirements Document (PRD)
### Version 1.0 | MVP for YC Pitch

---

> **Mission:** Build the "operating system" for drone swarm defense — a real-time, AI-powered command and control platform that fuses every sensor and every interceptor on a site into a single tactical picture, restoring cost advantage to defenders.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Vision & Strategy](#3-vision--strategy)
4. [Target Users](#4-target-users)
5. [MVP Scope — What Ships First](#5-mvp-scope)
6. [Full Product Scope — Post-MVP Roadmap](#6-full-product-scope)
7. [System Architecture & Data Flow](#7-system-architecture--data-flow)
8. [Module Specifications](#8-module-specifications)
9. [Connection Map — How Everything Talks](#9-connection-map)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Milestones & Timeline](#11-milestones--timeline)
12. [Success Metrics (YC Demo Day Targets)](#12-success-metrics)
13. [Risks & Mitigations](#13-risks--mitigations)
14. [Appendix — Glossary](#14-appendix)

---

## 1. Executive Summary

AEGIS is a software-first, AI-powered counter-swarm defense platform. It ingests real-time data from heterogeneous sensor networks (radar, RF, optical, ADS-B), fuses them into a unified threat picture, autonomously classifies and prioritizes threats, and assigns optimal interception responses — all in under 500ms latency.

The MVP is a fully functional simulation environment: a working command-and-control dashboard tracking live simulated drone swarms, demonstrating AI-driven threat assignment, and showcasing the architecture that hardware partners plug into. This is the demo that gets us into YC.

**One-line pitch:** *"Cloudflare for drone swarms — we're the software layer that makes any sensor, any interceptor, and any operator work together in real time."*

---

## 2. Problem Statement

### The Asymmetry Crisis

| Metric | Attacker Cost | Defender Cost |
|---|---|---|
| FPV Attack Drone | $500 | — |
| Patriot Missile (intercept) | — | $3,000,000 |
| Cost Ratio | 1x | 6,000x |

A swarm of 1,000 drones costs $500,000 to deploy. Defending against it with current systems costs billions.

### Why Current Solutions Fail

Today's counter-drone stack is a pile of disconnected systems:

- Radars that don't talk to cameras
- Jammers operated by different personnel than interceptors
- No unified software brain
- Humans in the loop for every decision — far too slow for swarm timescales
- Systems designed for single-drone threats, not coordinated swarms of hundreds

### The Insight

Drone defense is no longer a kinetic weapons problem. It is a **real-time distributed systems problem.** The winning solution is not a better missile — it is better software. AEGIS is that software.

---

## 3. Vision & Strategy

### Short Term (MVP — 3 months)
Deliver a simulation-backed C2 platform that demonstrates the full software stack: sensor fusion, AI classification, autonomous threat assignment, and operator dashboard. No hardware required. Pitch to YC.

### Medium Term (6–12 months)
Partner with hardware integrators, defense labs, and university robotics programs to plug real sensor data into AEGIS. Target AFWERX grants and SBIR funding.

### Long Term (12–36 months)
Become the standard C2 software layer for counter-drone installations globally — the operating system that any sensor vendor and any interceptor vendor integrates into.

---

## 4. Target Users

### Primary — MVP

**Defense Operators / Analysts (Simulated for Demo)**
These are the end users in the actual deployment. For MVP, we simulate their workflow to demonstrate usability.

Goals: See all threats at once, respond faster, make fewer cognitive errors under pressure.

### Secondary — MVP Pitch Audience

**YC Partners / Investors**
They need to see: a working demo, a clear moat, a large market, and a founder who ships.

**Defense Hardware Partners (Future)**
Radar vendors, interceptor manufacturers, system integrators. They plug their hardware into our software API.

**Government / Military Buyers (Future)**
DoD, DHS, allied defense ministries. Procurement cycles are long — relationships start now.

---

## 5. MVP Scope

> **Core Principle:** The MVP is a fully functional software system running against simulated data. It must be demo-able live, on a laptop, in a YC interview room.

### What the MVP Includes

#### M1 — Swarm Simulation Engine
A synthetic environment that generates realistic drone swarm behavior: coordinated attack vectors, formation flying, evasion patterns, communication protocols. Built on AirSim + ROS 2 with a Python orchestration layer.

Delivers: Real-time swarm telemetry (position, velocity, heading, RF signature) streamed over Kafka.

#### M2 — Sensor Fusion Engine
Ingests multiple simulated sensor streams — radar returns, optical detections, RF signatures — and fuses them into unified track objects using a Kalman Filter. Handles sensor disagreement, occlusion, and latency mismatch.

Delivers: A clean, unified stream of `Track` objects, each representing one confirmed aerial entity.

#### M3 — AI Threat Classification
A PyTorch model (YOLOv8 backbone for optical + transformer for behavioral) that classifies each Track as: Benign (bird/commercial), Unknown, Hostile FPV, Hostile Fixed-Wing, or Swarm Node.

Delivers: Per-track threat scores updated at 10Hz.

#### M4 — Threat Assignment Optimizer
Given a set of confirmed hostile tracks and available interceptors/countermeasures, compute the optimal assignment using Google OR-Tools. Minimizes total threat score reaching the protected zone while respecting interceptor reload times and engagement envelopes.

Delivers: An assignment plan, updated every 500ms.

#### M5 — Operator Dashboard (The Demo)
A React + Three.js real-time 3D tactical display showing:

- Live map with all tracked objects (color-coded by threat level)
- Incoming swarm visualization with predicted trajectories
- AI recommendations panel
- Interceptor status panel
- System health / latency indicators
- Alert timeline

This is the "single pane of glass" — the Cloudflare dashboard for drone defense.

#### M6 — WebSocket API Gateway
FastAPI backend exposing a WebSocket endpoint that the dashboard subscribes to. Streams the full system state at 10Hz. Also exposes a REST API for historical data queries.

### What the MVP Explicitly Does NOT Include

- Real hardware integration (radar, interceptors, jammers)
- Real RF signal processing
- Classified or export-controlled components
- Mobile app
- Multi-site coordination
- User authentication beyond basic session management

---

## 6. Full Product Scope

> Post-YC funding. Documented here to show investors the roadmap is real.

### Phase 2 — Hardware Integration (Months 4–9)

- Sensor abstraction layer: plug any radar (MESA, Echodyne, DroneShield) into the fusion engine via a standardized sensor adapter interface
- Real RF spectrum ingestion via SDR (Software Defined Radio)
- Interceptor command interface: send engagement orders to networked interceptors
- GPS spoofing and RF jamming as software-controlled countermeasures

### Phase 3 — Autonomy Stack Attacks (Months 9–18)

- Adversarial signal injection against drone autopilot protocols (MAVLink, DJI OcuSync)
- GPS spoofing modules (software-defined, hardware-agnostic)
- Mesh network disruption: degrade swarm coordination by attacking inter-drone communication
- Adversarial ML: generate inputs that fool enemy swarm recognition systems

### Phase 4 — Multi-Site & Federation (Months 12–24)

- Federated C2: multiple AEGIS installations sharing threat intelligence in real time
- Theater-level swarm tracking across hundreds of kilometers
- Integration with existing C2 systems (Link 16, ATAK)
- Allied nation deployment

### Phase 5 — Predictive Defense (Months 18–36)

- Swarm intent prediction: where is this swarm going and what is it targeting?
- Pre-positioning of interceptors based on predicted attack vectors
- Reinforcement learning for interceptor assignment optimization
- After-action analysis and training replay

---

## 7. System Architecture & Data Flow

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AEGIS PLATFORM                              │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   SENSOR     │    │   FUSION     │    │   AI THREAT      │  │
│  │   LAYER      │───▶│   ENGINE     │───▶│   CLASSIFIER     │  │
│  │              │    │              │    │                  │  │
│  │ Radar Sim    │    │ Kalman Filter│    │ PyTorch Model    │  │
│  │ Optical Sim  │    │ Track Mgmt   │    │ YOLOv8 + TF      │  │
│  │ RF Sim       │    │ Dedup        │    │ Threat Scorer    │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│          │                  │                      │            │
│          ▼                  ▼                      ▼            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              APACHE KAFKA — EVENT BUS                     │  │
│  │    topic: raw.tracks  |  topic: fused.tracks              │  │
│  │    topic: threat.scores  |  topic: assignments            │  │
│  └───────────────────────────────────────────────────────────┘  │
│          │                  │                      │            │
│          ▼                  ▼                      ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  ASSIGNMENT  │    │  TIMESCALE   │    │  FASTAPI + WS    │  │
│  │  OPTIMIZER   │───▶│  DATABASE    │    │  GATEWAY         │  │
│  │              │    │              │    │                  │  │
│  │  OR-Tools    │    │  Time-series │    │  REST + WS       │  │
│  │  Auction Alg │    │  Storage     │    │  10Hz stream     │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                  │             │
└──────────────────────────────────────────────────┼─────────────┘
                                                   │
                                                   ▼
                                    ┌──────────────────────────┐
                                    │   OPERATOR DASHBOARD     │
                                    │                          │
                                    │  React + Three.js        │
                                    │  Real-time 3D map        │
                                    │  Threat panel            │
                                    │  Assignment panel        │
                                    └──────────────────────────┘
```

### Data Flow — Step by Step

**Step 1: Simulation generates events**
The swarm simulation (AirSim/Python) generates drone telemetry at 10Hz per drone. Each event contains: drone ID, lat/lon/alt, velocity vector, RF signature hash, optical bounding box (if in camera FOV).

**Step 2: Sensor streams published to Kafka**
Three separate Kafka producers simulate three sensor types:
- `sensor.radar` — position + velocity returns, with noise
- `sensor.optical` — bounding box detections from simulated cameras
- `sensor.rf` — RF frequency signatures, signal strength

**Step 3: Fusion Engine consumes and correlates**
The Fusion Engine subscribes to all three sensor topics. It runs a multi-hypothesis Kalman Filter to associate detections across sensors into unified Track objects. Publishes to `topic: fused.tracks`.

**Step 4: AI Classifier scores each Track**
The Classifier subscribes to `fused.tracks`, runs inference (PyTorch), and publishes a threat score + classification label to `topic: threat.scores`. Latency target: <100ms per track.

**Step 5: Assignment Optimizer computes response plan**
The Optimizer subscribes to `threat.scores` and the current interceptor state. Solves the assignment problem and publishes the plan to `topic: assignments`.

**Step 6: Gateway aggregates state and streams to dashboard**
The FastAPI gateway maintains the full system state in Redis. It consumes all relevant topics, updates the state, and pushes the full state to all connected WebSocket clients at 10Hz.

**Step 7: Dashboard renders**
The React dashboard receives the state blob and updates the Three.js 3D scene, panels, and alerts in real time. No polling — pure WebSocket push.

**Step 8: TimescaleDB records everything**
All events are written to TimescaleDB for post-mission analysis, replay, and ML training data.

---

## 8. Module Specifications

### Module 1: Swarm Simulation Engine

**Purpose:** Generate realistic multi-drone swarm scenarios without real hardware.

**Technology:** Python (primary), AirSim (optional for 3D visualization), custom swarm behavior engine.

**Key Components:**

`SwarmOrchestrator` — spawns N drone agents, assigns attack vectors, manages swarm coordination behavior (formations, splitting, swarming around obstacles).

`DroneAgent` — individual drone state machine: idle → navigating → attacking → evading → destroyed.

`SensorSimulator` — wraps each drone's telemetry and emits it through the lens of different sensor types (radar noise model, optical FOV constraints, RF propagation model).

`KafkaProducer` — publishes sensor events to the correct Kafka topics.

**Configurable Parameters:**
- Number of drones: 1–1000
- Attack vector: single direction, multi-vector, distributed
- Drone type mix: FPV, fixed-wing, loitering munitions
- Sensor noise level: low/medium/high
- Communication jamming: on/off

**Output Schema (per radar detection event):**
```json
{
  "sensor_id": "radar_north_01",
  "timestamp_ms": 1712345678901,
  "drone_id": "swarm_alpha_042",
  "position": { "lat": 28.6139, "lon": 77.2090, "alt_m": 120 },
  "velocity": { "vx": 15.2, "vy": -3.1, "vz": 0.5 },
  "rcs_dbsm": -12.3,
  "confidence": 0.87
}
```

---

### Module 2: Sensor Fusion Engine

**Purpose:** Merge noisy, heterogeneous sensor streams into clean, unified track objects.

**Technology:** Python, FilterPy (Kalman Filter), NumPy.

**Key Components:**

`TrackManager` — maintains the set of all active tracks. Associates new detections to existing tracks using nearest-neighbor + Mahalanobis distance gating. Creates new tracks for unassociated detections. Deletes tracks that haven't been updated in >2 seconds.

`KalmanFilter` — 6-state filter (x, y, z, vx, vy, vz) per track. Handles asynchronous, multi-rate sensor updates correctly.

`SensorAdapter` — normalizes each sensor's output into a common detection schema before fusion.

**Output Schema (per fused track):**
```json
{
  "track_id": "TRK-00042",
  "timestamp_ms": 1712345678950,
  "position": { "lat": 28.6140, "lon": 77.2091, "alt_m": 119.8 },
  "velocity": { "vx": 15.1, "vy": -3.0, "vz": 0.4 },
  "position_uncertainty_m": 3.2,
  "contributing_sensors": ["radar_north_01", "optical_cam_02"],
  "track_age_s": 12.4,
  "track_status": "CONFIRMED"
}
```

---

### Module 3: AI Threat Classifier

**Purpose:** Classify each track as hostile/benign and assign a threat priority score.

**Technology:** Python, PyTorch, YOLOv8, scikit-learn.

**Model Architecture:**

Two-branch classifier:
- Branch A (Kinematic) — MLP on velocity, altitude, approach angle, track history. Fast, runs on CPU.
- Branch B (Behavioral) — Transformer on the last 30 frames of track state. Detects swarm coordination patterns.

Outputs fused by a lightweight ensemble head.

**Labels:**
- `BENIGN` — commercial drone, bird, aircraft
- `UNKNOWN` — insufficient data
- `HOSTILE_FPV` — small fast maneuvering drone
- `HOSTILE_FIXED_WING` — faster, larger, likely loitering munition
- `SWARM_NODE` — confirmed part of coordinated swarm

**Training Data:** Synthetic from simulation engine + open ADS-B data + public drone flight datasets.

**Output Schema:**
```json
{
  "track_id": "TRK-00042",
  "timestamp_ms": 1712345679050,
  "classification": "HOSTILE_FPV",
  "threat_score": 0.94,
  "swarm_probability": 0.88,
  "estimated_impact_time_s": 47,
  "predicted_target": "ZONE_ALPHA"
}
```

---

### Module 4: Threat Assignment Optimizer

**Purpose:** Compute the optimal assignment of countermeasures to threats in real time.

**Technology:** Python, Google OR-Tools (CP-SAT solver), custom auction algorithm for low-latency re-planning.

**Inputs:**
- Current threat list with scores and predicted trajectories
- Available countermeasures: type (interceptor/jammer/aerosol), status (ready/reloading/engaged), engagement envelope (max range, heading constraints)

**Optimization Objective:**
Minimize total expected threat damage to protected zones, subject to:
- Each countermeasure can engage at most one target at a time
- Engagement feasibility constraints (range, angle, reload time)
- Prioritize high-score threats and threats closest to impact

**Output Schema:**
```json
{
  "plan_id": "PLAN-00234",
  "timestamp_ms": 1712345679100,
  "assignments": [
    {
      "countermeasure_id": "INTERCEPTOR_01",
      "target_track_id": "TRK-00042",
      "engagement_type": "KINETIC",
      "engagement_window_ms": [1712345680000, 1712345682000],
      "confidence": 0.91
    }
  ],
  "unassigned_threats": ["TRK-00051", "TRK-00063"],
  "plan_validity_ms": 500
}
```

---

### Module 5: Operator Dashboard

**Purpose:** Render the full system state in a real-time, usable operator interface.

**Technology:** React 18, Three.js (r3f), Mapbox GL JS (free tier), TailwindCSS, Recharts.

**Views:**

`TacticalMap (Primary)` — 3D terrain map with live drone positions, color-coded by threat level. Predicted trajectories shown as arcs. Protected zones shown as perimeter rings. Interceptor positions and engagement envelopes shown.

`ThreatPanel (Right sidebar)` — ranked list of all confirmed threats. Click to focus map. Shows track ID, classification, threat score, ETA.

`AssignmentPanel (Bottom)` — current engagement assignments, countermeasure status, engagement timelines.

`AlertTimeline (Top bar)` — scrolling chronological alert feed. Critical alerts pulse red.

`SystemHealth (Top right)` — sensor status indicators, Kafka consumer lag, model inference latency, WebSocket connection status.

**Color Coding:**
- Green: Benign / No threat
- Yellow: Unknown / Monitoring
- Orange: Hostile — assigned, being engaged
- Red: Hostile — unassigned, inbound
- Pulsing Red: Critical — impact imminent

---

### Module 6: API Gateway

**Purpose:** Single ingress point for the dashboard. Maintains system state, serves WebSocket streams.

**Technology:** FastAPI, Redis, WebSockets (native), Pydantic.

**Endpoints:**

`WS /ws/state` — push full system state at 10Hz to all connected clients.

`GET /api/tracks` — current confirmed tracks (REST).

`GET /api/tracks/{id}/history` — track history from TimescaleDB.

`GET /api/assignments/current` — current assignment plan.

`GET /api/health` — system health status, per-module latency metrics.

`POST /api/sim/scenario` — (demo only) load a new swarm scenario into the simulation engine.

---

## 9. Connection Map — How Everything Talks

```
SIMULATION ENGINE
    │
    ├──[Kafka Producer]──▶ topic: sensor.radar ──▶ FUSION ENGINE
    ├──[Kafka Producer]──▶ topic: sensor.optical ──▶ FUSION ENGINE  
    └──[Kafka Producer]──▶ topic: sensor.rf ──▶ FUSION ENGINE
    
FUSION ENGINE
    └──[Kafka Producer]──▶ topic: fused.tracks ──▶ AI CLASSIFIER
                                                ──▶ API GATEWAY (state update)
                                                ──▶ TIMESCALEDB (write)
    
AI CLASSIFIER
    └──[Kafka Producer]──▶ topic: threat.scores ──▶ ASSIGNMENT OPTIMIZER
                                                ──▶ API GATEWAY (state update)
                                                ──▶ TIMESCALEDB (write)
                                                
ASSIGNMENT OPTIMIZER
    └──[Kafka Producer]──▶ topic: assignments ──▶ API GATEWAY (state update)
                                              ──▶ TIMESCALEDB (write)
                                              
API GATEWAY
    ├──[Redis GET/SET]──▶ REDIS (system state store)
    └──[WebSocket PUSH]──▶ OPERATOR DASHBOARD (10Hz)
    
OPERATOR DASHBOARD
    └──[WebSocket]──▶ API GATEWAY
    └──[REST GET]──▶ API GATEWAY (on-demand history queries)
```

### Service Discovery & Ports (Local Dev)

| Service | Port |
|---|---|
| Kafka Broker | 9092 |
| Kafka UI (Redpanda Console) | 8080 |
| Redis | 6379 |
| FastAPI Gateway | 8000 |
| TimescaleDB (PostgreSQL) | 5432 |
| React Dashboard (Vite dev) | 5173 |
| Simulation Engine gRPC | 50051 |

All services run in Docker containers, orchestrated by a single `docker-compose.yml`.

### Inter-Service Data Contracts

All Kafka messages are serialized as JSON (Avro for production). All services validate schemas on consumption using Pydantic models. Schema violations are logged and the message is sent to a dead-letter topic for debugging.

---

## 10. Non-Functional Requirements

### Latency
- Sensor event to fused track: <100ms
- Fused track to threat score: <100ms
- Threat score to assignment plan: <300ms
- Total end-to-end (event to dashboard update): <500ms
- Dashboard render cycle: 10Hz (100ms)

### Reliability (MVP — Simulation)
- Simulation engine: 99% uptime during demo
- API Gateway: graceful WebSocket reconnect on disconnect
- Kafka: single-broker for MVP (not production-grade, acceptable for demo)

### Scalability (Design Targets — Not MVP)
- Track capacity: 10,000 simultaneous tracks
- Sensor ingestion: 1M events/second
- Dashboard clients: 100 simultaneous operators
- Assignment re-plan cycle: <500ms for 1,000 threats

### Security (MVP — Minimal)
- HTTPS for all REST endpoints
- WebSocket over WSS
- No real classified data handled in MVP

---

## 11. Milestones & Timeline

### Week 1–2: Foundation
- Docker Compose up with Kafka, Redis, TimescaleDB, FastAPI skeleton
- Simulation engine generating 10 drones, publishing to Kafka
- Basic dashboard displaying simulated positions on a Mapbox map

**Checkpoint:** Live map showing 10 moving dots. Ship this as a GIF to Twitter.

### Week 3–4: Fusion Engine
- Kalman Filter track management working
- Multi-sensor association logic complete
- Fused tracks streaming through Kafka to dashboard

**Checkpoint:** Dashboard shows fused tracks, not raw sensor detections. Noise visibly reduced.

### Week 5–6: AI Classifier
- Kinematic classifier (MLP) trained on synthetic data
- Threat scores appearing in dashboard
- Color-coded threat levels on map

**Checkpoint:** Demo shows drone swarm approaching, threat scores rising in real time.

### Week 7–8: Assignment Optimizer + Full Demo
- OR-Tools assignment working end-to-end
- Assignment panel live in dashboard
- Scenario loader: click to launch 50-drone swarm attack
- Full end-to-end demo polished and rehearsed

**Checkpoint:** Full YC demo ready. 50-drone swarm attack, AI classification, interceptor assignments, all live.

### Week 9–10: Polish + Apply
- Performance profiling, latency optimization
- UI polish — looks like a real defense product
- Record demo video
- YC application submitted

---

## 12. Success Metrics

### Technical Metrics (Demo Day Targets)
- Demonstrate real-time tracking of 50+ simultaneous simulated drones
- End-to-end latency under 500ms, visible in system health panel
- AI classification accuracy >90% on test swarm scenarios
- Assignment optimizer producing valid plans within 300ms

### Business Metrics (YC Conversation Targets)
- One LOI or MOU from a defense hardware partner, university lab, or defense innovation unit (AFWERX, DIU)
- Evidence of market pull — one paid pilot conversation started
- Clear articulation of the path from simulation to real sensor integration

### Demo Script Metrics
- Demo runs flawlessly in 3 minutes without crashing
- Investor can understand what they're looking at within 30 seconds
- The "wow moment" is clearly visible: 50 drones appear, system responds autonomously

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Simulation too unrealistic to impress investors | Medium | High | Research real swarm attack patterns; cite real incidents (Iranian drone attack on AWS) |
| Kafka too complex for solo dev to stand up fast | Medium | Medium | Use Redpanda (Kafka-compatible, simpler ops) as drop-in replacement |
| AI model underperforms on demo day | Medium | High | Hardcode a "cheat mode" for the demo — preloaded scenarios with known-good outcomes |
| Export control concerns | Low | High | Keep everything in simulation; no real RF, no real targeting. Consult a lawyer before hardware integration |
| YC application too early / not enough traction | Medium | High | Get any LOI or advisor from defense sector before applying |
| Single developer bandwidth | High | High | Ruthlessly cut scope — MVP is modules 1-6 only. Nothing else. |

---

## 14. Appendix — Glossary

**C2** — Command and Control. The system through which operators command defensive assets and receive situational awareness.

**Track** — A confirmed aerial object being actively monitored by the system. Created when enough sensor detections are correlated to establish confidence.

**Kalman Filter** — A recursive Bayesian estimator that optimally combines noisy sensor measurements with a physical motion model to produce clean position/velocity estimates.

**Threat Assignment** — The problem of deciding which countermeasure engages which threat. Equivalent to a min-cost bipartite matching problem in operations research.

**FPV Drone** — First-Person View drone. Cheap, fast, maneuverable, used extensively in recent conflicts. The primary threat vector AEGIS defends against.

**OR-Tools** — Google's open-source operations research library. Includes a high-performance CP-SAT solver used for threat assignment optimization.

**SDR** — Software Defined Radio. Hardware that allows radio signal processing to be performed in software, enabling flexible RF sensing and countermeasures.

**AFWERX** — The U.S. Air Force's innovation arm. A primary government funding pathway for defense tech startups.

**DIU** — Defense Innovation Unit. DoD entity that connects commercial technology to military needs. A key partnership target.

**MAVLink** — The most common drone autopilot communication protocol. A target for autonomy stack attacks in Phase 3.

---

*Document Version: 1.0 | Author: AEGIS Founding Team | Classification: Unclassified — Public*

---
