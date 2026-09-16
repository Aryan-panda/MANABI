import re
from typing import Optional


class MermaidDiagramGenerator:
    """
    Generator and validator for architectural Mermaid diagrams.
    Ensures syntax correctness so frontend Mermaid viewers render cleanly.
    """

    @staticmethod
    def validate_mermaid_syntax(mermaid_code: str) -> bool:
        trimmed = mermaid_code.strip()
        valid_prefixes = (
            "graph ",
            "flowchart ",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "erDiagram",
            "gantt",
            "pie",
            "gitGraph",
            "C4Context",
            "mindmap",
        )
        for prefix in valid_prefixes:
            if trimmed.startswith(prefix):
                return True
        return False

    @staticmethod
    def generate_system_architecture_diagram(service_name: str = "MANABI Modular Monolith") -> str:
        return f"""flowchart TB
    subgraph ClientLayer [Client Presentation]
        Browser[React + TypeScript + Tailwind SPA]
        MobileApp[Mobile Webview]
    end

    subgraph EdgeLayer [Edge & Security Gateway]
        Nginx[Nginx Reverse Proxy / SSL Termination / Rate Limiter]
    end

    subgraph AppMonolith [MANABI Modular Monolith]
        direction TB
        API[FastAPI Application Server]
        Router[Intent Routing Engine]
        Gateway[Internal Model Gateway]
        
        subgraph AgentsRuntime [Agents Layer]
            AcadAgent[Academic Advisor]
            EngAgent[Engineering Architect]
            LightAgents[Commerce / Management / Law]
        end

        subgraph CoreServices [Platform Services]
            RAGService[pgvector RAG Retrieval]
            CalcService[Deterministic Engineering Calculator]
            MemoryService[User Memory Engine]
            GraphService[LangGraph Plan Reviewer]
        end
    end

    subgraph Persistence [Data Tier]
        PG[(PostgreSQL 16 + pgvector)]
        Redis[(Redis 7 Cache / PubSub)]
    end

    subgraph ExternalServices [External Providers]
        Gemini[Google Gemini API]
        OpenAI[OpenAI API]
        Ollama[Local External Ollama HTTP]
        CollegeSIS[Institutional SIS API]
    end

    Browser -->|HTTPS / SSE Streaming| Nginx
    MobileApp -->|HTTPS| Nginx
    Nginx -->|Reverse Proxy| API
    API --> Router
    Router --> AgentsRuntime
    AgentsRuntime --> CoreServices
    CoreServices --> Gateway
    Gateway --> Gemini
    Gateway --> OpenAI
    Gateway --> Ollama
    AcadAgent --> CollegeSIS
    CoreServices --> PG
    CoreServices --> Redis
"""

    @staticmethod
    def generate_er_diagram() -> str:
        return """erDiagram
    USERS ||--o{ CONVERSATIONS : initiates
    USERS ||--o{ MEMORIES : owns
    USERS }o--|| ROLES : assigned
    CONVERSATIONS ||--o{ MESSAGES : contains
    CONVERSATIONS ||--o{ AGENT_EXECUTIONS : records
    AGENT_EXECUTIONS ||--o{ CITATIONS : generates
    AGENT_EXECUTIONS ||--o{ LLM_USAGE : measures
    AGENT_EXECUTIONS ||--o{ TOOL_EXECUTIONS : executes
    TOOL_DEFINITIONS ||--o{ TOOL_EXECUTIONS : defines
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : releases
    DOCUMENT_VERSIONS ||--o{ DOCUMENT_CHUNKS : splits_into
    DOCUMENT_CHUNKS ||--o{ CITATIONS : references

    USERS {
        uuid id PK
        string email UK
        string name
        string password_hash
        int role_id FK
        boolean is_active
        datetime created_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid user_id FK
        string agent_id FK
        string title
        string status
        datetime created_at
    }

    DOCUMENT_CHUNKS {
        uuid id PK
        uuid document_version_id FK
        int chunk_index
        string section
        text text
        vector embedding
        json metadata_json
    }

    MEMORIES {
        uuid id PK
        uuid user_id FK
        string type
        string key
        text value
        string confidence
        int evidence_count
    }
"""


mermaid_generator = MermaidDiagramGenerator()
