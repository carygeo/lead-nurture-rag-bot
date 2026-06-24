from __future__ import annotations

import os
import re
from typing import Any

from openai import OpenAI

from .models import AgentTurnResult, LeadState, SearchHit
from .observation import ObservationAnalysis, analyze_observation, build_observation
from .retriever import KnowledgeBase

POSITIVE = {"interested", "help", "reduce", "improve", "pain", "problem", "issue", "need", "useful"}
BUYING = {"demo", "budget", "price", "pricing", "proposal", "contract", "buy", "pilot", "this week", "schedule", "book"}
OBJECTIONS = {"not interested", "too expensive", "no budget", "later", "already have", "busy", "spam"}
PAIN = {"manual", "slow", "too much time", "risk", "missing", "errors", "bottleneck", "validation"}


def _contains_any(text: str, terms: set[str]) -> list[str]:
    low = text.lower()
    return [term for term in sorted(terms) if term in low]


def score_lead(
    lead_id: str, history: list[str], message: str, analysis: ObservationAnalysis | None = None
) -> LeadState:
    corpus = " ".join(history + [message]).lower()
    signals = _contains_any(corpus, POSITIVE | BUYING | PAIN)
    objections = _contains_any(corpus, OBJECTIONS)
    score = 10
    score += min(25, 6 * len(_contains_any(corpus, POSITIVE)))
    score += min(30, 8 * len(_contains_any(corpus, PAIN)))
    buying_signals = _contains_any(corpus, BUYING)
    score += min(45, 12 * len(buying_signals))
    if len(buying_signals) >= 2:
        score += 18
    if len(buying_signals) >= 3:
        score += 15
    if "?" in message:
        score += 10
    if len(message.split()) > 12:
        score += 8
    if analysis and analysis.sentiment.label == "positive":
        score += 8
    if analysis and analysis.intent == "schedule_demo":
        score += 20
    if analysis and analysis.sentiment.label == "negative":
        score -= 15
    score -= min(30, 10 * len(objections))
    score = max(0, min(100, score))
    temperature = "cold" if score < 40 else "warm" if score < 75 else "hot"
    demographics = analysis.demographics if analysis else None
    return LeadState(
        lead_id=lead_id,
        temperature=temperature,
        score=score,
        signals=signals,
        objections=objections,
        demographics=demographics or {},
    )


class LeadNurtureAgent:
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        model: str | None = None,
        client: Any | None = None,
    ):
        self.knowledge_base = knowledge_base
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if client is not None:
            self._client = client
        elif os.getenv("OPENAI_API_KEY"):
            self._client = OpenAI()
        else:
            self._client = None

    def respond(self, lead_id: str, history: list[str], message: str) -> AgentTurnResult:
        observation = build_observation(lead_id=lead_id, channel="chat", message=message, history=history)
        analysis = analyze_observation(observation)
        retrieval_query = f"{message} {' '.join(analysis.recommended_rag_topics)}"
        retrieved = self.knowledge_base.search(retrieval_query, k=4)
        lead = score_lead(lead_id, history, message, analysis)
        next_action = self._next_action(lead)
        if self._client:
            reply = self._llm_reply(lead, history, message, retrieved, next_action)
            response_mode = "llm"
            response_model = self.model
        else:
            reply = self._fallback_reply(lead, message, retrieved, next_action)
            response_mode = "fallback"
            response_model = None
        rationale = (
            f"{lead.temperature} lead scored {lead.score}; intent={analysis.intent}; "
            f"sentiment={analysis.sentiment.label}/{analysis.sentiment.score}; "
            f"signals={lead.signals}; objections={lead.objections}"
        )
        return AgentTurnResult(
            lead=lead,
            reply=reply,
            retrieved_context=retrieved,
            next_action=next_action,
            observation=analysis,
            rationale=rationale,
            response_mode=response_mode,
            response_model=response_model,
        )

    def _next_action(self, lead: LeadState) -> str:
        if lead.temperature == "hot":
            return "schedule_contact"
        if lead.temperature == "warm":
            return "offer_case_study"
        return "continue_nurture"

    def _llm_reply(self, lead: LeadState, history: list[str], message: str, retrieved: list[SearchHit], next_action: str) -> str:
        context = "\n\n".join(f"Source: {hit.source}\n{hit.text}" for hit in retrieved) or "No retrieved context."
        system = (
            "You are the chat completion model inside a lead nurturing chatbot prototype. "
            "Respond directly to the potential lead's latest chat query as the agent would in production. "
            "Be helpful, concise, and value-led. Use retrieved company knowledge only; do not invent features. "
            "Goal: answer the question, make the next conversation step slightly warmer by connecting a business pain "
            "to a concrete value point, then ask one focused qualification question. "
            "If hot, ask for a concrete scheduling window for a contact appointment/demo. Never pretend to be human."
        )
        user = f"Lead state: {lead.model_dump()}\nNext action: {next_action}\nHistory: {history[-6:]}\nMessage: {message}\nRetrieved context:\n{context}"
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
        )
        return response.choices[0].message.content or self._fallback_reply(lead, message, retrieved, next_action)

    def _fallback_reply(self, lead: LeadState, message: str, retrieved: list[SearchHit], next_action: str) -> str:
        evidence = retrieved[0].text if retrieved else "the company knowledge base you provided"
        sentence = re.split(r"(?<=[.!?])\s+", evidence.strip())[0][:240]
        if next_action == "schedule_contact":
            return (
                f"Based on what you shared, this sounds like an active fit. {sentence} "
                "A practical next step is to schedule a short contact appointment or workflow review with someone who can map it to your project. "
                "What day this week would be easiest for a 20-minute demo?"
            )
        if next_action == "offer_case_study":
            return (
                f"That pain is exactly where the strongest value tends to show up: {sentence} "
                "If useful, I can walk through a quick example of how this would reduce review effort. "
                "Which part of the workflow is most painful right now?"
            )
        return (
            f"A useful starting point is this: {sentence} "
            "The goal would be to reduce low-value manual follow-up before asking you for more time. "
            "What workflow or outcome would make this worth exploring for your team?"
        )
