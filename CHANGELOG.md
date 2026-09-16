# Changelog — MANABI (Agentic Intelligence & Learning Platform)

All notable changes and architectural phase completions are documented in this file.

---

## [Phase 1] - 2026-09-16

### Added
- **Infrastructure & Environment**:
  - Registered portable Git engine (v2.55.0) and Node.js LTS (v24.19.0) in user space.
  - Multi-container `docker-compose.yml` with PostgreSQL 16 + pgvector, Redis 7, Backend, Frontend, Worker, and Nginx.
  - Nginx reverse proxy configuration (`nginx/nginx.conf`) with SSE streaming support.
  - Complete `.gitignore`, `.env.example`, and production `README.md`.
  - Architecture Decision Records (ADRs 001–005) in `docs/adr/`.
- **Database Layer**:
  - Full PostgreSQL 16 + pgvector schema derived from Section 7 of the software engineering design doc.
  - SQLAlchemy 2.0 async models: `User`, `Role`, `Agent`, `AgentCapability`, `AgentExecution`, `ModelConfiguration`, `LLMUsage`, `Conversation`, `Message`, `Feedback`, `Document`, `DocumentVersion`, `DocumentChunk`, `Citation`, `Memory`, `ToolDefinition`, `ToolExecution`, `Evaluation`, `AuditEvent`.
  - Database seeding utility (`backend/app/database/seed.py`) with initial roles, test user, agents, and authoritative academic & engineering RAG corpora.
- **Model Gateway**:
  - Internal provider-agnostic `ModelGateway` with support for Google Gemini, OpenAI, and local external Ollama (zero containerization).
  - Bounded exponential backoff retries, fallback provider routing, latency measurement, cost/token tracking, and SSE streaming generator.
- **Agents & Stateful Workflows**:
  - Common `BaseAgent` contract with token budgeting and context construction conforming to Section 34.
  - High-velocity `IntentRouter` with deterministic keyword matching and structured JSON classification fallback.
  - Full-featured `AcademicAdvisorAgent` integrated with the LangGraph stateful `AcademicPlanReviewer` graph (`Student Data` → `Course Extraction` → `Prerequisite Verification` → `Workload Analysis` → `Risk Scorecard` → `Revised Plan`).
  - Abstract `AcademicDataProvider` interface with `MockAcademicDataProvider` (synthetic realistic records) and `ExternalCollegeAPIProvider` (graceful degradation, zero hallucination).
  - Full-featured `EngineeringArchitectAgent` with deterministic capacity calculator (`EngineeringCalculator` for QPS, storage, bandwidth, cache sizing, latency budgets) and validated Mermaid diagram generator.
  - Lightweight extensible agents: `CommerceAgent`, `ManagementAgent`, and `LawAgent` (with educational disclaimer).
  - Evidence-backed `MemoryManager` with gradual confidence escalation.
  - Structure-aware document chunker and pgvector RAG retriever with citation tracking.
- **FastAPI Modular Monolith API**:
  - Assembled `/api/v1` routes: `/auth`, `/users`, `/conversations` (with real-time SSE streaming), `/academic`, `/engineering`, `/memory`, `/agents`, `/health`.
  - Correlation ID middleware and strict CORS policy.
- **Testing**:
  - Test suites: `test_calculator.py`, `test_academic_provider.py`, `test_agents.py`, `test_chunker.py`, `test_memory.py` (13/13 passing).

---

## [Phase 2] - 2026-09-16

### Added
- **React + TypeScript + Tailwind CSS Frontend Application**:
  - Modern SPA built with React 18, TypeScript, Vite 5, Tailwind CSS, and Lucide React icons.
  - High-fidelity dark glassmorphism design system in `frontend/src/index.css` with smooth gradients, custom scrollbars, and micro-animations.
  - Global state management via Zustand (`frontend/src/stores/useAppStore.ts`) tracking active agent persona, current tab, streaming tokens, conversation sessions, and citations.
  - Asynchronous API client (`frontend/src/services/api.ts`) supporting fetch-based Server-Sent Events (SSE) streaming with cancellation and error resilience.
