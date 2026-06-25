from __future__ import annotations

import argparse
import json
import re
import statistics
import time
from pathlib import Path
from typing import Any

from lead_nurture_rag.agent import score_lead
from lead_nurture_rag.models import KnowledgeChunk
from lead_nurture_rag.observation import analyze_observation, build_observation
from lead_nurture_rag.retriever import KnowledgeBase


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected a JSON object")
        rows.append(row)
    return rows


def load_kb(path: Path) -> KnowledgeBase:
    kb = KnowledgeBase()
    for line_no, row in enumerate(iter_jsonl(path), 1):
        try:
            chunk = KnowledgeChunk(**row)
        except Exception as exc:  # pydantic raises rich validation exceptions
            raise ValueError(f"{path}:{line_no}: invalid KnowledgeChunk row: {exc}") from exc
        kb.chunks[chunk.id] = chunk
    kb._reindex()
    return kb


def query_for_case(case: dict[str, Any]) -> str:
    expected_retrieval = case.get("expected_retrieval") or {}
    topics = expected_retrieval.get("topics") or []
    history = case.get("history") or []
    parts = [" ".join(str(item) for item in history), str(case.get("message", "")), " ".join(topics)]
    return " ".join(part for part in parts if part).strip()


def next_action_for_temperature(temperature: str) -> str:
    if temperature == "hot":
        return "schedule_contact"
    if temperature == "warm":
        return "offer_case_study"
    return "continue_nurture"


def normalize_tokens(value: str) -> set[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "as",
        "for",
        "have",
        "is",
        "me",
        "not",
        "of",
        "or",
        "our",
        "the",
        "this",
        "to",
        "with",
    }
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if token not in stopwords}


def label_matches(expected: str, actual_values: list[str]) -> bool:
    expected_low = expected.lower()
    expected_tokens = normalize_tokens(expected)
    for actual in actual_values:
        actual_low = actual.lower()
        if expected_low in actual_low or actual_low in expected_low:
            return True
        if expected_tokens and expected_tokens.intersection(normalize_tokens(actual)):
            return True
    return False


def list_recall(expected_values: list[str], actual_values: list[str]) -> float | None:
    if not expected_values:
        return None
    return sum(1 for expected in expected_values if label_matches(str(expected), actual_values)) / len(expected_values)


def evaluate(kb: KnowledgeBase, cases: list[dict[str, Any]], k_hit: int = 3, k_recall: int = 5) -> dict[str, Any]:
    if not cases:
        raise ValueError("No evaluation cases found")
    hit_count = 0
    recall_sum = 0.0
    reciprocal_rank_sum = 0.0
    missing_expected: list[str] = []
    no_hit_cases: list[dict[str, Any]] = []
    latencies_ms: list[float] = []

    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        expected_ids = set((case.get("expected_retrieval") or {}).get("chunk_ids") or [])
        if not expected_ids:
            missing_expected.append(case_id)
            continue

        start = time.perf_counter()
        hits = kb.search(query_for_case(case), k=max(k_hit, k_recall))
        latencies_ms.append((time.perf_counter() - start) * 1000)
        hit_ids = [hit.id for hit in hits]
        hit_ids_at_k = hit_ids[:k_hit]
        hit_ids_for_recall = hit_ids[:k_recall]

        if expected_ids.intersection(hit_ids_at_k):
            hit_count += 1
        else:
            no_hit_cases.append({"id": case_id, "expected": sorted(expected_ids), "got": hit_ids_at_k})

        recall_sum += len(expected_ids.intersection(hit_ids_for_recall)) / len(expected_ids)
        first_rank = next((index + 1 for index, hit_id in enumerate(hit_ids_for_recall) if hit_id in expected_ids), None)
        if first_rank is not None:
            reciprocal_rank_sum += 1 / first_rank

    scored_cases = len(cases) - len(missing_expected)
    if scored_cases <= 0:
        raise ValueError("No cases with expected_retrieval.chunk_ids found")

    p95_latency_ms = max(latencies_ms) if len(latencies_ms) < 2 else statistics.quantiles(latencies_ms, n=20)[18]
    return {
        "valid_kb_documents": len(kb.chunks),
        "valid_jsonl_cases": len(cases),
        "scored_retrieval_cases": scored_cases,
        f"hit_rate_at_{k_hit}": hit_count / scored_cases,
        f"hit_count_at_{k_hit}": hit_count,
        f"recall_at_{k_recall}": recall_sum / scored_cases,
        f"mrr_at_{k_recall}": reciprocal_rank_sum / scored_cases,
        "p95_retrieval_ms": p95_latency_ms,
        "cases_missing_expected_retrieval": missing_expected,
        "no_hit_cases": no_hit_cases,
    }


