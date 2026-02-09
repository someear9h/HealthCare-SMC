# 🚑 HealthCommand

## 🧠 Overview

HealthCommand is a real-time municipal health operations platform engineered to provide unified visibility and predictive intelligence across distributed health facility networks. It aggregates data from hospitals, primary health centers, laboratories, and emergency response systems into a coherent event-driven analytics layer that detects disease outbreaks within minutes, predicts infrastructure crises before they occur, and enables data-driven resource allocation decisions. Built for municipal corporations managing complex health ecosystems, the system reduces outbreak detection lag from weeks to minutes and transforms reactive crisis management into proactive intelligence-driven operations.

## ✨ Key Features

| Feature | Description | Impact |
|---------|-------------|--------|
| **Real-time Outbreak Detection** | Baseline-deviation anomaly detection across disease indicators with automated alert thresholds | Epidemiological signals surfaced within minutes of data submission |
| **Predictive Risk Scoring** | Ward and facility-level forecasting of resource exhaustion, bed demand, and disease pressure | Leadership enables proactive resource allocation 24 hours in advance |
| **Multi-source Data Ingestion** | Standardized schema validation for hospitals, PHCs, labs, ambulances with graceful malformed payload handling | Single unified API integration point across heterogeneous facility types |
| **Real-time WebSocket Broadcasting** | Live dashboard updates eliminating polling overhead and database thrashing | Sub-second operational state synchronization across all dashboards |
| **Geographic Intelligence** | GIS-integrated hotspot mapping for outbreak and resource constraint visualization | Spatial reasoning enables optimal emergency resource routing |
| **Facility Status Monitoring** | Continuous inventory tracking with crisis prediction based on admission velocity and depletion rates | Infrastructure blindness eliminated through continuous state visibility |
| **Stateless Microservices Architecture** | Horizontally scalable FastAPI services with database abstraction layer | Seamless scaling from pilot deployments to city-wide infrastructure without refactoring |
| **Modular Analytics Stack** | Independent, composable analytical engines for outbreak, spike, and risk analysis | Intelligence layers can evolve independently as detection methodologies improve |

## 🏗 System Architecture

HealthCommand is engineered as an **event-driven analytics platform** rather than a traditional CRUD transactional system. This architectural choice reflects the fundamental nature of municipal health decision-making: not data storage, but signal extraction and predictive intelligence.

**Core Design Principles:**

- **Stateless Services**: Each FastAPI instance is independently disposable, enabling horizontal scaling and zero-downtime deployments
- **Repository Pattern**: Data access abstraction layer decouples analytical logic from storage implementation, enabling database portability (SQLite → PostgreSQL) without service refactoring
- **Denormalized State**: Dashboard queries operate on pre-aggregated city-level and ward-level state optimized for real-time read performance
- **Event-Driven Intelligence**: Data flows through multiple independent analytical pipelines simultaneously—outbreak detection, spike analysis, risk scoring—each producing complementary decision signals
- **WebSocket-Driven Broadcasting**: Computed intelligence is streamed to connected dashboards rather than pulled, eliminating database query thrashing and reducing latency
- **Modular Services**: Analytics engines (outbreak, spike, risk) are loosely coupled, allowing methodologies to evolve without architectural redesign

**Data Flow Architecture:**

```
Facility Ingestion → Validation & Normalization → Repository Layer
                                                        ↓
                                    ┌───────────────────┼───────────────────┐
                                    ↓                   ↓                   ↓
                          Outbreak Engine        Risk Engine          Spike Engine
                                    ↓                   ↓                   ↓
                                    └───────────────────┼───────────────────┘
                                                        ↓
                                        WebSocket Broadcasting
                                                        ↓
                                    Real-time Dashboard Synchronization
```

This architecture enables detection and decision-making latencies measured in seconds rather than hours, while maintaining extensibility for future analytical models.

## 📂 Folder Structure

