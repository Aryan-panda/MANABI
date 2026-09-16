# MANABI — Agentic Intelligence & Learning Platform
*A Production-Grade Multi-Domain Agentic Monolith Backed by LangGraph, Deterministic Tools, pgvector RAG, and Internal Model Gateway*

[![CI Pipeline](https://github.com/Aryan-panda/MANABI/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryan-panda/MANABI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: Modular Monolith](https://img.shields.io/badge/Architecture-Modular%20Monolith-blue.svg)](docs/adr/ADR-001-modular-monolith.md)
[![Database: PostgreSQL + pgvector](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-indigo.svg)](docs/adr/ADR-002-postgresql-pgvector.md)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TS-61DAFB.svg)](https://react.dev/)

---

## 1. Problem Statement & The MANABI Solution

### The Problem
Traditional LLM wrappers, chatbots, and generic AI assistants fail catastrophically when deployed in institutional and mission-critical engineering environments due to four foundational flaws:

1. **Hallucination of Strict Policies & Rules**: In university governance, corporate compliance, and legal operations, regulations are rigid. Generic LLMs fabricate attendance rules, invent non-existent course prerequisites, and mislead students about graduation requirements.
2. **LLM Arithmetic Guesswork**: Language models are probabilistic next-token predictors. When asked to perform capacity planning calculations (e.g. QPS throughput, 3-year multi-replica storage retention, network bandwidth, cache Pareto sizing, or p95 SLA latency budgets), LLMs guess and hallucinate numbers, resulting in multi-million-dollar infrastructure sizing errors.
3. **Vendor Lock-in & Brittle Provider Coupling**: Hardcoding proprietary SDKs (such as OpenAI or Google Gemini) directly into route handlers makes systems fragile to outages, prevents model fallback resilience, and blocks seamless integration of local, private models (such as Ollama).
4. **Naive RAG & Context Pollution**: Typical RAG pipelines perform blind token-based splitting, discarding document structure and mixing conversation history with user preferences and institutional knowledge. They lack version governance, document access control, and verifiable citation anchors.

---

### The Solution: MANABI
**MANABI** is an enterprise-grade **Modular Monolith** designed from the ground up to solve these failure modes:

- **Specialized Multi-Domain Agents**: Dedicated personas for **Academic Advisory**, **Engineering Architecture**, **Commerce & Finance**, **Management & Strategy**, and **Legal Intelligence**.
- **Stateful Graph Workflows (LangGraph)**: Multi-step state machine for academic degree planning that strictly audits prerequisites, calculates workload hours, identifies academic risks, and produces verified revised schedules.
- **Deterministic Engineering Calculators**: Important mathematical computations are executed via pure-Python deterministic models (`app.tools.calculator`), guaranteeing zero mathematical hallucination.
- **Internal Model Gateway**: Decouples agents from underlying providers. Features bounded exponential backoff retries, fallback routing (e.g. Gemini → Ollama), token tracking, latency profiling, and Server-Sent Events (SSE) streaming.
- **Structure-Aware pgvector RAG**: Parses Markdown documents along header hierarchies (`#`, `##`, `###`), computes SHA-256 version hashes, enforces role-based document access control (student, faculty, admin), and provides citation match percentages.
- **Evidence-Backed User Memory**: Tracks user attributes, preferences, and verified proficiencies with gradual confidence escalation (Low → Medium → High) strictly separated from RAG knowledge.
- **Zero-Dependency Observability**: Native Prometheus metrics exporter (`/metrics`), structured JSON logging with correlation IDs, and automated benchmark evaluation harness (Section 39).
- **High-Fidelity Dark Glassmorphic Frontend**: React 18 + TypeScript + Vite + Tailwind CSS SPA with live token streaming, interactive Mermaid diagram visualizers, and specialized domain workspace views.

---

## 2. Platform Architecture

```
                                [ Public Traffic ]
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  Nginx Gateway  │ (Port 80)
                               └────────┬────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
    ┌─────────────────┐                                   ┌─────────────────┐
    │  React 18 SPA   │ (Port 3000)                       │ FastAPI Backend │ (Port 8000)
    │  Vite + Tailwind│                                   │ Modular Monolith│
    └─────────────────┘                                   └────────┬────────┘
                                                                   │
       ┌───────────────────────────────────────────────────────────┴──────────────────────────────┐
       │                                                                                          │
       ▼                                                                                          ▼
┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐   ┌──────────────────────────┐
│ Intent Router│   │ Domain Agents   │   │ LangGraph Engine │   │ Deterministic   │   │ Model Gateway            │
│ Keyword/LLM  │──▶│ 5 Personas      │──▶│ Stateful Review  │──▶│ Python Math     │──▶│ Gemini / OpenAI / Ollama │
└──────────────┘   └─────────────────┘   └──────────────────┘   └─────────────────┘   └──────────────────────────┘
       │                    │                      │                     │                         │
       └────────────────────┼──────────────────────┴─────────────────────┴─────────────────────────┘
                            ▼
       ┌───────────────────────────────────────────────┐
       │             Persistence Tier                  │
       ├───────────────────────┬───────────────────────┤
       │ PostgreSQL 16         │ Redis 7               │
       │ + pgvector            │ Ephemeral Cache       │
       │ Relational System of  │ Rate Limiting         │
       │ Record & Vector Store │ Worker Job Queue      │
       └───────────────────────┴───────────────────────┘
```

---

## 3. Workspaces & Key Features

### 1. Conversational Chat & Grounding Evidence Drawer
- Real-time token streaming using **Server-Sent Events (SSE)**.
- Suggested starter prompts tailored to each active agent persona.
- Slide-in **Authoritative Evidence Drawer** displaying similarity match percentage, document section, page number, and source quotes retrieved from pgvector.

### 2. Academic Degree Plan Reviewer (LangGraph Engine)
- View official Student Information System (SIS) records (CGPA, completed credits, program standing).
- Real-time attendance threshold alerts with visual warnings for courses near or below the mandatory 75% threshold.
- Submit proposed semester course schedules to trigger the multi-node LangGraph pipeline:
  `Student Data` → `Prerequisite Check` → `Workload Estimation` → `Risk Scorecard` → `Revised Plan Synthesis`.

### 3. Deterministic Engineering Calculator
Interactive parameter modeling with pure-Python execution:
- **QPS & Throughput**: Peak multipliers, read/write ratios, average vs peak queries per second.
- **Storage & Retention**: Multi-year growth, indexing overhead, replication factor (GB/TB).
- **Network Bandwidth**: Ingress/egress payload estimation in Mbps/Gbps.
- **Cache Pareto Sizing**: 80/20 working set sizing with safety headroom and cloud RAM power-of-2 recommendations.
- **Latency Budget & SLA**: Network RTT, reverse proxy, cache hit probability, and database read latency vs target SLA.

### 4. Architecture & Database Diagram Viewer (Mermaid.js)
- Interactive client-side diagram renderer powered by Mermaid.js.
- Generates and validates **System Architecture Flowcharts** and **PostgreSQL Entity-Relationship Diagrams (ERDs)**.

### 5. Evidence-Based User Memory Manager
- Transparent memory management conforming to Section 24 of the engineering design doc.
- Records skills, preferences, and academic goals with explicit confidence levels (`low`, `medium`, `high`) based on observation counts.
- Full user controls to add, inspect, or delete stored memories.

---

## 4. Repository Directory Structure

```
MANABI/
├── backend/                        # FastAPI Modular Monolith
│   ├── app/
│   │   ├── academic_data/          # Student data provider (Mock & External API)
│   │   ├── agents/                 # Agent definitions & Intent Router
│   │   │   ├── academic/           # Academic Advisor & LangGraph plan reviewer graph
│   │   │   ├── engineering/        # Engineering Architect & Mermaid diagram generator
│   │   │   ├── commerce/           # Commerce & Finance agent
│   │   │   ├── management/         # Management & Strategy agent
│   │   │   └── law/                # Legal Intelligence agent
│   │   ├── api/v1/                 # FastAPI REST routes (auth, chat, academic, eng, memory)
│   │   ├── cache/                  # Redis caching & rate-limiting client
│   │   ├── config/                 # Pydantic settings & environment configuration
│   │   ├── database/               # SQLAlchemy 2.0 async models, session, seed utility
│   │   ├── evaluation/             # Benchmark datasets, metrics, evaluation runner
│   │   ├── llm/                    # Model Gateway (Gemini, OpenAI, Ollama)
│   │   ├── memory/                 # Evidence-backed durable user memory manager
│   │   ├── observability/          # Prometheus metrics registry & structured JSON logger
│   │   ├── rag/                    # Structure-aware chunking, pgvector retriever, ingestion CLI
│   │   ├── security/               # Guardrails, prompt injection defenses, JWT auth, document ACL
│   │   ├── tools/                  # Deterministic capacity planning calculator
│   │   ├── main.py                 # FastAPI application root & middleware setup
│   │   └── worker.py               # Asynchronous background job worker
│   ├── migrations/                 # Alembic database migration revisions
│   ├── tests/                      # 27 automated unit & integration tests
│   ├── Dockerfile                  # Production container image for backend & worker
│   └── requirements.txt            # Python dependencies
├── frontend/                       # React 18 + TypeScript SPA
│   ├── src/
│   │   ├── components/             # UI components (chat, layout, academic, engineering, memory)
│   │   ├── services/               # Asynchronous API client with SSE streaming reader
│   │   ├── stores/                 # Zustand global application state store
│   │   ├── types/                  # TypeScript domain interfaces & types
│   │   ├── App.tsx                 # Root application component
│   │   ├── index.css               # Dark glassmorphic design system tokens
│   │   └── main.tsx                # Entry point with TanStack Query provider
│   ├── Dockerfile                  # Multi-stage production container build (Node -> Nginx)
│   ├── nginx.conf                  # Nginx configuration for SPA client routing
│   └── package.json                # Frontend dependencies
├── data/
│   └── documents/                  # Designated directory for RAG knowledge documents
│       ├── academic/               # Syllabi, attendance rules, curriculum policies
│       ├── engineering/            # System architecture RFCs, tech guidelines
│       ├── commerce/               # Financial models, SaaS valuation benchmarks
│       ├── management/             # Team topologies, sprint frameworks
│       └── law/                    # Software licensing guides, contract clause standards
├── docs/                           # Architecture and operations documentation
│   ├── adr/                        # Architecture Decision Records (ADR-001 to ADR-005)
│   ├── deployment/                 # Production deployment & operations runbook
│   └── REQUIREMENTS_TRACEABILITY.md# Matrix mapping all 50 design doc sections
├── nginx/
│   └── nginx.conf                  # Gateway reverse proxy configuration with SSE support
├── tests/load/
│   └── locustfile.py               # Locust load testing concurrency scenario
├── docker-compose.yml              # Complete multi-container deployment orchestration
├── pytest.ini                      # Pytest runner configuration
└── README.md                       # Platform manual & documentation
```

---

## 5. Quickstart & Deployment Manual

### Prerequisites
- **Docker Engine** (version 24.0+) & **Docker Compose** (v2.20+)
- *Or for local development without Docker*: Python 3.12/3.13, Node.js 20+, PostgreSQL 16 with pgvector, Redis 7.

---

### Option A: Complete Docker Compose Stack (Recommended)

#### 1. Clone Repository & Set Environment Variables
```bash
git clone https://github.com/Aryan-panda/MANABI.git
cd MANABI
cp .env.example .env
```

#### 2. Configure Your LLM Provider in `.env`
Open `.env` and set your preferred model credentials:
```ini
LLM_PROVIDER=gemini # Options: gemini | openai | ollama
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
*(Note: If no API key is set, the Model Gateway automatically operates in safe offline development mode with mock fallback responses).*

#### 3. Build & Launch Containers
```bash
docker compose up --build -d
```
Docker Compose orchestrates 6 services on the internal `manabi-network`:
- `manabi-postgres`: PostgreSQL 16 with pgvector extension enabled (port 5432).
- `manabi-redis`: Redis 7 Alpine in-memory cache and rate limiter (port 6379).
- `manabi-backend`: FastAPI modular monolith web server (port 8000).
- `manabi-worker`: Background job processing worker.
- `manabi-frontend`: React 18 production build served via Nginx (port 3000).
- `manabi-nginx`: Edge reverse proxy routing `/` to frontend and `/api/` to backend (port 80).

#### 4. Run Migrations & Seed Knowledge Base
```bash
# Apply Alembic schema migrations
docker compose exec backend alembic upgrade head

# Seed roles, test accounts, domain agents, and core RAG documents
docker compose exec backend python -m app.database.seed
```

#### 5. Verify Services
- **Frontend Web UI**: [http://localhost:3000](http://localhost:3000) (or [http://localhost](http://localhost))
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live Prometheus Metrics Stream**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Readiness Probe**: [http://localhost:8000/health/ready](http://localhost:8000/health/ready)

---

### Option B: Local Hybrid Development (Without Docker)

#### 1. Backend Setup
```bash
cd backend
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# The Vite dev server will start at http://localhost:5173
```

---

## 6. Knowledge Base & RAG Manual: Adding Documents

MANABI's RAG system uses **structure-aware Markdown chunking** rather than naive fixed-character splitting. It preserves header context (`#`, `##`, `###`), character boundaries, section anchors, and document versions.

### Where Do You Put Documents?
Place your Markdown (`.md`) or text (`.txt`) files in the appropriate domain folder under `data/documents/`:

```
data/documents/
├── academic/      # Drop university handbooks, syllabus docs, attendance policies here
├── engineering/   # Drop architecture RFCs, engineering standards, API contracts here
├── commerce/      # Drop financial models, SaaS unit economics, valuation docs here
├── management/    # Drop team topology guides, agile delivery frameworks here
└── law/           # Drop open-source software licensing rules, contract templates here
```

### How to Ingest Documents into pgvector

Execute the built-in ingestion CLI:

```bash
# Ingest all documents across all domains (domain is auto-detected from folder name):
python -m app.rag.ingestion.ingest --dir data/documents

# Ingest a specific domain folder:
python -m app.rag.ingestion.ingest --dir data/documents/academic --domain academic

# Ingest a single file:
python -m app.rag.ingestion.ingest --file data/documents/academic/sample_curriculum.md --domain academic
```

### Ingestion CLI Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--dir` | string | `None` | Path to a directory of documents to scan recursively. |
| `--file` | string | `None` | Path to a single document file to ingest. |
| `--domain` | string | `academic` | Domain association (`academic`, `engineering`, `commerce`, `management`, `law`). |
| `--access-level`| string | `public` | Document access control level (`public`, `student`, `faculty`, `admin`). |
| `--source` | string | `None` | Custom source attribution string. |

---

## 7. API Reference

All platform endpoints are versioned under `/api/v1`:

### Authentication & Users
- `POST /api/v1/auth/register` — Register a new platform account.
- `POST /api/v1/auth/login` — Authenticate and receive JWT access token.
- `GET /api/v1/users/me` — Retrieve current authenticated user profile and roles.

### Conversations & Real-Time Streaming
- `GET /api/v1/conversations` — List user conversation sessions.
- `POST /api/v1/conversations` — Create a new conversation session.
- `POST /api/v1/conversations/{id}/messages` — Post message and stream token response via **Server-Sent Events (SSE)**.

### Academic Advisor & Degree Planning
- `GET /api/v1/academic/profile` — Fetch official SIS student profile.
- `GET /api/v1/academic/attendance` — Retrieve course attendance records with threshold alarms.
- `POST /api/v1/academic/plan/review` — Execute stateful LangGraph plan review workflow.

### Engineering Architect & Calculators
- `POST /api/v1/engineering/calculate` — Execute deterministic Python capacity calculations (`qps`, `storage`, `bandwidth`, `cache`, `latency`).
- `GET /api/v1/engineering/diagram` — Generate validated Mermaid.js system or database ERD diagrams.

### User Memory & Security
- `GET /api/v1/memory` — Retrieve stored user preferences, skills, and goals.
- `POST /api/v1/memory` — Explicitly record an evidence-based memory item.
- `DELETE /api/v1/memory/{id}` — Delete a memory item.

### Platform Health & Observability
- `GET /health` — Platform liveness probe.
- `GET /health/ready` — Database and Redis readiness probe.
- `GET /metrics` — Prometheus metrics stream in standard 0.0.4 exposition format.

---

## 8. Observability & Monitoring

The platform provides complete observability conforming to Section 38:

### Prometheus Metrics (`/metrics`)
The application server exposes live metrics without third-party collector daemons:
- `manabi_http_requests_total`: Counter by method, endpoint, and HTTP status.
- `manabi_http_request_duration_seconds`: Histogram of endpoint latency distributions.
- `manabi_llm_requests_total`: Counter of calls to Model Gateway by provider and model.
- `manabi_llm_latency_seconds`: Histogram of LLM generation response times.
- `manabi_llm_tokens_total`: Counter of prompt vs completion tokens consumed.
- `manabi_rag_retrievals_total`: Counter of vector searches executed.
- `manabi_tool_executions_total`: Counter of deterministic calculator invocations.
- `manabi_cache_operations_total`: Counter of Redis cache hits and misses.

### Structured JSON Logging
All application logs are formatted in structured JSON with:
```json
{
  "timestamp": "2026-09-16T12:00:00.000Z",
  "level": "INFO",
  "logger": "manabi.llm.gateway",
  "message": "LLM Generation Succeeded",
  "correlation_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "provider": "gemini",
  "model": "gemini-1.5-flash",
  "latency_ms": 320.5,
  "token_usage": {"input": 124, "output": 86}
}
```

---

## 9. Security & Guardrails

Conforming to Section 29 of the engineering design doc:
- **Prompt Injection Scanner**: Regex pattern engine detects and blocks adversarial jailbreaks (e.g. `ignore previous instructions`, `DAN`, `reveal system prompt`).
- **Credential Redaction**: Output filter redacts Google API keys (`AIzaSy...`), OpenAI keys (`sk-...`), and authorization Bearer tokens before sending text to the client.
- **Document Access Control (ACL)**: Restricts RAG retrieval based on user role hierarchy (student < faculty < admin) and document lifecycle status (`active`, `superseded`, `archived`).
- **Sliding-Window Rate Limiting**: Redis-backed rate limiting per client IP/token with graceful in-memory fallback.

---

## 10. Verification & Testing

### Running the Full Pytest Suite
Execute all 27 unit and integration tests across all 8 modules:
```bash
pytest backend/tests -v
```
**Test Coverage**:
- `test_academic_provider.py`: Mock student profile, attendance thresholds, and external API degradation.
- `test_agents.py`: Agent registry and deterministic intent router.
- `test_calculator.py`: QPS, storage retention, bandwidth, cache sizing, and latency budget math.
- `test_chunker.py`: Structure-aware Markdown chunker and SHA-256 content hashing.
- `test_evaluation.py`: RAG ranking metrics (Recall@K, Precision@K, MRR), keyword coverage, numerical tolerance, and Mermaid syntax.
- `test_memory.py`: Evidence accumulation and confidence rating escalation.
- `test_observability.py`: Prometheus metrics counters, gauges, histograms, and structured JSON logs.
- `test_security.py`: Prompt injection defenses, credential sanitization, and document ACLs.

### Running the Section 39 Benchmark Evaluation Runner
Execute the multi-domain evaluation scorecard runner:
```bash
python -m app.evaluation.runner
```
**Scorecard Results**:
- Intent Routing Accuracy: **88.89%**
- Deterministic Math Accuracy: **100.0%** (zero hallucination)
- Mermaid Syntax Validity: **100.0%**
- RAG Grounding Recall@3: **100.0%**
- Overall Evaluation Status: **PASS**

### Running Concurrency Load Tests (Section 40)
Simulate 50 concurrent users with Locust:
```bash
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://localhost:8000
```

---

## 11. Troubleshooting & FAQs

- **Frontend cannot reach backend**: Verify that `backend` is healthy and that `VITE_API_BASE_URL` in frontend points to `http://localhost:8000` (or `http://localhost` if accessing through Nginx).
- **Ollama connection in Docker**: On Windows/macOS, use `http://host.docker.internal:11434` as `OLLAMA_BASE_URL` so the backend container can communicate with Ollama running on the host machine.
- **Redis unavailable**: MANABI is designed with graceful degradation (Section 35). If Redis is down, caching and rate limiting degrade silently to local memory while all persistent data remains safely stored in PostgreSQL.
- **Port 5432 or 80 already in use**: Adjust port mappings in `docker-compose.yml` (e.g. change `"5432:5432"` to `"5433:5432"`).

---

## 12. Documentation Index

- [Architecture Decision Records (ADRs)](docs/adr/): Comprehensive rationale behind the modular monolith, pgvector, Model Gateway, etc.
- [Requirements Traceability Matrix (RTM)](docs/REQUIREMENTS_TRACEABILITY.md): Complete traceability matrix mapping all 50 design doc requirements to code and tests.
- [Production Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md): Operations runbook and container topology.
- [Project Changelog](CHANGELOG.md): Chronological log of all architectural phase completions.

---

## Acknowledgements & Attribution

> **Idea credit**: The initial concept for this project was inspired by an idea proposed by Ayush Duttatreya panigrahi — [yggdrasil-platform](https://github.com/ayushduttatreya/yggdrasil-platform.git). But the architecture, implementation, and subsequent extensions were developed independently by me alone.