def evaluate_observation_and_scoring(cases: list[dict[str, Any]]) -> dict[str, Any]:
    if not cases:
        raise ValueError("No evaluation cases found")

    intent_matches = 0
    sentiment_matches = 0
    temperature_matches = 0
    action_matches = 0
    false_sensitive_demographic_inferences = 0
    pain_recalls: list[float] = []
    objection_recalls: list[float] = []
    buying_recalls: list[float] = []
    topic_recalls: list[float] = []
    recall_buckets = {
        "pain_points": pain_recalls,
        "objections": objection_recalls,
        "buying_signals": buying_recalls,
        "recommended_rag_topics": topic_recalls,
    }
    mismatches: list[dict[str, Any]] = []

    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        history = [str(item) for item in (case.get("history") or [])]
        message = str(case.get("message", ""))
        observation = build_observation(lead_id=case_id, channel="chat", message=message, history=history)
        analysis = analyze_observation(observation)
        lead_state = score_lead(case_id, history, message, analysis)
        predicted_action = next_action_for_temperature(lead_state.temperature)

        expected_observation = case.get("expected_observation") or {}
        expected_scoring = case.get("expected_scoring") or {}

        case_mismatches: dict[str, Any] = {"id": case_id}
        if analysis.intent == expected_observation.get("intent"):
            intent_matches += 1
        else:
            case_mismatches["intent"] = {"expected": expected_observation.get("intent"), "actual": analysis.intent}

        if analysis.sentiment.label == expected_observation.get("sentiment"):
            sentiment_matches += 1
        else:
            case_mismatches["sentiment"] = {"expected": expected_observation.get("sentiment"), "actual": analysis.sentiment.label}

        if lead_state.temperature == expected_scoring.get("temperature"):
            temperature_matches += 1
        else:
            case_mismatches["temperature"] = {"expected": expected_scoring.get("temperature"), "actual": lead_state.temperature, "score": lead_state.score}

        if predicted_action == expected_scoring.get("next_best_action"):
            action_matches += 1
        else:
            case_mismatches["next_best_action"] = {"expected": expected_scoring.get("next_best_action"), "actual": predicted_action}

        for key, actual in [
            ("pain_points", analysis.pain_points),
            ("objections", analysis.objections),
            ("buying_signals", analysis.buying_signals),
            ("recommended_rag_topics", analysis.recommended_rag_topics),
        ]:
            expected_values = [str(value) for value in expected_observation.get(key, [])]
            recall = list_recall(expected_values, actual)
            if recall is not None:
                recall_buckets[key].append(recall)
                if recall < 1.0:
                    case_mismatches[key] = {"expected": expected_values, "actual": actual, "recall": recall}

        compliance = case.get("compliance") or {}
        if not compliance.get("sensitive_inference_allowed", False) and (analysis.demographics.age_range or analysis.demographics.gender):
            false_sensitive_demographic_inferences += 1
            case_mismatches["sensitive_demographics"] = analysis.demographics.model_dump()

        if len(case_mismatches) > 1:
            mismatches.append(case_mismatches)

    total = len(cases)
    return {
        "observation_scored_cases": total,
        "intent_accuracy": intent_matches / total,
        "sentiment_label_accuracy": sentiment_matches / total,
        "pain_point_recall_approx": sum(pain_recalls) / len(pain_recalls) if pain_recalls else None,
        "objection_recall_approx": sum(objection_recalls) / len(objection_recalls) if objection_recalls else None,
        "buying_signal_recall_approx": sum(buying_recalls) / len(buying_recalls) if buying_recalls else None,
        "recommended_topic_recall_approx": sum(topic_recalls) / len(topic_recalls) if topic_recalls else None,
        "temperature_accuracy": temperature_matches / total,
        "next_action_accuracy": action_matches / total,
        "false_sensitive_demographic_inference_count": false_sensitive_demographic_inferences,
        "observation_scoring_mismatches": mismatches,
    }


