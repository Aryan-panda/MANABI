from typing import List, Optional
from app.agents.base import BaseAgent, AgentContext, AgentOutput
from app.agents.academic.plan_reviewer_graph import academic_plan_reviewer_app
from app.academic_data import get_academic_data_provider
from app.llm.base import LLMMessage


class AcademicAdvisorAgent(BaseAgent):
    agent_id: str = "academic"
    name: str = "Academic Advisor"
    description: str = (
        "Full-featured academic advisor assisting with degree planning, prerequisite checking, "
        "institutional regulations, attendance guidance, and curriculum navigation."
    )
    purpose: str = (
        "Provide accurate, authoritative academic guidance grounded strictly in institutional policy "
        "and verified student records."
    )
    capabilities: List[str] = [
        "academic_policy_guidance",
        "attendance_counseling",
        "curriculum_planning",
        "prerequisite_validation",
        "semester_plan_review",
        "student_record_lookup",
    ]
    allowed_tools: List[str] = [
        "academic_data_provider",
        "academic_plan_reviewer_workflow",
    ]
    retrieval_domain: Optional[str] = "academic"

    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            "You are the MANABI Academic Advisor, an authoritative university advisory agent.\n\n"
            "OPERATING CONSTRAINTS:\n"
            "1. Ground all policy, attendance, examination, and condonation answers in official institutional rules.\n"
            "2. Never fabricate student data, course prerequisites, or university policies.\n"
            "3. Standard University Attendance Policy: Minimum 75% attendance is strictly required for exam eligibility. "
            "Between 65% and 75%, condonation is granted ONLY with approved medical documentation or university deputation. "
            "Below 65%, attendance is un-condonable and requires course repetition.\n"
            "4. Credit Rules: Standard semester course load is 16-24 credits. Maximum 24 credits per semester without Dean approval.\n"
            "5. If student information is not available or unconfigured, explicitly state that student data integration is unavailable "
            "and offer general policy advice. Never hallucinate student grades or records.\n"
            "6. Always cite reference documents and regulations clearly.\n"
        )

    async def review_plan(self, raw_plan: str, student_id: Optional[str] = None) -> dict:
        """Execute stateful LangGraph plan review."""
        initial_state = {
            "raw_plan": raw_plan,
            "student_id": student_id,
            "student_context": None,
            "extracted_courses": [],
            "prerequisite_issues": [],
            "workload_analysis": {},
            "risk_factors": [],
            "suggested_changes": [],
            "revised_plan": "",
            "is_valid": False,
            "summary": "",
        }
        final_state = await academic_plan_reviewer_app.ainvoke(initial_state)
        return final_state


academic_agent = AcademicAdvisorAgent()
