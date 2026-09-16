# MANABI — Knowledge Base Documents Directory

Place your custom Markdown (`.md`), text (`.txt`), or policy documents in this directory to ingest them into the MANABI pgvector RAG system.

## Directory Structure

```
data/documents/
├── academic/      # University handbooks, attendance rules, course catalog, prerequisites
├── engineering/   # Architecture guidelines, API specifications, system design docs
├── commerce/      # Financial models, SaaS valuation benchmarks, unit economics docs
├── management/    # Team topologies, sprint frameworks, OKR guides
└── law/           # Open-source licensing guides, contract clause standards, compliance
```

## How to Ingest Documents

Once you've placed your files in the folders above, run the ingestion CLI from the project root:

```bash
# Ingest an entire directory (auto-infers domain from folder name)
python -m app.rag.ingestion.ingest --dir data/documents

# Or ingest a specific domain folder
python -m app.rag.ingestion.ingest --dir data/documents/academic --domain academic

# Or ingest a single file directly
python -m app.rag.ingestion.ingest --file data/documents/academic/sample_syllabus.md --domain academic
```

The system automatically:
1. Computes SHA-256 content hashes for document version governance (Section 37).
2. Performs structure-aware chunking preserving Markdown headers (`#`, `##`, `###`) and context boundaries.
3. Inserts document records and chunks into PostgreSQL with pgvector embeddings ready for semantic similarity search.
