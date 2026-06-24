from lead_nurture_rag.retriever import KnowledgeBase


def test_retriever_returns_relevant_chunks_for_company_value():
    kb = KnowledgeBase()
    kb.add_text(
        source="acme-site",
        text="Acme Construction helps project teams reduce RFIs with AI document review. "
        "Its dashboard flags payment application validation issues before approval.",
    )

    hits = kb.search("How can you help with payment app validation?", k=2)

    assert hits
    assert hits[0].source == "acme-site"
    assert "payment application validation" in hits[0].text.lower()


def test_retriever_uses_stable_chunk_ids_to_avoid_duplicates():
    kb = KnowledgeBase()
    text = "One useful company fact. " * 20

    first = kb.add_text(source="site", text=text)
    second = kb.add_text(source="site", text=text)

    assert first == second
    assert len(kb.chunks) == len(first)
