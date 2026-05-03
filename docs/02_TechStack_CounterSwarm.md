# AEGIS — Counter-Swarm Defense Platform
## Full Tech Stack Reference
### Version 1.0

---

> **Philosophy:** Every tool in this stack is open source, free to use, and chosen because it is the best tool for the job — not because it is popular. The stack is designed to be runnable by a single developer on a laptop, with a clear path to production-grade horizontal scaling.

---

## Stack Overview at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER                    TOOLS                             │
├─────────────────────────────────────────────────────────────┤
│  Simulation               Python, AirSim, ROS 2             │
│  Message Bus              Apache Kafka (Redpanda)           │
│  Sensor Fusion            Python, FilterPy, NumPy           │
│  AI / ML                  PyTorch, YOLOv8, scikit-learn     │
│  Optimization             Google OR-Tools                   │
│  Backend API              FastAPI, WebSockets, Pydantic     │
│  State Cache              Redis                             │
│  Time-series DB           TimescaleDB                       │
│  RF Simulation            GNU Radio                         │
│  Frontend                 React 18, Three.js, Mapbox GL     │
│  Styling                  TailwindCSS                       │
│  Charts                   Recharts                          │
│  Containerization         Docker, Docker Compose            │
│  Language (Systems)       Rust (latency-critical modules)   │
│  Dev Tools                VS Code, Jupyter, Redpanda UI     │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Simulation Layer

### Python 3.11+
**Role:** Primary language for simulation orchestration, fusion engine, AI pipeline, and API backend.

**Why Python:** Fastest iteration speed, best ML ecosystem (PyTorch, NumPy), excellent async support (asyncio). The performance-critical inner loops will be in Rust or C extensions.

**Key Libraries:**
- `asyncio` — concurrent drone agent simulation
- `numpy` — vector math for physics simulation
- `confluent-kafka` — Kafka producer/consumer
- `pydantic` — schema validation across all data contracts

### AirSim (Microsoft)
**Role:** Optional 3D visualization and physics-accurate drone simulation for impressive demo screenshots/video.

**Why AirSim:** Open source (MIT), best-in-class drone physics, Unreal Engine visuals, Python API.

**Note:** AirSim is used for visual demo purposes only. The core logic does not depend on it — it is a pluggable sensor data source.

**Install:** `pip install airsim`

### ROS 2 (Humble)
**Role:** Robot Operating System — provides the publish/subscribe framework used by drone simulators, and is the standard interface for real hardware sensors.

**Why ROS 2:** The standard in robotics and autonomous systems. When hardware partners join, their sensors likely already speak ROS 2.

**Install:** Ubuntu 22.04 + official ROS 2 Humble installer.

---

## 2. Message Bus Layer

### Apache Kafka (via Redpanda)
**Role:** The central event bus. Every inter-module communication goes through Kafka topics. Decouples all modules so they can be developed, scaled, and replaced independently.

**Why Kafka:** Battle-tested at extreme scale (LinkedIn, Uber). Gives replay capability — every sensor event is stored for post-mission analysis and ML training. The architecture that makes AEGIS feel like Cloudflare's infrastructure.

**Why Redpanda specifically:** Kafka-compatible API, but runs as a single binary with no JVM/ZooKeeper dependency. Dramatically easier to run locally. `docker run -p 9092:9092 redpandadata/redpanda`

**Topics:**

| Topic | Producer | Consumer(s) | Description |
|---|---|---|---|
| `sensor.radar` | Simulation Engine | Fusion Engine | Raw radar detections |
| `sensor.optical` | Simulation Engine | Fusion Engine | Optical camera detections |
| `sensor.rf` | Simulation Engine | Fusion Engine | RF signature detections |
| `fused.tracks` | Fusion Engine | AI Classifier, Gateway, DB | Unified track objects |
| `threat.scores` | AI Classifier | Optimizer, Gateway, DB | Per-track threat assessments |
| `assignments` | Optimizer | Gateway, DB | Engagement assignment plans |
| `system.health` | All modules | Gateway | Per-module health metrics |

**Python client:** `confluent-kafka-python`

### Redis 7
**Role:** In-memory system state store. The gateway reads/writes the current full system state here so it can push to WebSocket clients at 10Hz without re-querying the database.

