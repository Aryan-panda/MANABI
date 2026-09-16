import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import AsyncSessionLocal, engine
from app.database.base import Base
from app.database.models import (
    Role,
    User,
    Agent,
    Document,
    DocumentVersion,
    DocumentChunk,
)
from app.security.auth import get_password_hash
from app.rag.chunking.structure_aware import structure_chunker
from app.agents import list_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manabi.seed")


ACADEMIC_HANDBOOK_TEXT = """# University Academic Regulations and Student Handbook

## Attendance Regulations and Condonation Rules
All undergraduate and postgraduate students are required to maintain a minimum cumulative attendance of 75% in each registered course to be eligible to sit for the end-semester examinations.
Attendance is calculated from the official commencement date of the semester up to the last instructional day.

### Condonation of Attendance Shortage
Students who have secured between 65% and 74.9% attendance may submit an application for condonation of shortage under genuine medical grounds or approved university representation (such as inter-university sports, cultural events, or academic conferences).
Such applications must be submitted with valid medical certificates from a registered medical practitioner within 5 working days of resuming classes.
Condonation is granted strictly at the discretion of the Dean of Academic Affairs upon recommendation from the Department Head and requires payment of the prescribed condonation fee.
Students whose attendance falls strictly below 65% are NOT eligible for condonation under any circumstances and must repeat the course when offered next.

## Curriculum Credit Limits and Semester Planning
A student must complete a minimum of 160 credits to qualify for the award of the Bachelor of Technology (B.Tech) degree.
The standard academic workload per semester is between 16 and 22 credits.
The absolute maximum permissible credits in a regular semester is 24 credits. Any student attempting to register for more than 24 credits must obtain prior written approval from the Academic Review Board and possess a minimum CGPA of 8.5.

### Course Prerequisites
Students may not enroll in advanced courses without satisfying all prerequisites listed in the university course catalog.
For example:
- CS301 (Distributed Systems) strictly requires prior completion of CS201 (Data Structures) and CS204 (Computer Networks).
- CS304 (Database Internals) strictly requires prior completion of CS202 (Database Management Systems).
- CS308 (Machine Learning Systems) strictly requires prior completion of MA201 (Linear Algebra & Probability) and CS201 (Data Structures).

## Academic Integrity Policy and Disciplinary Actions
The university maintains zero tolerance towards academic dishonesty.
Plagiarism in assignments, laboratory reports, or project theses is strictly monitored using automated detection software.
First offense of minor plagiarism: Grade F in the concerned evaluation component and mandatory counseling.
Repeated offense or examination malpractice: Immediate cancellation of all course registrations for the semester and referral to the University Disciplinary Committee for possible suspension.
"""

ENGINEERING_MANUAL_TEXT = """# Production System Engineering & Architecture Guidelines

## PostgreSQL and pgvector Architecture
PostgreSQL is the primary persistent system of record.
When storing high-dimensional vector embeddings with pgvector:
- Use HNSW (Hierarchical Navigable Small World) indexes for low latency sub-linear similarity search where memory permits.
- Use Cosine distance operator (<=>) for normalized embeddings.
- Ensure work_mem and maintenance_work_mem are appropriately sized during index construction.
- Combine vector similarity search with relational SQL WHERE clauses (metadata pre-filtering) to prevent full-table scans.

## Redis Caching Strategies
Redis must be used for ephemeral, high-throughput workloads rather than durable persistence.
- Cache-Aside (Lazy Loading): Application queries Redis first. On cache miss, it reads PostgreSQL, writes the result to Redis with an explicit TTL, and returns.
- Every cache entry must declare an explicit TTL (Time-To-Live) to prevent unbounded memory growth.
- Working set sizing: typically 20% of data generates 80% of read traffic. Size cache memory to hold this 20% working set plus 30% safety headroom.
- Use Redis for rate-limiting using the sliding window log or token bucket algorithm.

## Latency Budgets in Distributed Systems
In a modern web tier with an SLA target of 200ms p95:
- Network RTT: budget 30-50ms for client-to-datacenter roundtrips.
- Reverse Proxy (Nginx) & Ingress: 5-10ms.
- Application processing & routing: 15-25ms.
- Cache query: 1-3ms.
- Database query (indexed): 10-25ms per query.
- LLM inference: Token streaming (TTFT - Time to First Token) should be under 800ms.
"""


