from __future__ import annotations

import sqlite3
from pathlib import Path


class ConversationStore:
    def __init__(self, path: str | Path = "data/leads.sqlite"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS leads (
                lead_id TEXT PRIMARY KEY,
                temperature TEXT NOT NULL,
                score INTEGER NOT NULL,
                rationale TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def append_turn(self, lead_id: str, role: str, content: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO turns (lead_id, role, content) VALUES (?, ?, ?)",
                (lead_id, role, content),
            )

    def get_history(self, lead_id: str) -> list[str]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT role, content FROM turns WHERE lead_id = ? ORDER BY id ASC", (lead_id,)
            ).fetchall()
        return [f"{role.capitalize()}: {content}" for role, content in rows]

    def upsert_lead(self, lead_id: str, temperature: str, score: int, rationale: str) -> None:
        with self._connect() as db:
            db.execute(
                """INSERT INTO leads (lead_id, temperature, score, rationale, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(lead_id) DO UPDATE SET
                    temperature=excluded.temperature,
                    score=excluded.score,
                    rationale=excluded.rationale,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (lead_id, temperature, score, rationale),
            )

    def list_leads(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT lead_id, temperature, score, rationale, updated_at FROM leads ORDER BY score DESC, updated_at DESC"
            ).fetchall()
        return [
            {"lead_id": r[0], "temperature": r[1], "score": r[2], "rationale": r[3], "updated_at": r[4]}
            for r in rows
        ]