def evaluate_compliance_fixture_invariants(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate source-backed compliance fixture labels before a real gate exists.

    This is intentionally a fixture-consistency baseline, not a claim that the
    application enforces these rules yet. It checks whether labeled compliance
    cases encode the proposed ComplianceGate result contract in a way future
    implementation tests can consume deterministically.
    """
    compliance_cases = 0
    send_block_cases = 0
    stop_contact_cases = 0
    human_review_cases = 0
    provider_event_cases = 0
    missing_required_field_cases = 0
    draft_allowed_cases = 0
    violations: list[dict[str, Any]] = []

    blocking_provider_events = {"spam_report", "complaint", "bounce", "dropped", "unsubscribe"}
    blocking_missing_fields = {"unsubscribe_url", "postal_address", "reviewer_approval", "fresh_thread_review"}

    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        compliance = case.get("compliance") or {}
        if not compliance:
            continue

        tracked_keys = {
            "must_stop_contact",
            "send_allowed",
            "draft_allowed",
            "requires_human_review",
            "suppression_reason",
            "provider_event_types",
            "missing_required_fields",
            "compliance_action",
            "review_requirements",
        }
        if not tracked_keys.intersection(compliance):
            continue

        compliance_cases += 1
        send_allowed = compliance.get("send_allowed")
        must_stop = bool(compliance.get("must_stop_contact", False))
        requires_review = bool(compliance.get("requires_human_review", False))
        provider_events = set(str(event) for event in compliance.get("provider_event_types", []))
        missing_fields = set(str(field) for field in compliance.get("missing_required_fields", []))
        compliance_action = compliance.get("compliance_action")

        if send_allowed is False:
            send_block_cases += 1
        if must_stop:
            stop_contact_cases += 1
        if requires_review:
            human_review_cases += 1
        if provider_events:
            provider_event_cases += 1
        if missing_fields:
            missing_required_field_cases += 1
        if compliance.get("draft_allowed") is True:
            draft_allowed_cases += 1

        case_violations: list[str] = []
        if must_stop and send_allowed is not False:
            case_violations.append("must_stop_contact requires send_allowed=false")
        if provider_events.intersection(blocking_provider_events) and send_allowed is not False:
            case_violations.append("blocking provider event requires send_allowed=false")
        if missing_fields.intersection(blocking_missing_fields) and send_allowed is not False:
            case_violations.append("blocking missing field requires send_allowed=false")
        if send_allowed is False and (must_stop or provider_events or missing_fields) and not (
            compliance.get("suppression_reason") or compliance_action or missing_fields
        ):
            case_violations.append("blocked case should expose suppression_reason, compliance_action, or missing_required_fields")
        if requires_review and send_allowed is True:
            case_violations.append("requires_human_review should not be sendable before review")

        if case_violations:
            violations.append({"id": case_id, "violations": case_violations})

    return {
        "compliance_fixture_cases": compliance_cases,
        "compliance_send_block_cases": send_block_cases,
        "compliance_must_stop_contact_cases": stop_contact_cases,
        "compliance_requires_human_review_cases": human_review_cases,
        "compliance_provider_event_cases": provider_event_cases,
        "compliance_missing_required_field_cases": missing_required_field_cases,
        "compliance_draft_allowed_internal_cases": draft_allowed_cases,
        "compliance_fixture_invariant_violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate research JSONL fixtures and run TF-IDF retrieval smoke metrics.")
    parser.add_argument("--kb-fixture", type=Path, default=Path("research/fixtures/kb_documents.jsonl"))
    parser.add_argument("--cases", type=Path, default=Path("research/fixtures/lead_nurture_eval_cases.jsonl"))
    parser.add_argument("--out", type=Path, default=None, help="Optional JSON output path")
    parser.add_argument("--k-hit", type=int, default=3)
    parser.add_argument("--k-recall", type=int, default=5)
    args = parser.parse_args()

    kb = load_kb(args.kb_fixture)
    cases = iter_jsonl(args.cases)
    result = evaluate(kb, cases, k_hit=args.k_hit, k_recall=args.k_recall)
    result.update(evaluate_observation_and_scoring(cases))
    result.update(evaluate_compliance_fixture_invariants(cases))

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)

    if result["no_hit_cases"] or result["cases_missing_expected_retrieval"] or result["compliance_fixture_invariant_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
