from lead_nurture_rag.crawler import CrawledDocument
from lead_nurture_rag.retriever import KnowledgeBase


def test_knowledge_base_ingests_crawled_docs_with_metadata_for_retrieval():
    kb = KnowledgeBase()
    doc = CrawledDocument(
        url="https://acme.test/solutions/pay-apps",
        title="Pay App Validation",
        text="Reduce missing lien waivers and payment application risk for project teams.",
        metadata={
            "company_name": "Acme",
            "page_type": "solution",
            "intent_stage": "consideration",
            "topics": ["payment_application_validation", "risk_reduction"],
            "personas": ["project_team"],
            "industries": ["construction"],
            "questions_answered": ["pain_point"],
        },
    )

    kb.add_documents([doc])
    hit = kb.search("Can you help with lien waiver risk?", k=1)[0]

    assert hit.metadata["page_type"] == "solution"
    assert "payment_application_validation" in hit.metadata["topics"]
    assert hit.source == "https://acme.test/solutions/pay-apps"
