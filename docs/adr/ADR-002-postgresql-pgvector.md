# ADR-002: PostgreSQL with pgvector for Relational and Vector Data

## Status
Accepted

## Context
MANABI requires persistent storage for transactional data (users, auth, conversations, messages, feedback, audit logs) and external knowledge embeddings for RAG retrieval (academic documents, institutional policies, engineering manuals). Introducing a separate standalone vector database (such as Pinecone, Qdrant, Milvus, or Weaviate) introduces dual-database synchronization challenges, fragmented backup/restore cycles, network overhead, and unnecessary licensing or infrastructure costs.

## Decision
Use **PostgreSQL with the pgvector extension** as the single persistent source of record for both relational entities and vector embeddings.
- Vector distance metrics: Cosine distance (`<=>`) or Inner Product (`<#>`).
- Chunk embeddings stored alongside metadata and document version foreign keys.
- HNSW or IVFFlat indexes created on embedding columns for fast sub-linear similarity search.

## Alternatives Considered
1. **Dedicated Vector Database (Pinecone / Weaviate / Qdrant)**:
   - *Rejected*: Incurs additional operational cost, dual-write consistency issues, and breaks relational joins between documents, chunks, citations, and conversation executions.
2. **PostgreSQL Full-Text Search alone**:
   - *Rejected*: Lacks semantic similarity matching necessary for unstructured policy and engineering retrieval.

## Consequences
- **Positive**: Single transactional backup/restore, ACID compliance, zero sync lag between document metadata and chunk vectors, simplified Docker Compose setup.
- **Negative**: For multi-billion vector scale, PostgreSQL requires vertical memory scaling or dedicated vector partitioning, which is far beyond the initial scale requirement.