- **Components & Specialized Workspaces**:
  - `Navbar`: Displays platform branding, system status, active persona indicators, and view switcher tabs.
  - `Sidebar`: Dynamic agent selection (Academic, Engineering, Commerce, Management, Law), conversation session history, and infrastructure status indicators.
  - `ChatWindow` & `MessageBubble`: Real-time streaming conversation workspace with suggested domain prompts, role-based chat bubbles, and inline citation badges.
  - `CitationDrawer`: Slide-in grounding evidence panel displaying pgvector retrieved chunks, similarity match percentages, section anchors, and source documents.
  - `PlanReviewView`: Interactive academic advisor interface displaying official SIS student profile, live attendance threshold warnings (<75%), raw course plan submission, and LangGraph multi-step review scorecard.
  - `CalculatorView`: Deterministic system engineering capacity calculator dashboard for QPS & throughput, 3-year storage retention, network bandwidth, cache Pareto sizing, and SLA latency budgets.
  - `ArchitectureView` & `MermaidViewer`: Client-side Mermaid.js diagram viewer rendering platform architecture topologies and PostgreSQL entity-relationship diagrams.
  - `MemoryManagerView`: User-controlled memory inspection dashboard showing durable user attributes, confidence scores, observation counts, and deletion controls.
- **Frontend Infrastructure & Containerization**:
  - Multi-stage `frontend/Dockerfile` (Node 20 build stage -> Nginx Alpine production server).
  - Production `frontend/nginx.conf` with SPA client-side fallback routing.
- **Verification & Testing**:
  - Executed `tsc && vite build`: **0 errors**, 3,160 modules transformed, production assets generated cleanly.
  - Executed `pytest backend/tests -v`: **13 of 13 unit tests passed (100%)**.

---

## [Phase 3] - 2026-09-16

### Added
- **Observability & Prometheus Metrics (Section 38)**:
  - Thread-safe, pure-Python Prometheus metrics collector (`backend/app/observability/metrics.py`) implementing Counter, Gauge, and Histogram primitives without external dependencies.
  - Exposed `/metrics` endpoint on the FastAPI application exposing standard Prometheus 0.0.4 exposition format text.
  - Instrumenting metrics: `manabi_http_requests_total`, `manabi_http_request_duration_seconds`, `manabi_llm_requests_total`, `manabi_llm_latency_seconds`, `manabi_llm_tokens_total`, `manabi_rag_retrievals_total`, `manabi_tool_executions_total`, and `manabi_cache_operations_total`.
  - Structured JSON logging (`backend/app/observability/logger.py`) formatting application logs with ISO-8601 timestamps, correlation IDs, user IDs, model latencies, token counts, and error stack traces.
- **Benchmark Evaluation Framework (Section 39)**:
  - Multi-domain benchmark evaluation dataset (`backend/app/evaluation/datasets.py`) covering Academic, Engineering, Commerce, Management, and Law domains.
  - Information retrieval and accuracy metrics (`backend/app/evaluation/metrics.py`): Recall@K, Precision@K, Mean Reciprocal Rank (MRR), keyword coverage, deterministic numerical tolerance verification, and Mermaid syntax validation.
  - Automated benchmark evaluation runner (`backend/app/evaluation/runner.py`) achieving **88.89% routing accuracy**, **100% deterministic math accuracy**, **100% Mermaid syntax validity**, and **100% RAG Grounding Recall@3**.
- **Security Hardening (Section 29)**:
  - Input guardrails (`backend/app/security/guardrails.py`) scanning for and blocking prompt-injection attempts, DAN jailbreaks, and system instruction leaks.
  - Output boundary sanitizer redacting leaked API keys and authorization bearer tokens.
  - Document access control layer verifying user role hierarchy (student/faculty/admin) and document governance status (active/superseded/archived).
  - Rate limiting sliding-window helper with Redis backend and graceful local fallback.
- **Load Testing & Documentation (Sections 40, 45, 49)**:
  - Locust load-testing script (`tests/load/locustfile.py`) simulating concurrent user sessions across health, calculator, diagram, and plan review endpoints.
  - Requirements Traceability Matrix (`docs/REQUIREMENTS_TRACEABILITY.md`) mapping all 50 design doc sections to architecture components, database entities, APIs, and tests.
  - Comprehensive Deployment Guide (`docs/deployment/DEPLOYMENT_GUIDE.md`) with topology diagram, Docker Compose instructions, and operational runbooks.
- **Verification & Testing**:
  - Expanded backend test suite from 13 to **27 automated tests** across 8 test modules (`test_observability.py`, `test_security.py`, `test_evaluation.py`, `test_academic_provider.py`, `test_agents.py`, `test_calculator.py`, `test_chunker.py`, `test_memory.py`).
  - **100% pass rate (27/27 passed in 1.79s)**.


