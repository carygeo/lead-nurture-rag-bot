from lead_nurture_rag.agent import LeadNurtureAgent
from lead_nurture_rag.retriever import KnowledgeBase


def test_agent_result_includes_observation_analysis_and_sentiment_adjusts_score():
    kb = KnowledgeBase()
    kb.add_text("company", "We help construction finance teams validate payment applications.")
    agent = LeadNurtureAgent(kb)

    result = agent.respond(
        lead_id="lead-obs",
        history=[],
        message="This is useful. I am the CFO and we have budget for a demo.",
    )

    assert result.observation.intent == "schedule_demo"
    assert result.observation.sentiment.label == "positive"
    assert result.lead.demographics.occupation == "CFO"
    assert result.next_action == "schedule_contact"
