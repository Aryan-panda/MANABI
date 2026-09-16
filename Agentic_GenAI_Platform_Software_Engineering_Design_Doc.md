# Agentic GenAI Platform — Software Engineering Design Document

## 0. Senior Development Build Directive

You are the **Senior Software Engineer, GenAI Engineer, System Architect, Database Architect, Security Engineer, QA Engineer, and DevOps Engineer** responsible for implementing this system.

Build the project according to this document as the source of truth.

### Non-negotiable rules
- Do not invent missing business requirements, college APIs, credentials, schemas, or undocumented external behavior.
- If a critical requirement is genuinely missing, stop and ask before implementing it.
- Use a **modular monolith**, not premature microservices.
- Use **Docker + Docker Compose** for project infrastructure.
- **Do not use Kubernetes.**
- **Do not deploy or containerize Ollama.** Ollama is an optional external LLM provider accessed through a configurable API endpoint.
- Do not add Kafka, a separate vector database, or other infrastructure unless a measured requirement justifies it.
- Do not create agents merely to increase the agent count.
- RAG must be used only where external knowledge grounding is useful.
- Conversation history, user memory, structured college data, and RAG knowledge are separate concepts.
- Important numerical calculations must use deterministic tools, not unsupported LLM arithmetic.
- Never fabricate unavailable college data or policy.
- Every implementation decision must have a clear reason.

---

# 1. Product Definition

Build a multi-domain Agentic GenAI Assistant Platform.

## Full-featured agents
1. Academic Advisor
2. Engineering Architect

## Lightweight agents
3. Commerce
4. Management
5. Law

Commerce, Management, and Law initially provide domain-aware conversational assistance. Their architecture must allow RAG, tools, memory, and workflows to be added later without redesigning the platform.

---

# 2. Technology Stack

## Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Zustand
- Vitest
- React Testing Library
- Playwright

## Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- pytest

## GenAI
- LangChain
- LangGraph
- Internal LLM Provider abstraction
- Gemini provider
- OpenAI provider
- Ollama provider

## Data
- PostgreSQL
- pgvector
- Redis

## Infrastructure
- Docker
- Docker Compose
- Nginx

## CI/CD
- GitHub
- GitHub Actions

## Testing / performance
- pytest
- Vitest
- Playwright
- Locust or k6

## Diagrams
- Mermaid

## Explicitly excluded
- Kubernetes
- Dockerized Ollama
- Kafka initially
- separate vector database
- unnecessary microservices

---

# 3. Architectural Style

Use a **modular monolith**.

High-level flow:

User
→ React + TypeScript + Tailwind
→ Nginx
→ FastAPI
→ Intent Router
→ Agent Runtime
→ RAG / Memory / Tools
→ Model Gateway
→ Gemini / OpenAI / external Ollama

PostgreSQL is the persistent system of record.

Redis provides cache, rate limiting, ephemeral data, and background-job coordination where justified.

---

# 4. Repository Architecture

Use this structure as the baseline:

project/
- frontend/
  - src/
    - components/
    - pages/
    - layouts/
    - hooks/
    - services/
    - stores/
    - types/
    - utils/
- backend/
  - app/
    - main.py
    - api/
    - agents/
      - base.py
      - router.py
      - academic/
      - engineering/
      - commerce/
      - management/
      - law/
    - rag/
      - ingestion/
      - retrieval/
      - chunking/
      - embeddings/
      - citations/
    - memory/
    - tools/
    - llm/
      - base.py
      - gateway.py
      - providers/
    - academic_data/
      - interface.py
      - mock.py
      - external_api.py
    - database/
    - cache/
    - security/
    - observability/
    - evaluation/
    - config/
  - migrations/
  - tests/
- docs/
  - architecture/
  - api/
  - database/
  - agents/
  - rag/
  - adr/
  - deployment/
- nginx/
- .github/workflows/
- docker-compose.yml
- .env.example
- README.md

Keep domain logic out of API route handlers.

---

# 5. Frontend Design

React + TypeScript + Tailwind CSS.

Responsibilities:
- authentication UI
- agent selection
- chat interface
- streaming responses
- conversation history
- citations
- academic planning/review UI
- engineering architecture output
- Mermaid diagrams
- memory management
- loading/error states
- responsive layout