```
health-smc/
│
├── backend/
│   ├── core/               # Database initialization and WebSocket management
│   ├── routers/            # FastAPI route handlers for all endpoints
│   ├── services/           # Business logic and service orchestration
│   ├── repositories/       # Data access abstraction layer
│   ├── models/             # ORM definitions and analytical engines
│   ├── engines/            # Outbreak, spike, and risk detection  
│   ├── schemas/            # Pydantic request/response schemas
│   ├── simulator/          # Health data stream simulation for testing
│   ├── datasets/           # CSV data files for ingestion and validation
│   ├── data/               # Facility/facility_status reference data
│   └── main.py             # FastAPI application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React UI components
│   │   ├── services/       # API and WebSocket client layer
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Root React component
│   │   └── index.js        # React DOM entry point
│   ├── public/             # Static assets and HTML shell
│   └── package.json        # Node dependencies and build config
│
├── tests/                  # Backend unit and integration tests
├── QUICKSTART.md           # Developer onboarding guide
├── VERIFICATION_CHECKLIST.md # Testing and validation procedures
├── VERIFICATION_SIMULATIONS.md # Simulation scenario documentation
└── README.md               # This file
```

**Folder Descriptions:**

- **backend/core** — Database initialization, connection pooling, WebSocket manager for real-time broadcast orchestration
- **backend/routers** — FastAPI endpoints for ingestion, risk analysis, outbreak detection, facility status, analytics, and ambulance coordination
- **backend/services** — Service layer implementing business logic, orchestrating repositories and analytical engines
- **backend/repositories** — Data access abstraction enabling database portability without modifying downstream code
- **backend/models** — SQLAlchemy ORM definitions, Pydantic analytical schemas, outbreak/risk/spike detection algorithms
- **backend/engines** — Specialized analytical modules: outbreak detection, spike detection, risk scoring, prediction
- **backend/schemas** — Pydantic request/response validation for all API endpoints
- **backend/simulator** — Health data stream generators simulating facility submissions for load testing and scenario verification
- **frontend** — React dashboard with Leaflet GIS integration, WebSocket client, real-time state synchronization
- **tests** — Comprehensive test suite validating ingestion, data normalization, analytical correctness, and API contracts

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | FastAPI, Uvicorn, Python 3.10+ | Asynchronous HTTP request handling, WebSocket broadcasting, zero-downtime deployment |
| **Frontend** | React, Tailwind CSS, Leaflet | Interactive dashboards, geographic visualization, real-time WebSocket synchronization |
| **Database** | SQLAlchemy, SQLite (dev) / PostgreSQL (prod) | ORM abstraction enabling database portability, connection pooling, transactional consistency |
| **Analytics** | Python (Pandas, Numpy) | Baseline-deviation anomaly detection, rolling aggregation, predictive scoring |
| **Data Validation** | Pydantic | Schema validation, type safety, automatic API documentation |
| **Real-time Communication** | WebSocket | Sub-second dashboard updates, broadcast-based state synchronization |
| **Reporting** | FPDF2, Plotly | Automated PDF report generation with embedded visualizations |
| **Development** | Git, Virtual Environment, Pytest | Version control, dependency isolation, automated testing |

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (verify: `python --version`)
- **Node.js 16+** (verify: `node --version`)
- **pip** (Python package manager, included with Python)
- **npm** (comes with Node.js)
- **Git**
- **Virtual environment support** (built into Python 3.10+)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/health-smc.git
cd health-smc
```

#### 2. Set Up Backend Environment

```bash
# Create virtual environment
python -m venv smc-env

# Activate virtual environment
source smc-env/bin/activate  # On macOS/Linux
# OR
smc-env\Scripts\activate     # On Windows

