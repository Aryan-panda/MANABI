# MANABI — Agentic Intelligence & Learning Platform

[![CI Pipeline](https://github.com/Aryan-panda/MANABI/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryan-panda/MANABI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: Modular Monolith](https://img.shields.io/badge/Architecture-Modular%20Monolith-blue.svg)](docs/adr/ADR-001-modular-monolith.md)
[![Database: PostgreSQL + pgvector](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-indigo.svg)](docs/adr/ADR-002-postgresql-pgvector.md)

**MANABI** is a production-grade multi-domain Agentic GenAI platform built as an enterprise modular monolith. It provides specialized domain intelligence across **Academic Advisory**, **Engineering Architecture**, **Commerce & Finance**, **Management & Strategy**, and **Legal Intelligence**, powered by an internal multi-provider Model Gateway, stateful LangGraph workflows, a pgvector-backed RAG engine, and evidence-based durable user memory.

---

## Acknowledgements & Attribution

> **Idea credit**: The initial concept for this project was inspired by an idea proposed by Ayush Duttatreya panigrahi — [yggdrasil-platform](https://github.com/ayushduttatreya/yggdrasil-platform.git). But the architecture, implementation, and subsequent extensions were developed independently by me alone.

---

## High-Level Platform Architecture

```
User → React + TypeScript (Vite + Tailwind) → Nginx Reverse Proxy (Port 80)
       ├── Direct Frontend SPA (Port 3000)
       └── FastAPI Modular Monolith (Port 8000)
           ├── Intent Router (Deterministic keyword density + LLM structured classification)
           ├── Domain Agents (Academic, Engineering, Commerce, Management, Law)
           ├── Stateful Workflows (LangGraph plan reviewer graph)
           ├── Grounded RAG Pipeline (Structure-aware chunking + PostgreSQL pgvector)
           ├── Deterministic Tools (Python arithmetic: QPS, storage, bandwidth, cache, SLA latency)
           ├── Model Gateway (Provider-agnostic: Google Gemini, OpenAI, local external Ollama)
           ├── User Memory Engine (Evidence accumulation & confidence rating)
           ├── Observability (Prometheus metrics at /metrics + structured JSON logging)
           └── Persistence (PostgreSQL 16 for durable records, Redis 7 for ephemeral caching)
```

---

## Domain Agents & Features

| Agent Persona | Capability Depth | Key Features |
| :--- | :--- | :--- |
| **Academic Advisor** | Full-Featured | Degree plan review, attendance threshold warnings (<75%), course prerequisites validation, credit overload checks, LangGraph multi-step graph execution. |
| **Engineering Architect** | Full-Featured | System capacity planning, deterministic calculators (QPS, 3-yr storage, bandwidth, cache Pareto sizing, latency budgets), validated Mermaid.js architecture diagrams and ERDs. |
| **Commerce & Finance** | Extensible | Unit economics formulas (CAC, LTV, Payback Period), pricing strategies, operating leverage, SaaS metrics. |
| **Management & Strategy** | Extensible | Team Topologies (Stream-aligned vs Platform teams), Agile/Scrum delivery, OKRs, organizational scaling. |
| **Legal Intelligence** | Extensible | Software licensing guidance (MIT vs AGPL v3 copyleft risks), contract clauses (NDA, confidentiality), educational compliance disclaimers. |

---

## How to Set Up and Use MANABI

### Option A: Complete Docker Compose Stack (Recommended)

To launch the full platform (PostgreSQL + pgvector, Redis, Backend, Worker, Frontend, and Nginx reverse proxy):

1. **Clone repository and configure environment**:
   ```bash
   git clone https://github.com/Aryan-panda/MANABI.git
   cd MANABI
   cp .env.example .env
   ```

2. **Add your API Keys to `.env`**:
   ```ini
   LLM_PROVIDER=gemini # or openai / ollama
   GEMINI_API_KEY=your-gemini-api-key
   OPENAI_API_KEY=your-openai-api-key
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```
   *(Note: If no API key is provided, the platform automatically runs in safe offline development mode with mock fallbacks).*

3. **Start services**:
   ```bash
   docker compose up --build -d
   ```

4. **Initialize Database & Seed Initial Knowledge**:
   ```bash
   # Execute database schema migrations
   docker compose exec backend alembic upgrade head

   # Seed initial roles, test users, agents, and RAG knowledge
   docker compose exec backend python -m app.database.seed
   ```

5. **Access the Interfaces**:
   - **Frontend Web Application**: [http://localhost:3000](http://localhost:3000) (or [http://localhost](http://localhost) via Nginx)
   - **FastAPI Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Prometheus Metrics Stream**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
   - **Readiness Health Check**: [http://localhost:8000/health/ready](http://localhost:8000/health/ready)

---

### Option B: Local Hybrid Development (Without Docker)

1. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## RAG Documents & Knowledge Base: Where & How to Add Them

MANABI uses a **structure-aware RAG pipeline** backed by PostgreSQL and pgvector. Documents are not blindly dumped into the context; they are chunked preserving Markdown header hierarchies (`#`, `##`, `###`), tracked with SHA-256 hashes, governed with access levels (Section 37), and presented in the UI with citation match percentages.

### 1. Pre-Loaded Default Documents
Running `python -m app.database.seed` automatically installs:
- *University Academic Regulations and Student Handbook* (attendance policies, condonation rules, credit limits, prerequisites).
- *Production System Engineering & Architecture Guidelines* (PostgreSQL + pgvector configuration, Redis caching rules, latency budgets).

### 2. Adding Your Own Custom Documents Manually

Place your custom Markdown (`.md`) or text (`.txt`) files into the designated folder structure under `data/documents/`:

```
data/documents/
├── academic/      <- Drop university syllabi, handbooks, regulations, policies here
├── engineering/   <- Drop engineering guides, architecture RFCs, API contracts here
├── commerce/      <- Drop financial reports, pricing models, SaaS benchmarks here
├── management/    <- Drop team frameworks, agile delivery guides, OKR docs here
└── law/           <- Drop IP guidelines, contract clauses, compliance policies here
```

### 3. Ingesting Documents into pgvector

Execute the built-in ingestion CLI:

```bash
# Ingest an entire directory (automatically assigns domain based on folder name):
python -m app.rag.ingestion.ingest --dir data/documents

# Ingest a specific domain folder:
python -m app.rag.ingestion.ingest --dir data/documents/academic --domain academic

# Ingest a single file:
python -m app.rag.ingestion.ingest --file data/documents/academic/sample_curriculum.md --domain academic
```

The ingestion tool will:
1. Extract the document title from the top header or filename.
2. Compute the content hash for versioning.
3. Decompose the document into structure-aware chunks.
4. Insert records into `documents`, `document_versions`, and `document_chunks`.
5. Make the knowledge immediately retrievable by the agents via semantic search with source citations!

---

## Automated Verification & Testing

### 1. Running Unit & Integration Tests
Execute the complete test suite (27 passing tests across all 8 modules):
```bash
pytest backend/tests -v
```

### 2. Running Benchmark Evaluation (Section 39)
Execute the multi-domain benchmark evaluation runner:
```bash
python -m app.evaluation.runner
```
Outputs a verified evaluation scorecard measuring Intent Routing accuracy, 100% deterministic mathematical exactness, Mermaid syntax validity, and RAG Grounding Recall@3.

### 3. Load Testing (Section 40)
Simulate concurrent users using Locust:
```bash
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://localhost:8000
```

---

## Documentation Index

- [Architecture Decision Records (ADRs)](docs/adr/): Rationale behind modular monolith, pgvector, Model Gateway, etc.
- [Requirements Traceability Matrix (RTM)](docs/REQUIREMENTS_TRACEABILITY.md): Complete mapping of all 50 design doc requirements to code and tests.
- [Production Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md): Operations runbook and container topology.
- [Project Changelog](CHANGELOG.md): Detailed log of all architectural phase milestones.