Use TanStack Query for server state and Zustand only for appropriate client state.

Do not duplicate server state unnecessarily in Zustand.

---

# 6. Backend Design

FastAPI is the platform backend.

Main modules:
- authentication
- users
- conversations
- agents
- academic
- engineering
- RAG
- memory
- tools
- LLM gateway
- evaluation
- observability

Use Pydantic request/response models.

API routes must call application/domain services rather than directly implementing business logic.

---

# 7. Database Design

Use PostgreSQL + pgvector.

The schema must be derived from actual requirements but initially support:

## users
- id UUID PK
- email
- name
- password_hash or external_auth_id
- role_id FK
- is_active
- created_at
- updated_at

## roles
- id
- name

## agents
- id
- name
- description
- configuration
- is_active
- created_at
- updated_at

## agent_capabilities
- id
- agent_id FK
- capability
- configuration

## conversations
- id UUID PK
- user_id FK
- agent_id FK
- title
- status
- created_at
- updated_at

## messages
- id UUID PK
- conversation_id FK
- role
- content
- model
- token_count
- created_at

## documents
- id
- title
- domain
- document_type
- source
- access_level
- status
- created_at
- updated_at

## document_versions
- id
- document_id FK
- version
- effective_date
- content_hash
- created_at

## document_chunks
- id
- document_version_id FK
- chunk_index
- section
- subsection
- page
- text
- embedding
- metadata
- created_at

## citations
- id
- execution_id FK
- chunk_id FK
- relevance information
- created_at

## memories
- id
- user_id FK
- type
- key
- value
- confidence
- evidence_count
- last_seen
- created_at
- updated_at

## tool_definitions
- id
- name
- description
- input_schema
- output_schema
- permissions
- is_active

## tool_executions
- id
- execution_id FK
- tool_id FK
- input
- output
- status
- latency
- created_at

## agent_executions
- id
- conversation_id FK
- agent_id FK
- execution_id
- status
- started_at
- completed_at
- latency

## model_configurations
- id
- provider
- model
- configuration
- is_active

## llm_usage
- id
- execution_id FK
- provider
- model
- input_tokens
- output_tokens
- estimated_cost
- latency
- created_at

## feedback
- id
- user_id FK
- conversation_id FK
- message_id FK
- rating/feedback type
- comment
- created_at

## evaluations
- id
- agent_id FK
- dataset/version
- metric
- score
- execution information
- created_at

## audit_events
- id
- user_id
- event_type
- resource_type
- resource_id
- metadata
- created_at

Use:
- PK/FK constraints
- unique constraints
- check constraints
- indexes based on query patterns
- appropriate cascade behavior
- timestamps
- soft deletion only where justified
- Alembic migrations

Do not blindly create unused tables; simplify where requirements do not need a proposed entity.

---

# 8. RAG Architecture

RAG is for external knowledge.

It is NOT conversation memory.

Pipeline:

Document
→ validation
→ extraction
→ structure detection
→ structure-aware chunking
→ metadata
→ embedding
→ PostgreSQL + pgvector

Retrieval:

Question
→ agent/task understanding
→ retrieval policy
→ metadata filtering
→ vector/keyword retrieval
→ optional reranking
→ context assembly
→ LLM
→ answer + citations

Chunks must be meaningful logical units, not arbitrary fixed-size text.

Evaluate chunking strategies before finalizing the production strategy.

---

# 9. Academic RAG Corpus

Use authoritative institutional material such as:
- Student Handbook
- Academic Regulations
- Attendance Policy
- Examination Regulations
- Academic Calendar
- Program Curriculum
- Course Catalog
- Course Syllabi
- Grading Regulations
- Academic Procedures
- Leave / Medical / Condonation Rules
- Academic Integrity Policy
- Disciplinary Regulations
- Faculty Directory
- Department / School Information
- Academic Support Resources
- Scholarship information where relevant

Never invent institutional rules.

Document metadata should support:
- domain
- school
- department
- program
- course
- topic
- version
- effective date
- source
- access level
- page
- section

---

# 10. Engineering RAG Corpus

