# ADR-005: Scoped LangGraph Usage for Stateful Workflows

## Status
Accepted

## Context
Agent workflows can range from simple single-turn informational queries (e.g. "What is the penalty for plagiarism?") to complex, multi-stage stateful evaluations (e.g. reviewing an entire degree plan against prerequisites, credit limits, semester workload balance, and risk factors). Forcing every simple query through an elaborate state machine introduces unnecessary latency and token overhead, while managing complex review workflows with simple linear chains leads to fragile prompting and uncontrolled execution.

## Decision
Apply **LangGraph selectively** only for multi-step, stateful, cyclically verifiable workflows:
- **Academic Plan Reviewer**:
  - `Task Extraction` → `Prerequisite & Dependency Analysis` → `Workload & Credit Analysis` → `Skill-Gap Analysis` → `Risk Identification` → `Plan Revision & Validation`.
- **Engineering Architecture Workflow**:
  - `Requirements Extraction` → `Capacity Estimation` → `Data Modeling & Mermaid ERD Generation` → `Trade-off & Failure Analysis`.
- **General conversational turns**:
  - Route through standard Intent Router and direct single-pass agent generation with RAG context assembly, keeping latency minimal and predictable.

## Alternatives Considered
1. **LangGraph for all conversational turns**:
   - *Rejected*: Over-engineers simple FAQ/policy Q&A, increasing p95 latency.
2. **Hardcoded Python scripts without graph abstractions**:
   - *Rejected*: Fails to provide visualizable state inspection, checkpointing, and branch rollback capabilities for plan revisions.

## Consequences
- **Positive**: Blazing fast responses for simple questions; structured, verifiable, resilient execution for complex academic and engineering planning.
