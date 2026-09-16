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