Start with curated authoritative technical documentation:
- PostgreSQL
- Redis
- FastAPI
- Python
- Java
- Spring Boot
- Docker
- Nginx
- React
- TypeScript
- GitHub Actions
- LangChain
- LangGraph
- relevant LLM provider documentation
- OWASP
- relevant HTTP/API standards

Books are primarily learning resources for the developer and should not automatically be dumped into the production RAG corpus.

Technical documentation must be version-aware where appropriate.

---

# 11. Academic Advisor

The Academic Advisor is a full-featured agent.

Capabilities:
- academic policy questions
- attendance guidance
- curriculum questions
- course planning
- semester planning
- study planning
- personalized recommendations
- skill-aware recommendations
- plan generation
- plan review
- faculty/resource discovery
- curriculum analysis
- institution-procedure guidance based only on official sources
- student data lookup through an abstract provider

Architecture:

User
→ Academic Agent
→ task classification
→ relevant workflow
→ RAG / memory / academic-data tools
→ LLM reasoning
→ validation
→ citations
→ response

---

# 12. Academic Plan Reviewer

Implement a structured workflow:

Plan
→ task extraction
→ prerequisite/dependency analysis
→ workload analysis
→ skill-gap analysis
→ goal alignment
→ risk identification
→ revised plan
→ validation

Output should contain:
- current plan summary
- detected issues
- evidence/reasoning
- dependencies
- risks
- suggested changes
- revised plan

Use LangGraph for this stateful workflow.

---

# 13. College API Abstraction

Do not require a real college API to run the platform.

Define:

AcademicDataProvider

with methods such as:
- get_student_profile()
- get_courses()
- get_attendance()
- get_results()
- get_schedule()

Implement:
- MockAcademicDataProvider
- ExternalCollegeAPIProvider

Later a real institutional adapter can implement the same interface.

If the external college API is absent:
- the application must still work for general academic RAG and LLM functionality;
- features requiring live student-specific data must return a controlled "student data integration unavailable" response;
- never fabricate student data.

The provider must be dependency-injected so the rest of the Academic Agent does not depend on a specific college.

---

# 14. Engineering Architect

This is a full-featured technical architecture agent.

Capabilities:
- system design
- database design
- ER diagrams
- API design
- architecture review
- technology comparison
- scalability analysis
- caching decisions
- asynchronous processing
- deployment architecture
- project planning
- prompt engineering
- code architecture
- debugging
- architecture critique
- Mermaid diagrams
- repository/code analysis when a repository is supplied

Workflow:

Requirements
→ assumptions
→ architecture
→ capacity estimation
→ database
→ API
→ cache
→ async processing
→ deployment
→ failure analysis
→ security
→ testing
→ trade-offs
→ final design

---

# 15. Engineering Technology Knowledge

Backend:
- Python/FastAPI
- Java/Spring Boot
- Node.js

Frontend:
- React
- TypeScript
- Tailwind CSS

Data:
- PostgreSQL
- Redis

Infrastructure:
- Docker
- Nginx
- GitHub Actions

Distributed systems:
- caching
- queues
- load balancing
- WebSockets
- microservices when genuinely justified

GenAI:
- LLM APIs
- RAG
- LangChain
- LangGraph
- agents
- evaluation
- Ollama

Security:
- OWASP
- API security
- JWT/OAuth concepts
- secrets management

Java/Spring Boot is a supported Engineering stack, not the platform backend.

---

# 16. Engineering Calculator Tool

Implement deterministic calculation tools for:
- QPS
- storage
- bandwidth
- capacity
- latency budgets
- cache sizing
- database estimates

Use Python for calculations.

The LLM should explain verified calculator results rather than performing important numerical calculations unreliably itself.

---

# 17. Diagram Generation

Engineering outputs should support Mermaid.

Examples:
- system architecture
- sequence diagrams
- ER diagrams
- deployment diagrams
- data flows

The backend generates validated Mermaid text; the React frontend renders it.

---

# 18. Lightweight Agents

Commerce, Management, and Law initially use:
- dedicated system instructions
- domain-aware prompts
- conversation context
- common Model Gateway

They should NOT initially receive unnecessary RAG/tools/workflows.

Law responses must be framed as educational/informational assistance, not a substitute for professional legal advice.

Their code must conform to the same BaseAgent contract so they can be upgraded later.