**Why Redis:** Sub-millisecond reads/writes. Native pub/sub for additional real-time needs. Dead simple to run.

**Usage Pattern:** The gateway maintains a single Redis hash `aegis:state` containing the current JSON state blob. Updated on every Kafka event. Read every 100ms and pushed to WebSocket clients.

**Install:** `docker run -p 6379:6379 redis:7`

---

## 3. Sensor Fusion Layer

### FilterPy
**Role:** Python Kalman Filter implementation.

**Why FilterPy:** Clean, well-documented implementation of Kalman and Extended Kalman filters. No need to implement the math from scratch.

**Install:** `pip install filterpy`

**Usage:** One `KalmanFilter` instance per active track. 6-state: `[x, y, z, vx, vy, vz]`. Updated asynchronously as new sensor measurements arrive.

### NumPy + SciPy
**Role:** Vector math, distance calculations, statistical operations used throughout the fusion engine.

**Why:** The standard. Fast C extensions under the hood.

**Install:** `pip install numpy scipy`

### Shapely
**Role:** Geometric operations — computing whether a track is within a protected zone, within an interceptor's engagement envelope, etc.

**Install:** `pip install shapely`

---

## 4. AI / ML Layer

### PyTorch 2.x
**Role:** Deep learning framework for training and running threat classifiers.

**Why PyTorch:** Best research ecosystem, most flexible, excellent deployment story (TorchScript, ONNX export). The choice for anyone serious about ML.

**Install:** `pip install torch torchvision`

### Ultralytics YOLOv8
**Role:** Object detection model for optical sensor classification. Pre-trained on COCO, fine-tuned on drone imagery.

**Why YOLOv8:** State-of-the-art real-time object detection. Free to use. Hugging Face model hub has drone-specific checkpoints.

**Install:** `pip install ultralytics`

### scikit-learn
**Role:** Classical ML utilities — feature scaling, evaluation metrics, simple baselines for kinematic classification before the neural network is trained.

**Install:** `pip install scikit-learn`

### ONNX Runtime
**Role:** Optimized model inference. After training in PyTorch, models are exported to ONNX and run via ONNX Runtime for lower-latency production inference.

**Install:** `pip install onnxruntime`

### Weights & Biases (W&B) — Free Tier
**Role:** Experiment tracking during model training. Logs loss curves, accuracy metrics, model artifacts.

**Why W&B:** Free for individual use. Makes the demo story stronger — "here's our training run."

**Free tier:** Unlimited for individuals.

---

## 5. Optimization Layer

### Google OR-Tools
**Role:** Solves the threat assignment optimization problem — which interceptor engages which drone.

**Why OR-Tools:** Designed for exactly this class of problem (assignment, routing, scheduling). Apache 2.0 licensed. Built by Google. Very fast CP-SAT solver.

**Install:** `pip install ortools`

**Usage:** Model the problem as a min-cost bipartite matching. Threats on one side, interceptors on the other. Edge weights are engagement effectiveness scores. Constraints encode feasibility (range, reload time, heading).

---

## 6. Backend / API Layer

### FastAPI
**Role:** Python web framework serving the REST API and WebSocket gateway.

**Why FastAPI:** Async-native (asyncio). Automatic OpenAPI docs. Pydantic integration for schema validation. 10x faster than Flask for I/O-bound workloads.

**Install:** `pip install fastapi uvicorn`

**Key Dependencies:**
- `uvicorn` — ASGI server
- `websockets` — native WebSocket support in FastAPI
- `pydantic v2` — schema models
- `redis-py` — async Redis client
- `aiokafka` — async Kafka consumer

### Pydantic v2
**Role:** Data schema validation and serialization across all inter-module boundaries. Every Kafka message is validated against a Pydantic model.

**Why Pydantic:** Catches data contract violations at runtime. FastAPI uses it natively. Essential for a multi-module system.

---

## 7. Database Layer

### TimescaleDB
**Role:** Time-series database for storing all sensor events, tracks, threat scores, and assignments. Enables post-mission replay and ML training data export.

**Why TimescaleDB:** PostgreSQL extension — full SQL compatibility. Automatically partitions by time for query performance. Compression for long-term storage.

