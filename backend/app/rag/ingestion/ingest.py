import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional, List
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models import Document, DocumentVersion, DocumentChunk
from app.rag.chunking.structure_aware import structure_chunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("manabi.rag.ingestion")


async def ingest_file(
    file_path: Path,
    domain: str = "academic",
    document_type: str = "handbook",
    source: Optional[str] = None,
    access_level: str = "public",
    version_label: str = "1.0.0",
) -> Optional[Document]:
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"File not found: {file_path}")
        return None

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read file {file_path}: {exc}")
        return None

    if not content.strip():
        logger.warning(f"File is empty, skipping: {file_path}")
        return None

    # Derive document title from first header or filename
    title = file_path.stem.replace("_", " ").title()
    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("# "):
            title = trimmed[2:].strip()
            break

    doc_source = source or f"Manual Ingestion: {file_path.name}"
    content_hash = structure_chunker.calculate_content_hash(content)

    async with AsyncSessionLocal() as db:
        # Check if identical document title exists
        stmt = select(Document).where(Document.title == title, Document.domain == domain)
        existing_doc = (await db.execute(stmt)).scalar_one_or_none()

        if not existing_doc:
            doc = Document(
                title=title,
                domain=domain,
                document_type=document_type,
                source=doc_source,
                access_level=access_level,
                status="active",
            )
            db.add(doc)
            await db.flush()
        else:
            doc = existing_doc
            doc.status = "active"

        # Create new version record
        doc_version = DocumentVersion(
            document_id=doc.id,
            version=version_label,
            content_hash=content_hash,
        )
        db.add(doc_version)
        await db.flush()

        # Structure-aware chunking
        chunks = structure_chunker.chunk_markdown(content)
        for c in chunks:
            chunk_record = DocumentChunk(
                document_version_id=doc_version.id,
                chunk_index=c.chunk_index,
                section=c.section,
                subsection=c.subsection,
                text=c.text,
                metadata_json=c.metadata,
            )
            db.add(chunk_record)

        await db.commit()
        logger.info(f"Successfully ingested: '{title}' [{domain}] -> {len(chunks)} chunks stored.")
        return doc


async def ingest_directory(
    dir_path: Path,
    domain: str = "academic",
    access_level: str = "public",
) -> List[Document]:
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory not found: {dir_path}")
        return []

    valid_extensions = {".md", ".txt", ".markdown"}
    files = [f for f in dir_path.rglob("*") if f.is_file() and f.suffix.lower() in valid_extensions]

    if not files:
        logger.warning(f"No text/markdown documents found in: {dir_path}")
        return []

    logger.info(f"Found {len(files)} documents to ingest in {dir_path}")
    ingested = []
    for f in files:
        # Auto-infer domain from subfolder if named academic/engineering/commerce/management/law
        file_domain = domain
        parts_lower = [p.lower() for p in f.parts]
        for candidate in ["academic", "engineering", "commerce", "management", "law"]:
            if candidate in parts_lower:
                file_domain = candidate
                break

        doc = await ingest_file(f, domain=file_domain, access_level=access_level)
        if doc:
            ingested.append(doc)

    return ingested


def main():
    parser = argparse.ArgumentParser(description="MANABI RAG Document Ingestion CLI")
    parser.add_argument("--file", type=str, help="Path to a single Markdown/Text document to ingest")
    parser.add_argument("--dir", type=str, help="Path to directory containing documents to ingest")
    parser.add_argument("--domain", type=str, default="academic", choices=["academic", "engineering", "commerce", "management", "law"], help="Domain association")
    parser.add_argument("--access-level", type=str, default="public", choices=["public", "student", "faculty", "admin"], help="Document ACL access level")
    parser.add_argument("--source", type=str, default=None, help="Document source description")

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(1)

    if args.file:
        asyncio.run(ingest_file(Path(args.file), domain=args.domain, access_level=args.access_level, source=args.source))
    elif args.dir:
        asyncio.run(ingest_directory(Path(args.dir), domain=args.domain, access_level=args.access_level))


if __name__ == "__main__":
    main()
