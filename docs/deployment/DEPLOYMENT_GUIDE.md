# MANABI — Production Deployment & Operations Guide

This guide details the steps to build, configure, run, and monitor the **MANABI Agentic Intelligence & Learning Platform** in staging and production environments using Docker Compose.

---

## 1. System Architecture & Topology

```
                       [ Incoming Traffic ]
                                │
                                ▼
                       ┌─────────────────┐
                       │  Nginx Reverse  │ (Port 80)
                       │     Proxy       │
                       └────────┬────────┘
                                │
             ┌──────────────────┴──────────────────┐
             ▼                                     ▼
    ┌─────────────────┐                   ┌─────────────────┐
    │  React 18 SPA   │ (Port 3000)       │  FastAPI Monolith│ (Port 8000)
    │  Nginx Alpine   │                   │  Modular App    │
    └─────────────────┘                   └────────┬────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼                                                   ▼
                ┌──────────────────┐                                ┌──────────────────┐
                │  PostgreSQL 16   │ (Port 5432)                    │   Redis 7 Cache  │ (Port 6379)
                │  + pgvector      │                                │   & Rate Limit   │
                └──────────────────┘                                └──────────────────┘
```

---

## 2. Infrastructure Requirements

- **Operating System**: Linux (Ubuntu 22.04 LTS recommended), macOS, or Windows 11 with WSL2 / Docker Desktop.
- **Hardware Minimum**: 4 vCPU, 8 GB RAM, 20 GB SSD storage.
- **Docker**: Engine version 24.0+ and Docker Compose v2.20+.
- **Network Ports**:
  - `80`: Public HTTP / Nginx gateway
  - `8000`: Backend FastAPI direct (optional in internal network)
  - `3000`: Frontend SPA direct (optional in internal network)
  - `5432`: PostgreSQL database
  - `6379`: Redis cache

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

### Core Parameters

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `POSTGRES_USER` | PostgreSQL superuser username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` (change in prod) |
| `POSTGRES_DB` | Primary database name | `manabi` |
| `DATABASE_URL` | Asyncpg connection URL | `postgresql+asyncpg://postgres:postgres@postgres:5432/manabi` |
| `DATABASE_URL_SYNC` | Sync connection URL for migrations | `postgresql://postgres:postgres@postgres:5432/manabi` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing secret (32+ bytes) | `generate-random-32-byte-secret` |
| `LLM_PROVIDER` | Active LLM Gateway provider | `gemini` (or `openai`, `ollama`) |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-...` |
| `OLLAMA_BASE_URL` | External Ollama endpoint | `http://host.docker.internal:11434` |

---

## 4. Single-Command Launch (Docker Compose)

To build images and start all containerized services:

```bash
docker compose up --build -d
```

### Checking Status

```bash
docker compose ps
docker compose logs -f backend
```

---

## 5. Database Initialization & Seeding

When deploying to a fresh database, execute database schema migration and populate baseline roles, domain agents, and sample RAG documents:

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Seed initial roles, agents, and RAG knowledge
docker compose exec backend python -m app.database.seed
```

---

## 6. Verification & Health Monitoring

The platform provides dedicated health check and observability endpoints:

1. **Liveness Probe**:
   ```bash
   curl -I http://localhost:8000/health
   # HTTP/1.1 200 OK -> {"status": "healthy"}
   ```

2. **Readiness Probe** (validates PostgreSQL & Redis connectivity):
   ```bash
   curl http://localhost:8000/health/ready
   # {"status": "ready", "database": "connected", "redis": "connected"}
   ```

3. **Prometheus Metrics**:
   ```bash
   curl http://localhost:8000/metrics
   # Returns text/plain Prometheus 0.0.4 metrics stream
   ```

---

## 7. Load Testing Execution

To execute synthetic concurrency testing via Locust:

```bash
pip install locust
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://localhost:8000
```