**Install:** `docker run -p 5432:5432 timescale/timescaledb:latest-pg15`

**Key Tables:**

| Table | Hypertable Partition | Description |
|---|---|---|
| `sensor_events` | `timestamp` | Raw sensor detections |
| `fused_tracks` | `timestamp` | Unified track states |
| `threat_scores` | `timestamp` | Per-track AI assessments |
| `assignments` | `timestamp` | Engagement plans |
| `system_health` | `timestamp` | Module health snapshots |

**Python client:** `asyncpg` (async PostgreSQL driver)

---

## 8. RF Simulation Layer

### GNU Radio
**Role:** Software-defined radio simulation for modeling RF sensor inputs, jamming effects, and drone communication protocols.

**Why GNU Radio:** Industry standard for SDR work. Free, open source. When real SDR hardware is integrated later, GNU Radio is already the right interface.

**Usage in MVP:** Generates synthetic RF signature data (frequency, signal strength, modulation type) for simulated drones. Kafka producer wraps the output.

**Install:** `sudo apt install gnuradio` (Ubuntu)

---

## 9. Frontend Layer

### React 18
**Role:** UI framework for the operator dashboard.

**Why React 18:** Best ecosystem for complex real-time dashboards. Concurrent rendering handles 10Hz state updates without jank. Massive component library availability.

**Create project:** `npm create vite@latest aegis-dashboard -- --template react`

### Three.js (via React Three Fiber)
**Role:** 3D tactical map rendering. Drone positions in 3D space, predicted trajectory arcs, protected zone perimeters, interceptor engagement envelopes.

**Why Three.js:** The standard for WebGL 3D in the browser. React Three Fiber (r3f) makes it composable with React.

**Install:** `npm install three @react-three/fiber @react-three/drei`

### Mapbox GL JS
**Role:** Base map layer under the 3D visualization.

**Why Mapbox:** Best performance, most features. Free tier: 50,000 map loads/month — more than enough for demo and early production.

**Free tier:** Yes, no credit card required for dev.

**Install:** `npm install mapbox-gl react-map-gl`

### TailwindCSS
**Role:** Utility-first CSS framework for the dashboard UI.

**Why Tailwind:** Fastest way to build a polished UI without writing CSS. The dark tactical color scheme is trivially configurable.

**Install:** `npm install tailwindcss postcss autoprefixer`

### Recharts
**Role:** React charting library for the system health metrics panel, threat score timelines, latency graphs.

**Why Recharts:** React-native, composable, free. Not overkill like D3 for this use case.

**Install:** `npm install recharts`

### Zustand
**Role:** Global state management for the dashboard. Holds the WebSocket-received system state.

**Why Zustand:** Minimal boilerplate compared to Redux. Perfect for a real-time state store that gets updated at 10Hz.

**Install:** `npm install zustand`

---

## 10. Systems / Performance Layer

### Rust
**Role:** Latency-critical inner loops where Python is too slow. Specifically: the hot path in the Fusion Engine's track association algorithm, and the Kafka message serialization layer.

**Why Rust:** Zero-cost abstractions, memory safety without GC pauses. Called from Python via PyO3 bindings. Only write Rust where profiling proves Python is the bottleneck.

**MVP Note:** Start in Python. Rewrite hot paths in Rust only when benchmarks show it is necessary. Do not premature optimize.

**PyO3 (Python-Rust bindings):** `pip install maturin` + standard Rust toolchain.

---

## 11. Infrastructure / DevOps Layer

### Docker + Docker Compose
**Role:** Containerizes every service. Single `docker-compose up` brings the entire AEGIS stack online.

**Why Docker:** Non-negotiable for a multi-service system. Without containers, dependency management across 8+ services is a nightmare.

**Key Compose Services:**
```yaml
services:
  redpanda:        # Kafka-compatible message broker
  redis:           # System state cache
  timescaledb:     # Time-series database
  sim-engine:      # Python swarm simulation
  fusion-engine:   # Kalman filter track fusion
  ai-classifier:   # PyTorch threat classification
  optimizer:       # OR-Tools assignment
  api-gateway:     # FastAPI + WebSocket
  dashboard:       # React frontend (Vite dev server)
  redpanda-console: # Kafka UI for debugging
```

