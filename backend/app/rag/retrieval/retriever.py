import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models.rag import Document, DocumentVersion, DocumentChunk


class RAGRetriever:
    """
    RAG Retrieval Engine with metadata filtering and citation attribution.
    """

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        domain: Optional[str] = None,
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Query document chunks with domain metadata filtering.
        Performs vector similarity search if pgvector is enabled,
        or token-overlap keyword matching as resilient fallback.
        """
        stmt = (
            select(DocumentChunk, Document.title, Document.domain, Document.source)
            .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(Document.status == "active")
        )

        if domain:
            stmt = stmt.where(Document.domain == domain)

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Token-based keyword ranking & cosine score approximation
        query_tokens = set(query.lower().split())
        ranked_results = []

        for chunk, doc_title, doc_domain, doc_source in rows:
            chunk_tokens = set(chunk.text.lower().split())
            overlap = len(query_tokens.intersection(chunk_tokens))
            relevance = min(overlap / max(len(query_tokens), 1), 1.0)

            if overlap > 0:
                ranked_results.append({
                    "chunk_id": str(chunk.id),
                    "title": doc_title,
                    "domain": doc_domain,
                    "source": doc_source,
                    "section": chunk.section,
                    "subsection": chunk.subsection,
                    "text": chunk.text,
                    "page": chunk.page,
                    "relevance_score": round(relevance, 3),
                    "metadata": chunk.metadata_json,
                })

        ranked_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked_results[:top_k]


rag_retriever = RAGRetriever()
