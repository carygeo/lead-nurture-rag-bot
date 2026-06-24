from lead_nurture_rag.agent import LeadNurtureAgent
from lead_nurture_rag.retriever import KnowledgeBase


def build_agent():
    kb = KnowledgeBase()
    kb.add_text(
        source="company-profile",
        text=(
            "BuildCo AI validates subcontractor payment applications, finds missing lien waivers, "
            "and summarizes risk for construction project teams before approvals."
        ),
    )
    return LeadNurtureAgent(kb)


def test_agent_moves_interested_lead_to_warm_and_asks_nurturing_question():
    agent = build_agent()

    result = agent.respond(
        lead_id="lead-1",
        history=[],
        message="We spend too much time checking payment apps. Can this reduce missing lien waivers?",
    )

    assert result.lead.temperature in {"warm", "hot"}
    assert result.lead.score >= 40
    assert result.retrieved_context
    assert "lien" in result.reply.lower() or "payment" in result.reply.lower()
    assert "?" in result.reply


def test_agent_scopes_retrieval_by_company_name():
    kb = KnowledgeBase()
    kb.add_text(
        source="supernews-site",
        text="Supernews creates AI summaries and bite-sized visual news for mobile readers.",
        metadata={"company_name": "Supernews"},
    )
    kb.add_text(
        source="coldwater-site",
        text="Coldwater Harvest delivers premium Canadian Atlantic seafood to homes and restaurants.",
        metadata={"company_name": "Coldwater Harvest"},
    )
    agent = LeadNurtureAgent(kb)

    result = agent.respond(
        lead_id="lead-3",
        history=[],
        message="Tell me more about your company",
        company_name="Coldwater Harvest",
    )

    assert result.retrieved_context
    assert all(hit.metadata["company_name"] == "Coldwater Harvest" for hit in result.retrieved_context)
    assert "supernews" not in result.reply.lower()


def test_agent_marks_explicit_buying_signal_as_hot():
    agent = build_agent()

    result = agent.respond(
        lead_id="lead-2",
        history=["Bot: We can show a short workflow if useful."],
        message="Yes, book a demo this week. We have budget and need this for our next project.",
    )

    assert result.lead.temperature == "hot"
    assert result.lead.score >= 75
    assert result.next_action == "schedule_contact"