**Install:** Docker Desktop (free for personal use).

---

## 12. Development Tools

### VS Code
**Extensions:** Python, Pylance, Docker, Remote Containers, GitLens, Jupyter.

### Jupyter Lab
**Role:** Model training, data exploration, prototype new algorithms before integrating into the pipeline.

**Install:** `pip install jupyterlab`

### Redpanda Console
**Role:** Web UI for inspecting Kafka topics, messages, consumer lag. Essential for debugging the message pipeline.

**Access:** `http://localhost:8080` after `docker-compose up`

### Pytest
**Role:** Testing framework. Every module has unit tests. The fusion engine and classifier have integration tests.

**Install:** `pip install pytest pytest-asyncio`

### Black + Ruff
**Role:** Code formatter (Black) and linter (Ruff). Enforce consistent style across the codebase.

**Install:** `pip install black ruff`

---

## 13. Free Compute Resources

For model training and heavy compute:

| Resource | What You Get | How to Access |
|---|---|---|
| Google Colab | T4 GPU, free | colab.research.google.com |
| Kaggle Notebooks | P100 GPU, 30hr/week | kaggle.com |
| University HPC | Varies, often free | Ask CS department |
| GitHub Student Pack | $200 cloud credits + more | education.github.com |
| Google TPU Research Cloud | Free TPUs | Apply at sites.research.google |
| AWS Educate | $100 credits | aws.amazon.com/education |

---

## 14. Repository Structure

```
aegis/
├── docker-compose.yml
├── README.md
│
├── sim-engine/              # Swarm simulation
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── orchestrator.py
│   │   ├── drone_agent.py
│   │   ├── sensor_simulator.py
│   │   └── kafka_producer.py
│   └── tests/
│
├── fusion-engine/           # Sensor fusion + Kalman
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── track_manager.py
│   │   ├── kalman_filter.py
│   │   └── sensor_adapter.py
│   └── tests/
│
├── ai-classifier/           # PyTorch threat classification
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── model.py
│   │   ├── inference.py
│   │   └── feature_engineering.py
│   ├── training/
│   │   └── train.py
│   └── tests/
│
├── optimizer/               # OR-Tools assignment
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── assignment_solver.py
│   │   └── auction_algorithm.py
│   └── tests/
│
├── api-gateway/             # FastAPI + WebSocket
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── state_manager.py
│   │   ├── ws_handler.py
│   │   └── routes/
│   └── tests/
│
├── dashboard/               # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── TacticalMap.jsx
│   │   │   ├── ThreatPanel.jsx
│   │   │   ├── AssignmentPanel.jsx
│   │   │   ├── AlertTimeline.jsx
│   │   │   └── SystemHealth.jsx
│   │   ├── store/
│   │   │   └── useAegisStore.js
│   │   └── ws/
│   │       └── websocket.js
│   └── tests/
│
└── shared/                  # Shared schemas + utilities
    ├── schemas/
    │   ├── track.py
    │   ├── threat_score.py
    │   └── assignment.py
    └── utils/
        └── geo.py
```

---

## 15. Technology Decision Log

This section records why key technology decisions were made, for future reference.

**Why Kafka over RabbitMQ?** Kafka provides event replay, which is critical for ML training data and post-mission analysis. RabbitMQ does not.

**Why TimescaleDB over InfluxDB?** Full SQL compatibility means any analyst can query with standard tools. InfluxDB's Flux query language is non-standard.

**Why FastAPI over Django?** AEGIS is an API + WebSocket server, not a full-stack web app. FastAPI is purpose-built for this. Django's ORM and templating are irrelevant overhead.

**Why React over Vue/Svelte?** Ecosystem size. The Three.js + Mapbox integrations (r3f, react-map-gl) are best maintained for React.

**Why Redpanda over vanilla Kafka?** Single binary, no JVM, no ZooKeeper. A solo developer can run it reliably. Kafka-compatible API means migration to full Kafka when needed is transparent.

**Why OR-Tools over custom algorithm?** OR-Tools' CP-SAT solver is a world-class optimizer developed by Google. Writing a custom solver that outperforms it would take years. Use the best tool available.

---

*Document Version: 1.0 | AEGIS Founding Team*
