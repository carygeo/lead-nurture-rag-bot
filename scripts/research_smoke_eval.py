from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

from lead_nurture_rag.models import KnowledgeChunk
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

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)

    if result["no_hit_cases"] or result["cases_missing_expected_retrieval"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
