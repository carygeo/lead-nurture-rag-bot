from lead_nurture_rag.observation import build_observation, analyze_observation
from lead_nurture_rag.store import ConversationStore


def test_store_persists_observation_analysis(tmp_path):
    store = ConversationStore(tmp_path / "leads.sqlite")
    obs = build_observation("lead-1", "email", "We have budget and want a demo", [])
    analysis = analyze_observation(obs)

    store.append_observation(obs, analysis)

    saved = store.get_observations("lead-1")
    assert len(saved) == 1
    assert saved[0]["analysis"]["intent"] == "schedule_demo"
    assert saved[0]["analysis"]["sentiment"]["label"] == "positive"
