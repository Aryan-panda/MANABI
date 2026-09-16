import pytest
from app.agents import list_agents, get_agent
from app.agents.router import intent_router


def test_agent_registry():
    agents = list_agents()
    assert len(agents) == 5
    agent_ids = {a.agent_id for a in agents}
    assert agent_ids == {"academic", "engineering", "commerce", "management", "law"}

    academic = get_agent("academic")
    assert academic is not None
    assert academic.name == "Academic Advisor"

    engineering = get_agent("engineering")
    assert engineering is not None
    assert "system_design" in engineering.capabilities


def test_intent_router_deterministic():
    res_academic = intent_router.route_deterministic("What is the attendance condonation shortage policy?")
    assert res_academic is not None
    assert res_academic.agent == "academic"
    assert res_academic.confidence >= 0.70

    res_engineering = intent_router.route_deterministic("Can you help me design a database schema and calculate QPS?")
    assert res_engineering is not None
    assert res_engineering.agent == "engineering"

    res_law = intent_router.route_deterministic("What does an indemnity clause mean in an NDA contract?")
    assert res_law is not None
    assert res_law.agent == "law"

    res_commerce = intent_router.route_deterministic("How do I calculate unit economics and EBITDA margin?")
    assert res_commerce is not None
    assert res_commerce.agent == "commerce"
