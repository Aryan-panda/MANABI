from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class EvalTestCase:
    id: str
    category: str
    domain: str  # "academic" | "engineering" | "commerce" | "management" | "law"
    input_text: str
    expected_agent: str
    expected_keywords: List[str]
    expected_citations: List[str]
    is_numerical: bool = False
    expected_numerical_result: Dict[str, Any] = None
    expected_mermaid: bool = False


BENCHMARK_DATASET: List[EvalTestCase] = [
    # --- ACADEMIC ADVISOR BENCHMARK CASES ---
    EvalTestCase(
        id="acad-001",
        category="policy_attendance",
        domain="academic",
        input_text="What are the official rules and requirements for attendance condonation?",
        expected_agent="academic",
        expected_keywords=["75%", "65%", "condonation", "medical", "dean"],
        expected_citations=["Academic Regulations 2026", "Attendance and Leave Rules"],
    ),
    EvalTestCase(
        id="acad-002",
        category="prerequisites",
        domain="academic",
        input_text="What are the prerequisites for enrolling in Machine Learning Systems CS308?",
        expected_agent="academic",
        expected_keywords=["CS201", "Data Structures", "Linear Algebra", "CS308"],
        expected_citations=["Curriculum Handbook"],
    ),
    EvalTestCase(
        id="acad-003",
        category="credit_overload",
        domain="academic",
        input_text="Can I take 26 credits in semester 6 if my CGPA is 8.5?",
        expected_agent="academic",
        expected_keywords=["overload", "24 credits", "CGPA", "permission"],
        expected_citations=["Academic Regulations 2026"],
    ),

    # --- ENGINEERING ARCHITECT BENCHMARK CASES ---
    EvalTestCase(
        id="eng-001",
        category="numerical_qps",
        domain="engineering",
        input_text="Calculate QPS for 100000 daily active users with 50 actions per day, peak multiplier 2.5, and read ratio 0.8",
        expected_agent="engineering",
        expected_keywords=["QPS", "throughput", "read", "write"],
        expected_citations=["System Design Handbook"],
        is_numerical=True,
        expected_numerical_result={
            "average_total_qps": 57.87,
            "peak_total_qps": 144.68,
            "peak_read_qps": 115.74,
            "peak_write_qps": 28.94,
        },
    ),
    EvalTestCase(
        id="eng-002",
        category="numerical_storage",
        domain="engineering",
        input_text="Calculate 3-year storage capacity for 1,000,000 daily records of 500 bytes each, 25% indexing overhead, and 3x replication factor",
        expected_agent="engineering",
        expected_keywords=["storage", "gigabytes", "terabytes", "replication"],
        expected_citations=["Distributed Storage Systems"],
        is_numerical=True,
        expected_numerical_result={
            "daily_raw_mb": 476.84,
            "total_raw_gb": 509.78,
            "total_with_indexes_gb": 637.23,
            "total_with_replication_gb": 1911.69,
            "total_with_replication_tb": 1.87,
        },
    ),
    EvalTestCase(
        id="eng-003",
        category="architecture_diagram",
        domain="engineering",
        input_text="Design a modular monolith architecture for an agentic platform and generate a Mermaid flowchart",
        expected_agent="engineering",
        expected_keywords=["FastAPI", "PostgreSQL", "pgvector", "Redis", "flowchart"],
        expected_citations=["Modular Monolith Architecture Patterns"],
        expected_mermaid=True,
    ),

    # --- CROSS-DOMAIN ROUTING BENCHMARK CASES ---
    EvalTestCase(
        id="comm-001",
        category="unit_economics",
        domain="commerce",
        input_text="How do I compute Customer Lifetime Value (LTV) and CAC Payback Period for a B2B SaaS company?",
        expected_agent="commerce",
        expected_keywords=["LTV", "CAC", "churn", "gross margin", "payback"],
        expected_citations=["SaaS Unit Economics & Valuation"],
    ),
    EvalTestCase(
        id="mgmt-001",
        category="team_topologies",
        domain="management",
        input_text="How do we organize platform teams versus stream-aligned teams using Team Topologies?",
        expected_agent="management",
        expected_keywords=["stream-aligned", "platform", "enabling", "cognitive load"],
        expected_citations=["Team Topologies in Practice"],
    ),
    EvalTestCase(
        id="law-001",
        category="ip_licensing",
        domain="law",
        input_text="What are the copyleft risks of using AGPL v3 components in a proprietary cloud SaaS platform?",
        expected_agent="law",
        expected_keywords=["AGPL", "copyleft", "network access", "source code", "disclaimer"],
        expected_citations=["Software Licensing & IP Compliance"],
    ),
]
