from lead_nurture_rag.agent import LeadNurtureAgent
from lead_nurture_rag.retriever import KnowledgeBase


def test_hot_lead_is_asked_to_schedule_contact_appointment():
    kb = KnowledgeBase()
    kb.add_text(
        source="company",
        text="The company offers demos for teams ready to evaluate payment application automation.",
    )
    agent = LeadNurtureAgent(kb)

    result = agent.respond(
        lead_id="lead-ready",
        history=["Assistant: Would you like to see how this works?"],
        message="We have budget and want to schedule a demo.",
    )

    assert result.lead.temperature == "hot"
    assert result.next_action == "schedule_contact"
    assert "schedule" in result.reply.lower() or "appointment" in result.reply.lower()
    assert "what day" in result.reply.lower() or "time" in result.reply.lower()
