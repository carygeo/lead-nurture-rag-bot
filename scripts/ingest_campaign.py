from __future__ import annotations

import argparse
import json
from pathlib import Path

from lead_nurture_rag.crawler import CampaignConfig, crawl_campaign
from lead_nurture_rag.retriever import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl a campaign website and build the local RAG knowledge base.")
    parser.add_argument("campaign", help="Path to campaign JSON config")
    parser.add_argument("--knowledge", default="data/knowledge.json", help="Path to persisted knowledge JSON")
    args = parser.parse_args()

    payload = json.loads(Path(args.campaign).read_text(encoding="utf-8"))
    config = CampaignConfig(**payload)
    kb = KnowledgeBase(args.knowledge)
    docs = crawl_campaign(config)
    chunk_ids = kb.add_documents(docs)

    print(json.dumps({
        "company_name": config.company_name,
        "pages_crawled": len(docs),
        "chunks_added_or_seen": len(chunk_ids),
        "chunks_total": len(kb.chunks),
        "pages": [{"url": doc.url, "title": doc.title, "metadata": doc.metadata} for doc in docs],
    }, indent=2))


if __name__ == "__main__":
    main()