---

# 19. Agent Contract

All agents implement a common interface containing:
- identity
- purpose
- capabilities
- allowed_tools
- retrieval_policy
- system_prompt
- output_schema
- safety_policy
- execution_policy

The router selects the agent; the agent owns its domain behavior.

---

# 20. Intent Router

Use structured classification.

Example:

{
  "agent": "engineering",
  "task": "system_design",
  "confidence": 0.94
}

The router should not contain domain logic.

Ambiguous requests should have a defined fallback/clarification strategy.

---

# 21. LangGraph Usage

Use LangGraph for stateful workflows, especially:
- academic plan review
- academic plan generation where multi-step validation is needed
- engineering architecture workflow

Do not force every simple chat request through a complex graph.

---

# 22. LangChain Usage

Use LangChain where it provides useful reusable abstractions:
- model integrations
- prompts
- structured output
- retrievers
- tool integration

Do not use LangChain merely to add a dependency.

Maintain a clean internal architecture around it.

---

# 23. Conversation State vs Memory vs RAG

Keep them separate:

Conversation State:
- current conversation
- recent messages
- workflow state
- PostgreSQL/LangGraph state

User Memory:
- durable user preferences/skills/facts
- PostgreSQL
- confidence/evidence-based
- user-correctable

RAG:
- external institutional/technical knowledge
- PostgreSQL + pgvector

Never treat retrieved documents as user memory.

---

# 24. Memory Design

Memory records should contain evidence and confidence.

Example:
- key: Java
- value: intermediate
- confidence: medium
- evidence_count: 4

Do not infer strong expertise from one interaction.

Provide user controls for reviewing/correcting/removing memory.

---

# 25. Model Gateway

All agents call the internal Model Gateway rather than directly coupling themselves to an LLM provider.

Interface:

LLMProvider
- GeminiProvider
- OpenAIProvider
- OllamaProvider

Responsibilities:
- provider selection
- model configuration
- authentication
- timeout
- retry
- exponential backoff
- optional fallback
- token tracking
- cost tracking
- rate limiting
- structured logging

Ollama:
- external service only
- configurable base URL
- configurable model
- no container
- no model download

---

# 26. API Design

Base path:

/api/v1

Authentication:
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

Users:
- GET /users/me
- PATCH /users/me

Conversations:
- POST /conversations
- GET /conversations
- GET /conversations/{id}
- DELETE /conversations/{id}
- POST /conversations/{id}/messages

Agents:
- GET /agents
- GET /agents/{agent_id}

Academic:
- GET /academic/profile
- GET /academic/courses
- GET /academic/attendance
- GET /academic/results
- POST /academic/plan/review
- POST /academic/plan/generate

Engineering:
- POST /engineering/design
- POST /engineering/review
- POST /engineering/debug
- POST /engineering/plan

Memory:
- GET /memory
- POST /memory
- PATCH /memory/{id}
- DELETE /memory/{id}

Health:
- GET /health
- GET /health/ready

Use consistent response/error schemas and API versioning.

---

# 27. Streaming

Use SSE initially for LLM response streaming.

React
→ FastAPI
→ LLM
→ streamed tokens
→ SSE
→ React

Use WebSockets only if true bidirectional realtime requirements emerge.

---

# 28. Authentication and Authorization

Initially implement:
- JWT authentication
- refresh tokens
- RBAC
- student/admin/developer roles as required

Authorization must occur before accessing protected student data or protected RAG documents.

---

# 29. Security

Implement:
- input validation
- authentication
- authorization
- rate limiting
- secret management
- restrictive CORS
- SQL injection prevention
- prompt-injection defenses
- document access control
- audit logging
- LLM output validation
- tool permission checks

Retrieved documents are untrusted data, not system instructions.

Never expose secrets to the model.

---

# 30. Redis

Use Redis only for justified ephemeral workloads:
- rate limiting
- short-lived cache
- temporary workflow state where appropriate
- job queue
- distributed locks where necessary

PostgreSQL remains the source of truth.

Do not store critical permanent data only in Redis.

---

# 31. Background Worker

Use Python workers with Redis-backed job coordination for:
- document ingestion
- embedding generation
- batch evaluation
- other expensive asynchronous work

