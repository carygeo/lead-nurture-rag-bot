from lead_nurture_rag.store import ConversationStore


def test_store_persists_conversation_turns(tmp_path):
    store = ConversationStore(tmp_path / "leads.sqlite")

    store.append_turn("lead-1", "user", "hello")
    store.append_turn("lead-1", "assistant", "how can I help?")

    assert store.get_history("lead-1") == ["User: hello", "Assistant: how can I help?"]
