import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.rag import Citation
from app.database.base import utc_now


class CitationEngine:
    """
    Engine for creating, formatting, and verifying citations from RAG chunks.
    """

    @staticmethod
    async def record_citations(
        db: AsyncSession,
        execution_id: uuid.UUID,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> List[Citation]:
        citations = []
        for chunk in retrieved_chunks:
            chunk_id_str = chunk.get("chunk_id")
            if not chunk_id_str:
                continue
            try:
                chunk_uuid = uuid.UUID(chunk_id_str)
                citation = Citation(
                    execution_id=execution_id,
                    chunk_id=chunk_uuid,
                    relevance_score=chunk.get("relevance_score", 1.0),
                    quote=chunk.get("text", "")[:200],  # Short excerpt quote
                    created_at=utc_now(),
                )
                db.add(citation)
                citations.append(citation)
            except Exception:
                continue

        if citations:
            await db.commit()
        return citations

    @staticmethod
    def format_citations_markdown(citations: List[Dict[str, Any]]) -> str:
        if not citations:
            return ""
        lines = ["\n\n### Authoritative Sources & Citations:"]
        for idx, c in enumerate(citations, 1):
            source = c.get("source", "Institutional Document")
            section = c.get("section", "Section")
            relevance = c.get("relevance_score", 1.0) * 100
            lines.append(f"[{idx}] **{source}** — *{section}* (Relevance: {relevance:.0f}%)")
        return "\n".join(lines)


citation_engine = CitationEngine()