async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        logger.info("Seeding roles...")
        roles_data = [
            ("student", "Undergraduate and postgraduate students"),
            ("faculty", "Academic faculty and course instructors"),
            ("developer", "Platform software and GenAI engineers"),
            ("admin", "Platform administrators"),
        ]
        role_map = {}
        for role_name, role_desc in roles_data:
            stmt = select(Role).where(Role.name == role_name)
            role = (await db.execute(stmt)).scalar_one_or_none()
            if not role:
                role = Role(name=role_name, description=role_desc)
                db.add(role)
                await db.flush()
            role_map[role_name] = role

        logger.info("Seeding test user...")
        user_stmt = select(User).where(User.email == "aryan@university.edu")
        test_user = (await db.execute(user_stmt)).scalar_one_or_none()
        if not test_user:
            test_user = User(
                email="aryan@university.edu",
                name="Aryan Panda",
                password_hash=get_password_hash("password123"),
                role_id=role_map["student"].id,
                is_active=True,
            )
            db.add(test_user)
            await db.flush()

        logger.info("Seeding registered agents...")
        for agent in list_agents():
            stmt = select(Agent).where(Agent.id == agent.agent_id)
            existing_agent = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_agent:
                db_agent = Agent(
                    id=agent.agent_id,
                    name=agent.name,
                    description=agent.description,
                    configuration={"capabilities": agent.capabilities, "tools": agent.allowed_tools},
                    is_active=True,
                )
                db.add(db_agent)

        logger.info("Seeding Academic RAG Knowledge Base...")
        doc_stmt = select(Document).where(Document.title == "University Academic Regulations and Student Handbook")
        existing_doc = (await db.execute(doc_stmt)).scalar_one_or_none()
        if not existing_doc:
            academic_doc = Document(
                title="University Academic Regulations and Student Handbook",
                domain="academic",
                document_type="policy",
                source="University Academic Secretariat Official Publication",
                access_level="public",
                status="active",
            )
            db.add(academic_doc)
            await db.flush()

            doc_version = DocumentVersion(
                document_id=academic_doc.id,
                version="2024.1",
                content_hash=structure_chunker.calculate_content_hash(ACADEMIC_HANDBOOK_TEXT),
            )
            db.add(doc_version)
            await db.flush()

            chunks = structure_chunker.chunk_markdown(ACADEMIC_HANDBOOK_TEXT)
            for c in chunks:
                db_chunk = DocumentChunk(
                    document_version_id=doc_version.id,
                    chunk_index=c.chunk_index,
                    section=c.section,
                    subsection=c.subsection,
                    text=c.text,
                    metadata_json=c.metadata,
                )
                db.add(db_chunk)

        logger.info("Seeding Engineering RAG Knowledge Base...")
        eng_doc_stmt = select(Document).where(Document.title == "Production System Engineering & Architecture Guidelines")
        existing_eng_doc = (await db.execute(eng_doc_stmt)).scalar_one_or_none()
        if not existing_eng_doc:
            eng_doc = Document(
                title="Production System Engineering & Architecture Guidelines",
                domain="engineering",
                document_type="manual",
                source="MANABI Engineering Architecture Board",
                access_level="public",
                status="active",
            )
            db.add(eng_doc)
            await db.flush()

            eng_doc_version = DocumentVersion(
                document_id=eng_doc.id,
                version="1.0.0",
                content_hash=structure_chunker.calculate_content_hash(ENGINEERING_MANUAL_TEXT),
            )
            db.add(eng_doc_version)
            await db.flush()

            eng_chunks = structure_chunker.chunk_markdown(ENGINEERING_MANUAL_TEXT)
            for c in eng_chunks:
                db_chunk = DocumentChunk(
                    document_version_id=eng_doc_version.id,
                    chunk_index=c.chunk_index,
                    section=c.section,
                    subsection=c.subsection,
                    text=c.text,
                    metadata_json=c.metadata,
                )
                db.add(db_chunk)

        await db.commit()
        logger.info("Database seeding successfully completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