# Install dependencies
cd backend
pip install -r requirements.txt
cd ..
```

#### 3. Set Up Frontend Environment

```bash
cd frontend
npm install
cd ..
```

#### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./health_smc.db
# For PostgreSQL: postgresql://user:password@localhost:5432/health_smc

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# WebSocket Configuration
WS_HOST=0.0.0.0
WS_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Running the Project

#### Start Backend Server

```bash
cd backend
source ../smc-env/bin/activate  # If not already activated
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`  
API documentation: `http://localhost:8000/docs` (Swagger UI)

#### Start Frontend Development Server

```bash
cd frontend
npm start
```

Frontend will be available at: `http://localhost:3000`

#### Optional: Run Simulations

Test the system with simulated health data streams:

```bash
cd backend
python simulate_outbreak.py       # Simulate outbreak scenario
python simulate_scarcity.py       # Simulate resource scarcity scenario
```

#### Run Tests

```bash
cd backend
pytest tests/                     # Run all tests
pytest tests/test_facility_status.py -v  # Run specific test file with verbose output
```

## 📊 Scalability Note

HealthCommand is architected for horizontal scalability from pilot deployments serving a single municipality to city-wide infrastructure coordinating hundreds of health facilities. The stateless FastAPI backend enables trivial load balancing across multiple instances. The repository pattern abstracts database implementation, allowing seamless migration from SQLite (development) to PostgreSQL (production) without modifying business logic. Analytics engines operate on fixed-size rolling windows, preventing memory growth as data volumes increase. WebSocket broadcasting eliminates database polling, maintaining dashboard responsiveness even under high concurrent user load. This architectural foundation enables organic scaling as municipal health operations expand, without fundamental redesign or service interruptions.

## 🔐 Reliability & Performance

**WebSocket Efficiency:** Real-time dashboard updates use WebSocket broadcasting rather than HTTP polling. This reduces database query pressure by orders of magnitude—a single broadcast reaches all connected clients without multiplying database transactions. Dashboard responsiveness improves from polling intervals (typically 5-30 seconds) to sub-second updates.

**Stateless Services:** Each FastAPI instance is independently disposable with zero service-level state. This enables aggressive caching, connection pooling, and load balancing without coordinating distributed state. Node failures impact zero clients because load balancers route to healthy instances instantly.

**Repository Abstraction:** The data access layer decouples analytical code from storage implementation. If PostgreSQL throughput saturates during peak facility ingest periods, read replicas can be added without modifying service code. Database indexes, query optimization, and caching strategies evolve independently from business logic.

**Analytical Incrementalism:** When a new health record arrives, prediction models update incrementally rather than recalculating from scratch. Rolling baselines maintain fixed memory footprints. This keeps dashboard response latency constant regardless of historical data volume.

**Graceful Degradation:** Malformed or inconsistent facility data is validated and normalized rather than rejected. Missing fields are handled with sensible defaults. This prevents partial facility data from cascading into missed outbreak signals.

## 🛣 Future Enhancements

- **Predictive Demand Modeling** — ARIMA/Prophet-based forecasting for bed demand and equipment requirements weeks in advance
- **Mobile Responder Application** — Native iOS/Android app for field ambulance crews with real-time routing optimization and facility status visibility
- **GIS Integration Expansion** — Hexbin-based resource distribution optimization, geographic hotspot prediction, and optimal ambulance station placement analysis
- **PostgreSQL Migration Toolkit** — Automated schema migration, connection pooling optimization, read replica configuration for high-availability deployments
- **Kubernetes Deployment Architecture** — Helm charts for containerized backend, frontend, and database services with auto-scaling policies and health probes
- **Analytical Model Versioning** — A/B testing framework for outbreak detection methodologies, automated model performance tracking, and gradual rollout of improved algorithms
- **Inter-municipal Coordination Layer** — Data exchange protocols enabling neighboring municipal corporations to share outbreak signals and resource availability across jurisdictional boundaries

## 👥 Team

Built by engineers committed to production-grade system design and operational excellence in public health infrastructure.

## 📜 License

MIT License — See LICENSE file for details.