Do not introduce Kafka initially.

---

# 32. Caching

Potential cache targets:
- frequently requested non-sensitive data
- model metadata
- selected technical retrieval results
- temporary workflow data

Every cache must define:
- key
- TTL
- invalidation strategy
- stale-data policy

Never cache private data without considering authorization and user isolation.

---

# 33. Nginx

Initial:

Internet
→ Nginx
→ FastAPI

If measured load later requires multiple backend replicas:

Nginx
→ FastAPI #1
→ FastAPI #2
→ FastAPI #3

Use load balancing only when justified by actual deployment/load requirements.

No Kubernetes.

---

# 34. Context Engineering

Construct model context from:
1. system constraints
2. agent instructions
3. current user request
4. relevant tool results
5. relevant RAG evidence
6. relevant recent conversation
7. relevant user memory

Do not blindly send the entire conversation.

Implement token/context budgets.

---

# 35. Failure Handling

External LLM:
- timeout
- bounded retry
- exponential backoff
- optional configured fallback
- controlled error

College API:
- timeout
- bounded retry
- optional safe cache
- controlled unavailable response

Redis:
- caching should degrade where possible
- critical persistent data remains PostgreSQL

Never silently replace missing authoritative data with fabricated information.

---

# 36. Idempotency

Use idempotency where repeated execution could create duplicates or side effects:
- document ingestion
- memory creation
- external API mutations
- tool operations with side effects

---

# 37. Document Governance

Documents must support:
- source
- version
- effective date
- upload date
- content hash
- access level
- status

Statuses:
- draft
- active
- superseded
- archived

Retrieval should prefer the appropriate active/effective version.

---

# 38. Observability

Use structured logs and correlation IDs.

Track:
- request_id
- user_id
- conversation_id
- agent_id
- execution_id
- provider
- model
- latency
- token usage
- errors
- retrieval latency
- tool latency
- cache hits/misses

A single request must be traceable through API → agent → RAG → tool → LLM.

---

# 39. Evaluation

Build explicit evaluation datasets.

Academic:
- policy questions
- attendance
- course planning
- study planning
- plan review
- grounding
- citation correctness

Engineering:
- system design
- database design
- API design
- scalability
- architecture critique
- technology selection
- numerical calculations

Measure:
- correctness
- groundedness
- retrieval relevance
- citation correctness
- tool correctness
- structured-output validity
- latency
- token usage

For RAG evaluate:
- Recall@K
- Precision@K
- MRR
- retrieval relevance
- answer faithfulness
- citation accuracy

Do not claim quality without evaluation evidence.

---

# 40. Load Testing

Use Locust or k6.

Measure:
- p50 latency
- p95 latency
- p99 latency
- requests/sec
- error rate
- LLM concurrency
- PostgreSQL performance
- Redis performance

Only introduce scaling infrastructure based on measurements.

---

# 41. Frontend Testing

Use:
- Vitest
- React Testing Library
- Playwright

Test:
- routing
- authentication
- chat
- streaming
- citations
- agent selection
- academic planning
- engineering diagrams
- errors
- responsive behavior

---

# 42. Backend Testing

Use pytest.

Test:
- unit logic
- API endpoints
- database integration
- authentication
- authorization
- RAG retrieval
- agent routing
- workflows
- tools
- model gateway
- college API adapters
- failure cases
- security cases

AI tests should focus on properties/evaluation criteria rather than exact natural-language strings.

---

# 43. Docker Architecture

Docker Compose should provide:

- frontend
- backend
- postgres
- redis
- nginx
- worker

Ollama is NOT included.

Use internal Docker networking.

Environment variables include:

DATABASE_URL
REDIS_URL
LLM_PROVIDER
GEMINI_API_KEY
OPENAI_API_KEY
OLLAMA_BASE_URL
OLLAMA_MODEL
JWT_SECRET

Never commit secrets.

---

# 44. CI/CD

GitHub Actions pipeline:

Push / Pull Request
→ lint
→ type checks
→ backend tests
→ frontend tests
→ integration tests
→ frontend build
→ Docker build
→ security checks
→ deployment when configured

Teach and implement GitHub Actions properly; do not merely generate unexplained YAML.

---

# 45. Requirements Traceability

