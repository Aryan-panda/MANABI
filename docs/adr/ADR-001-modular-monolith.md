# ADR-001: Modular Monolith Architecture

## Status
Accepted

## Context
MANABI provides multi-domain agentic capabilities (Academic Advisory, Engineering Architecture, Commerce, Management, Law) along with shared platform capabilities (authentication, model gateway, pgvector RAG, evidence-based memory, and deterministic calculation tools). A common architectural mistake in GenAI applications is premature decomposition into microservices, which increases operational overhead, network latency, distributed transaction complexity, and deployment fragility without actual scale requirements.

## Decision
Adopt a **Modular Monolith** architecture:
- All domain modules (academic, engineering, commerce, management, law) and platform services (auth, RAG, memory, LLM gateway) reside within a single codebase and deployment unit (`FastAPI`).
- Internal module boundaries are strictly enforced through explicit interfaces and dependency injection.
- API route handlers remain thin and delegate directly to domain services.
- Shared persistence is maintained in PostgreSQL.

## Alternatives Considered
1. **Microservices from day one**:
   - *Rejected*: Incurs massive distributed-systems complexity, RPC latency between agents and LLM gateways, multi-repo or complex mono-repo tooling, and elevated infrastructure costs without measured traffic justification.
2. **Loosely coupled scripts / Serverless functions**:
   - *Rejected*: Lacks cohesion, impedes stateful workflow execution (e.g., LangGraph graphs), and makes centralized connection pooling (PostgreSQL/Redis) problematic.

## Consequences
- **Positive**: Single codebase, straightforward local development, simplified Docker Compose deployment, transactional consistency across PostgreSQL entities, zero network serialization latency between internal modules.
- **Negative**: Requires strict discipline to prevent cross-module coupling; if one module requires separate horizontal scaling in the future, it must be extracted then based on telemetry.
