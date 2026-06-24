from lead_nurture_rag.observation import analyze_observation, build_observation


def test_observation_analysis_extracts_sentiment_intent_and_signals():
    obs = build_observation(
        lead_id="lead-1",
        channel="email",
        message="This looks useful. We have budget and want to schedule a demo next week.",
        history=[],
    )

    analysis = analyze_observation(obs)

    assert analysis.sentiment.label == "positive"
    assert analysis.sentiment.score > 0
    assert analysis.intent == "schedule_demo"
    assert "budget" in analysis.buying_signals
    assert "schedule" in analysis.buying_signals
    assert analysis.recommended_rag_topics == ["scheduling", "pricing"]


def test_observation_analysis_tracks_negative_sentiment_and_objections():
    obs = build_observation(
        lead_id="lead-2",
        channel="chat",
        message="This feels too expensive and I am not interested right now.",
        history=[],
    )

    analysis = analyze_observation(obs)

    assert analysis.sentiment.label == "negative"
    assert "too expensive" in analysis.objections
    assert "not interested" in analysis.objections
    assert analysis.intent == "object"


def test_demographics_are_only_recorded_when_explicitly_self_disclosed():
    obs = build_observation(
        lead_id="lead-3",
        channel="email",
        message="I am a 42-year-old woman and the CFO for a construction firm.",
        history=[],
    )

    analysis = analyze_observation(obs)

    assert analysis.demographics.age_range == "40s"
    assert analysis.demographics.gender == "woman"
    assert analysis.demographics.occupation == "CFO"
    assert analysis.demographics.industry == "construction"
    assert analysis.demographics.inference_policy == "explicit_self_disclosure_only"


def test_demographics_do_not_guess_age_or_gender_from_role_only():
    obs = build_observation(
        lead_id="lead-4",
        channel="email",
        message="I manage pay apps for our construction team.",
        history=[],
    )

    analysis = analyze_observation(obs)

    assert analysis.demographics.age_range is None
    assert analysis.demographics.gender is None
    assert analysis.demographics.occupation == "project_team"
    assert analysis.demographics.industry == "construction"
