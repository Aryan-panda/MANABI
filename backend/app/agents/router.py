import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.llm.base import LLMMessage
from app.llm.gateway import model_gateway


class IntentRoutingResult(BaseModel):
    agent: str  # 'academic', 'engineering', 'commerce', 'management', 'law'
    task: str   # e.g., 'plan_review', 'system_design', 'policy_inquiry', 'general_chat'
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class IntentRouter:
    """
    High-performance structured Intent Router.
    Uses pattern-based deterministic matching for high-velocity turns,
    with fallback to LLM structured classification for ambiguous prompts.
    """

    # Deterministic keyword registries
    KEYWORDS: Dict[str, Dict[str, list]] = {
        "academic": {
            "attendance": ["attendance", "condonation", "shortage", "classes held", "medical leave"],
            "courses": ["course", "syllabus", "prerequisite", "curriculum", "credit", "elective"],
            "exam_results": ["exam", "gpa", "cgpa", "grades", "transcript", "backlog", "revaluation"],
            "plan_review": ["review my plan", "semester plan", "study plan", "degree plan", "course schedule"],
            "regulations": ["plagiarism", "cheating", "disciplinary", "student handbook", "academic policy"],
        },
        "engineering": {
            "system_design": ["system design", "architecture", "microservices", "modular monolith", "distributed"],
            "database": ["database design", "schema", "erd", "sql vs nosql", "pgvector", "indexing"],
            "capacity": ["qps", "throughput", "bandwidth", "storage capacity", "latency budget", "cache sizing"],
            "diagram": ["mermaid", "flowchart", "sequence diagram", "er diagram", "architecture diagram"],
            "code_review": ["debug", "refactor", "spring boot", "fastapi", "docker compose", "concurrency"],
        },
        "commerce": {
            "finance": ["balance sheet", "income statement", "cash flow", "roi", "capex", "opex"],
            "pricing": ["unit economics", "pricing strategy", "cogs", "gross margin", "ebitda", "valuation"],
        },
        "management": {
            "strategy": ["okr", "kpi", "agile", "scrum", "sprint", "kanban", "stakeholder management"],
            "leadership": ["change management", "organizational design", "team topology", "resource allocation"],
        },
        "law": {
            "contracts": ["contract", "clause", "nda", "terms of service", "liability", "indemnity"],
            "intellectual_property": ["patent", "trademark", "copyright", "fair use", "gdpr", "compliance"],
        }
    }

    def route_deterministic(self, prompt: str) -> Optional[IntentRoutingResult]:
        lowered = prompt.lower()

        scores: Dict[str, Dict[str, int]] = {}
        for agent, tasks in self.KEYWORDS.items():
            scores[agent] = {}
            for task, keywords in tasks.items():
                match_count = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lowered))
                if match_count > 0:
                    scores[agent][task] = match_count

        best_agent = None
        best_task = None
        highest_score = 0

        for agent, tasks in scores.items():
            for task, count in tasks.items():
                if count > highest_score:
                    highest_score = count
                    best_agent = agent
                    best_task = task

        if highest_score >= 1 and best_agent and best_task:
            confidence = min(0.70 + (highest_score * 0.10), 0.98)
            return IntentRoutingResult(
                agent=best_agent,
                task=best_task,
                confidence=confidence,
                reasoning=f"Deterministic match on keyword density ({highest_score} keyword hits)"
            )
        return None

    async def route(self, prompt: str, forced_agent: Optional[str] = None) -> IntentRoutingResult:
        if forced_agent and forced_agent.lower() in ["academic", "engineering", "commerce", "management", "law"]:
            return IntentRoutingResult(
                agent=forced_agent.lower(),
                task="user_selected",
                confidence=1.0,
                reasoning="Explicitly selected by user interface"
            )

        deterministic_result = self.route_deterministic(prompt)
        if deterministic_result and deterministic_result.confidence >= 0.80:
            return deterministic_result

        # Ambiguous prompt: use lightweight structured classification
        try:
            classification_prompt = (
                "You are an Intent Routing Classifier. Classify the user prompt into exactly one of these domains: "
                "['academic', 'engineering', 'commerce', 'management', 'law'].\n"
                "Respond in strictly JSON format matching this schema:\n"
                '{"agent": "academic|engineering|commerce|management|law", "task": "short_task_name", "confidence": 0.85, "reasoning": "brief reason"}\n'
                f"User Prompt: {prompt}"
            )
            resp = await model_gateway.generate(
                messages=[LLMMessage(role="user", content=classification_prompt)],
                temperature=0.0,
                max_tokens=150,
            )
            import json
            cleaned = resp.content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return IntentRoutingResult.model_validate(data)
        except Exception:
            # Fallback to academic if uncertain
            return IntentRoutingResult(
                agent="academic",
                task="general_inquiry",
                confidence=0.50,
                reasoning="Default fallback for ambiguous intent"
            )


intent_router = IntentRouter()