Maintain a matrix:

Requirement
→ Architecture component
→ API/module
→ database entity
→ test
→ evaluation metric

Every major feature should be traceable from requirement to implementation and validation.

---

# 46. Architecture Decision Records

Create ADRs for significant choices, including:
- modular monolith
- PostgreSQL + pgvector
- Redis usage
- FastAPI
- LangGraph scope
- Model Gateway
- external Ollama
- College API abstraction
- SSE
- Nginx
- no Kubernetes
- no Kafka initially

Each ADR must state:
- context
- decision
- alternatives
- consequences

---

# 47. Development Order

Implement in this exact order unless a dependency requires adjustment:

1. Repository and project scaffolding
2. Docker Compose
3. PostgreSQL
4. Database schema
5. Alembic migrations
6. FastAPI foundation
7. API contracts
8. Authentication
9. Users/conversations/messages
10. Raw LLM integration
11. Model Gateway
12. Basic React chat
13. Streaming
14. RAG ingestion
15. pgvector retrieval
16. citations
17. Academic Advisor
18. Academic data provider abstraction + mock provider
19. Academic workflows
20. Academic plan reviewer
21. Engineering Architect
22. Engineering RAG
23. Engineering calculator
24. Mermaid architecture output
25. Memory
26. Lightweight agents
27. Redis
28. Background worker
29. Security hardening
30. Observability
31. Evaluation
32. Automated testing
33. Load testing
34. Nginx deployment
35. GitHub Actions CI/CD
36. Documentation
37. Final architecture review

At every phase:
- implement
- test
- explain
- verify
- document
before moving forward.

---

# 48. Senior Engineering Rules

Do not:
- add technology because it sounds impressive;
- create unnecessary agents;
- hardcode institution-specific data;
- put business logic in routes;
- couple agents directly to providers;
- mix memory with RAG;
- use Redis as a permanent database;
- use LLMs for deterministic calculations;
- claim RAG quality without evaluation;
- blindly trust retrieved content;
- expose secrets;
- introduce Kubernetes without a real requirement.

Prefer:
- simple architecture
- explicit interfaces
- dependency injection
- typed contracts
- deterministic tooling
- measured optimization
- tests
- observability
- documented trade-offs
- incremental implementation

---

# 49. Definition of Done

The project is complete only when:

- frontend works with React + TypeScript + Tailwind;
- backend works with FastAPI;
- PostgreSQL schema and migrations are implemented;
- pgvector RAG works;
- Redis is used only where justified;
- Academic Advisor is fully functional;
- Engineering Architect is fully functional;
- Commerce/Management/Law are lightweight but extensible;
- college integration works through a mock provider without requiring a real college API;
- missing college API does not break general academic RAG/LLM functionality;
- Gemini/OpenAI provider abstraction works;
- external Ollama provider is supported without containerizing Ollama;
- LangGraph is used for appropriate workflows;
- LangChain is used where useful;
- Java/Spring Boot is supported knowledge within Engineering;
- Mermaid diagrams work;
- deterministic engineering calculations work;
- authentication/authorization works;
- citations work;
- memory is separate from RAG;
- Docker Compose runs the stack;
- no Kubernetes is used;
- automated tests exist;
- evaluation datasets and metrics exist;
- observability exists;
- load testing has been performed;
- CI/CD is implemented;
- documentation is complete.

---

# 50. Final Instruction to the AI Developer

You are not being asked to produce a superficial demo.

Build this as a serious software-engineering and GenAI engineering project.

Before writing code:
1. inspect the repository;
2. inspect existing dependencies/configuration;
3. identify what already exists;
4. reconcile existing code with this design;
5. create/update architecture and ADR documentation;
6. identify only genuinely missing information.

Then implement incrementally.

For every implementation:
- explain what is being built;
- explain why;
- show the relevant architecture;
- implement it cleanly;
- write tests;
- run the tests;
- fix failures;
- document the result;
- then continue.

Never invent unavailable APIs, credentials, institutional data, or requirements.

If the real college API is not provided, use MockAcademicDataProvider and keep the ExternalCollegeAPIProvider interface ready for later integration.

The goal is a maintainable, testable, extensible **Agentic GenAI platform**, not a collection of buzzword technologies.
