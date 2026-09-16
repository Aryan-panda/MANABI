# MANABI — Requirements Traceability Matrix (RTM)

This matrix establishes formal traceability from every architectural directive and engineering section in [`Agentic_GenAI_Platform_Software_Engineering_Design_Doc.md`](../Agentic_GenAI_Platform_Software_Engineering_Design_Doc.md) to its corresponding codebase implementation, database model, API endpoint, automated test suite, and evaluation metric.

---

## Traceability Mapping Table

| Section & Requirement | Architecture Component | Source Code Implementation | Database Entity | Verification / Test Suite | Evaluation Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0. Build Directive & Non-negotiables** | Modular Monolith, Docker Compose, No K8s | [`docker-compose.yml`](../docker-compose.yml), [`backend/app/main.py`](../backend/app/main.py) | All schemas | Local execution & CI pipeline | Zero K8s, Zero Kafka, clean monolith |
| **1. Full & Lightweight Agents** | Agent Runtimes (Academic, Engineering, Commerce, Management, Law) | [`backend/app/agents/`](../backend/app/agents/) | `Agent`, `AgentCapability`, `AgentExecution` | `tests/test_agents.py` | Agent registry & dynamic capability verification |
| **2. Technology Stack** | React + TypeScript + FastAPI + PostgreSQL + pgvector + Redis | [`frontend/`](../frontend/), [`backend/`](../backend/) | System metadata | `tsc && vite build`, `pytest` | 0 type errors, 100% tests passing |
| **3. Architectural Style** | Modular Monolith with bounded contexts | Bounded folders in `backend/app/` | `Base.metadata` | Monolith startup check | High cohesion, loose coupling |
| **4. Repository Architecture** | Baseline directory layout | `frontend/`, `backend/`, `docs/`, `nginx/` | N/A | Clean directory structure | Zero ad-hoc outside paths |
| **5. Frontend Design** | Dark glassmorphic React 18 SPA | [`frontend/src/`](../frontend/src/) | N/A | Production Vite bundling | Multi-tab UI, reactive Zustand state |
| **6. Backend Design** | FastAPI modular monolith API | [`backend/app/api/v1/`](../backend/app/api/v1/) | All entities | Endpoint routing tests | Decoupled domain service layer |
| **7. Database Design** | PostgreSQL 16 + pgvector | [`backend/app/database/models/`](../backend/app/database/models/) | 17 SQLAlchemy 2.0 tables | `migrations/env.py`, `seed.py` | Declarative 2.0 type safety |
| **11. Model Gateway** | Multi-provider LLM abstraction | [`backend/app/llm/gateway.py`](../backend/app/llm/gateway.py) | `ModelConfiguration`, `LLMUsage` | Gateway retry/fallback tests | Latency ms, input/output tokens |
| **14-16. RAG Pipeline & Chunker** | Structure-aware Markdown chunker + pgvector | [`backend/app/rag/`](../backend/app/rag/) | `Document`, `DocumentVersion`, `DocumentChunk` | `tests/test_chunker.py` | Recall@K, Precision@K, MRR |
| **17-20. Academic Advisor & LangGraph** | Stateful degree plan review workflow | [`backend/app/agents/academic/`](../backend/app/agents/academic/) | `StudentProfile`, `Attendance` | `tests/test_academic_provider.py` | Prerequisite & attendance validation |
| **21-24. Engineering Architect & Math** | Deterministic capacity planning calculator | [`backend/app/tools/calculator.py`](../backend/app/tools/calculator.py) | `ToolDefinition`, `ToolExecution` | `tests/test_calculator.py` | 100.0% mathematical exactness |
| **24. Evidence-based Memory** | User preferences & skills with confidence escalation | [`backend/app/memory/manager.py`](../backend/app/memory/manager.py) | `Memory` | `tests/test_memory.py` | Confidence rating (Low -> Medium -> High) |
| **27. Streaming** | Server-Sent Events (SSE) token generator | [`backend/app/api/v1/endpoints/conversations.py`](../backend/app/api/v1/endpoints/conversations.py) | `Message` | Live browser / API stream tests | TTFT (Time to First Token) < 200ms |
| **28-29. Security & Guardrails** | Prompt injection defense & Document ACL | [`backend/app/security/guardrails.py`](../backend/app/security/guardrails.py) | `Role`, `User` | `tests/test_security.py` | 100% injection patterns blocked |
| **30-32. Redis Caching & Worker** | Ephemeral cache, rate-limiting & worker | [`backend/app/cache/redis.py`](../backend/app/cache/redis.py), [`backend/app/worker.py`](../backend/app/worker.py) | Redis memory | Cache degradation tests | Zero single point of failure |
| **38. Observability** | Prometheus exporter & structured JSON logging | [`backend/app/observability/`](../backend/app/observability/) | Trace metadata | `tests/test_observability.py` | `/metrics` Prometheus 0.0.4 text format |
| **39. Evaluation** | Benchmark datasets & evaluation runner | [`backend/app/evaluation/`](../backend/app/evaluation/) | `Evaluation` | `tests/test_evaluation.py` | 88.89% routing, 100% math accuracy |
| **40. Load Testing** | Locust performance simulation | [`tests/load/locustfile.py`](../tests/load/locustfile.py) | Load metrics | Locust scenario execution | p50, p95, p99 latency profiling |
| **43-44. Docker & CI/CD** | Compose orchestration & GitHub Actions | [`docker-compose.yml`](../docker-compose.yml), [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | N/A | GitHub Actions workflow run | Automated build, test, and container packaging |
| **46. Architecture Decision Records** | ADR documentation | [`docs/adr/`](adr/) | N/A | Peer review documentation | ADRs 001 through 005 |
