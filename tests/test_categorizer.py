from lead_nurture_rag.categorizer import categorize_chunk, categorize_page


def test_categorize_page_identifies_solution_and_persona_from_url_and_title():
    meta = categorize_page(
        url="https://example.com/solutions/payment-application-validation",
        title="Payment Application Validation for Project Teams",
        text="Reduce manual pay app review for construction project managers and executives.",
    )

    assert meta["page_type"] == "solution"
    assert "payment_application_validation" in meta["topics"]
    assert "construction" in meta["industries"]
    assert "project_team" in meta["personas"]


def test_categorize_chunk_maps_content_to_buyer_journey_stage():
    meta = categorize_chunk(
        text="Book a demo to see pricing, implementation, and ROI for your next pilot.",
        page_metadata={"page_type": "pricing", "topics": [], "personas": [], "industries": []},
    )

    assert meta["intent_stage"] == "decision"
    assert "pricing" in meta["topics"]
    assert "schedule_demo" in meta["questions_answered"]
