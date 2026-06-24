from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

POSITIVE_TERMS = {
    "useful", "interested", "helpful", "good", "great", "yes", "need", "want", "budget",
    "schedule", "demo", "improve", "reduce", "valuable",
}
NEGATIVE_TERMS = {
    "not interested", "too expensive", "expensive", "spam", "bad", "confusing", "no budget",
    "later", "busy", "unsubscribe", "stop",
}
BUYING_TERMS = {"budget", "demo", "schedule", "book", "pricing", "price", "pilot", "proposal", "contract"}
PAIN_TERMS = {"manual", "slow", "risk", "missing", "error", "errors", "bottleneck", "too much time"}
OBJECTION_TERMS = {"not interested", "too expensive", "no budget", "later", "already have", "busy", "spam", "unsubscribe", "stop"}
ROLE_PATTERNS = {
    "CFO": [r"\bCFO\b", r"chief financial officer"],
    "CEO": [r"\bCEO\b", r"chief executive officer"],
    "project_team": [r"project manager", r"project executive", r"project team", r"manage pay apps"],
    "finance_team": [r"finance", r"accounting", r"controller", r"accounts payable", r"\bAP\b"],
}
INDUSTRY_PATTERNS = {
    "construction": [r"construction", r"contractor", r"subcontractor", r"jobsite"],
    "real_estate": [r"real estate", r"property", r"developer"],
}


class Observation(BaseModel):
    lead_id: str
    channel: Literal["chat", "email", "sms", "web", "other"] = "chat"
    message: str
    history: list[str] = Field(default_factory=list)


class Sentiment(BaseModel):
    label: Literal["positive", "neutral", "negative"]
    score: float = Field(ge=-1.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class Demographics(BaseModel):
    age_range: str | None = None
    gender: str | None = None
    occupation: str | None = None
    industry: str | None = None
    inference_policy: str = "explicit_self_disclosure_only"


class ObservationAnalysis(BaseModel):
    intent: Literal["learn", "evaluate", "object", "schedule_demo", "disengage"]
    sentiment: Sentiment
    pain_points: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    buying_signals: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    recommended_rag_topics: list[str] = Field(default_factory=list)
    demographics: Demographics = Field(default_factory=Demographics)


def build_observation(lead_id: str, channel: str, message: str, history: list[str] | None = None) -> Observation:
    return Observation(lead_id=lead_id, channel=channel, message=message, history=history or [])


def _contains_any(text: str, terms: set[str]) -> list[str]:
    low = text.lower()
    return [term for term in sorted(terms) if term in low]


def analyze_sentiment(message: str) -> Sentiment:
    positive = _contains_any(message, POSITIVE_TERMS)
    negative = _contains_any(message, NEGATIVE_TERMS)
    raw = len(positive) - len(negative)
    if raw > 0:
        label = "positive"
    elif raw < 0:
        label = "negative"
    else:
        label = "neutral"
    score = max(-1.0, min(1.0, raw / 5))
    return Sentiment(label=label, score=score, evidence=positive + negative)


def extract_questions(message: str) -> list[str]:
    return [q.strip() + "?" for q in re.findall(r"([^?]+)\?", message) if q.strip()]


def infer_demographics(message: str) -> Demographics:
    """Extract only self-disclosed demographics; do not infer protected traits from names/style."""
    low = message.lower()
    age_range = None
    age_match = re.search(r"\b(?:i am|i'm|im)\s+(\d{2})\s*(?:years old|year old|-year-old)?", low)
    if not age_match:
        age_match = re.search(r"\b(\d{2})-year-old\b", low)
    if age_match:
        age = int(age_match.group(1))
        age_range = f"{age // 10 * 10}s"

    gender = None
    explicit_gender = [
        ("woman", r"\b(?:i am|i'm|im)\s+(?:a\s+)?(?:\d{2}[- ]year[- ]old\s+)?woman\b|\bfemale\b"),
        ("man", r"\b(?:i am|i'm|im)\s+(?:a\s+)?(?:\d{2}[- ]year[- ]old\s+)?man\b|\bmale\b"),
        ("nonbinary", r"\b(?:non[- ]?binary|nb)\b"),
    ]
    for label, pattern in explicit_gender:
        if re.search(pattern, low):
            gender = label
            break

    occupation = None
    for label, patterns in ROLE_PATTERNS.items():
        if any(re.search(pattern, message, flags=re.IGNORECASE) for pattern in patterns):
            occupation = label
            break

    industry = None
    for label, patterns in INDUSTRY_PATTERNS.items():
        if any(re.search(pattern, message, flags=re.IGNORECASE) for pattern in patterns):
            industry = label
            break

    return Demographics(age_range=age_range, gender=gender, occupation=occupation, industry=industry)


def choose_intent(message: str, buying: list[str], objections: list[str], sentiment: Sentiment) -> str:
    low = message.lower()
    if "unsubscribe" in low or "stop" in low:
        return "disengage"
    if objections and sentiment.label == "negative":
        return "object"
    if {"demo", "schedule"} & set(buying) or "book" in buying:
        return "schedule_demo"
    if buying or any(term in low for term in ["compare", "case study", "pricing", "roi"]):
        return "evaluate"
    return "learn"


def recommended_topics(buying: list[str], pain: list[str], questions: list[str], intent: str) -> list[str]:
    topics: list[str] = []
    if intent == "schedule_demo":
        topics.append("scheduling")
    if any(term in buying for term in ["budget", "pricing", "price"]):
        topics.append("pricing")
    if pain:
        topics.extend(["risk_reduction", "pain_point"])
    if questions:
        topics.append("how_it_works")
    return list(dict.fromkeys(topics or ["general_value"]))


def analyze_observation(observation: Observation) -> ObservationAnalysis:
    message = observation.message
    sentiment = analyze_sentiment(message)
    objections = _contains_any(message, OBJECTION_TERMS)
    buying = _contains_any(message, BUYING_TERMS)
    pain = _contains_any(message, PAIN_TERMS)
    questions = extract_questions(message)
    intent = choose_intent(message, buying, objections, sentiment)
    return ObservationAnalysis(
        intent=intent,
        sentiment=sentiment,
        pain_points=pain,
        objections=objections,
        buying_signals=buying,
        questions=questions,
        recommended_rag_topics=recommended_topics(buying, pain, questions, intent),
        demographics=infer_demographics(message),
    )
