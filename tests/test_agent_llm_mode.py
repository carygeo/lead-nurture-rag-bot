from types import SimpleNamespace

from lead_nurture_rag.agent import LeadNurtureAgent
from lead_nurture_rag.retriever import KnowledgeBase


class FakeChatCompletions:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="LLM-written nurture response"))]
        )


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeChatCompletions())


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.add_text(
        source="supernews-profile",
        text="Supernews helps companies create AI-powered newsletters from company updates.",
    )
    return kb


def test_agent_uses_chat_completion_client_for_lead_reply() -> None:
    client = FakeOpenAIClient()
    agent = LeadNurtureAgent(build_kb(), client=client, model="test-chat-model")

    result = agent.respond("lead-llm", [], "What is your company about?")

    assert result.reply == "LLM-written nurture response"
    assert result.response_mode == "llm"
    assert result.response_model == "test-chat-model"
    assert client.chat.completions.calls
    call = client.chat.completions.calls[0]
    assert call["model"] == "test-chat-model"
    assert call["messages"][0]["role"] == "system"
    assert "potential lead" in call["messages"][0]["content"]
    assert "What is your company about?" in call["messages"][1]["content"]


def test_agent_reports_fallback_mode_when_no_chat_completion_client() -> None:
    agent = LeadNurtureAgent(build_kb(), client=None)

    result = agent.respond("lead-fallback", [], "What is your company about?")

    assert result.response_mode == "fallback"
    assert result.response_model is None
    assert result.reply != "LLM-written nurture response"
