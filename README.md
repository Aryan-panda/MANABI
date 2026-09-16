# MANABI — Agentic Intelligence & Learning Platform

MANABI is a multi-domain Agentic GenAI platform built as a modular monolith. It provides specialized domain intelligence across Academic Advisory, Engineering Architecture, Commerce, Management, and Law, powered by an internal multi-provider Model Gateway, stateful LangGraph workflows, a pgvector-backed RAG pipeline, and evidence-based durable user memory.

---

## Architecture Overview

```
User → React + TypeScript (Vite + Tailwind) → Nginx → FastAPI Modular Monolith
       ├── Intent Router
       ├── Agents Runtime (Academic, Engineering, Commerce, Management, Law)
       ├── Workflows (LangGraph stateful plan review & generation)
       ├── RAG Engine (Structure-aware chunking + PostgreSQL / pgvector)
       ├── Deterministic Tools (Capacity, QPS, Latency & Storage Calculators)
       ├── Model Gateway (Gemini, OpenAI, external Ollama)
       └── Persistence (PostgreSQL for system of record, Redis for ephemeral cache)
```

---

## Agents

1. **Academic Advisor (Full-featured)**:
   - Institutional regulation and policy guidance.
   - Curriculum planning, prerequisite verification, workload balance.
   - Stateful LangGraph Academic Plan Reviewer.
   - Student data abstraction layer (`AcademicDataProvider`) with mock and external API adapters.
2. **Engineering Architect (Full-featured)**:
   - System design, database modeling, and trade-off analysis.
   - Deterministic engineering calculators (QPS, storage, bandwidth, cache sizing).
   - Validated Mermaid diagram generation (ERDs, sequence flows, topology).
3. **Commerce (Lightweight & Extensible)**:
   - Domain-aware financial, pricing, and unit-economic guidance.
4. **Management (Lightweight & Extensible)**:
   - Agile methodology, resource allocation, and organizational strategy.
5. **Law (Lightweight & Extensible)**:
   - Informational legal concept guidance with educational disclaimers.

---

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, Mermaid.js
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, pytest
- **GenAI / Orchestration**: LangChain, LangGraph, Internal Model Gateway (Gemini, OpenAI, Ollama)
- **Data & Vector Storage**: PostgreSQL 16 + pgvector, Redis 7
- **Infrastructure**: Docker & Docker Compose, Nginx, GitHub Actions CI/CD

---

## Quickstart

### 1. Environment Setup
```bash
cp .env.example .env
# Configure your GEMINI_API_KEY, OPENAI_API_KEY, or local OLLAMA_BASE_URL
```

### 2. Run with Docker Compose
```bash
docker compose up -d --build
```
Access the application:
- Frontend UI: `http://localhost:3000` (or `http://localhost:80` through Nginx)
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 3. Local Development (Hybrid)
- **Backend**:
  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate  # or .venv\Scripts\activate on Windows
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

---

## Architecture Decision Records (ADRs)
See [docs/adr/](docs/adr/) for detailed rationale behind all architectural decisions.
