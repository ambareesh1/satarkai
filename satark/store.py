"""SQLite-backed history, stats and user feedback.

Keeps a rolling log of every analyzed message so the dashboard can show a
unified cross-channel timeline and simple statistics.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

from .message import Message, Detection

_DB_PATH = os.environ.get("SATARK_DB", "satark.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                channel TEXT NOT NULL,
                sender TEXT,
                subject TEXT,
                text TEXT NOT NULL,
                risk INTEGER NOT NULL,
                level TEXT NOT NULL,
                category TEXT,
                category_label TEXT,
                reasons TEXT,
                advice TEXT,
                engine TEXT,
                feedback TEXT
            )
            """
        )
        conn.commit()


def record(message: Message, det: Detection) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO detections
               (ts, channel, sender, subject, text, risk, level, category,
                category_label, reasons, advice, engine, feedback)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                message.timestamp, message.channel, message.sender, message.subject,
                message.text, det.risk, det.level, det.category, det.category_label,
                json.dumps(det.reasons), det.advice, det.engine, None,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def recent(limit: int = 50) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["reasons"] = json.loads(d.get("reasons") or "[]")
        except Exception:
            d["reasons"] = []
        d["text_preview"] = (d["text"] or "")[:140]
        out.append(d)
    return out


def since(ts: float, limit: int = 500) -> List[Dict[str, Any]]:
    """All detections with timestamp >= ts (newest first)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM detections WHERE ts >= ? ORDER BY id DESC LIMIT ?",
            (ts, limit),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["reasons"] = json.loads(d.get("reasons") or "[]")
        except Exception:
            d["reasons"] = []
        out.append(d)
    return out


def set_feedback(det_id: int, label: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE detections SET feedback=? WHERE id=?", (label, det_id)
        )
        conn.commit()
        return cur.rowcount > 0


def stats() -> Dict[str, Any]:
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        scams = conn.execute(
            "SELECT COUNT(*) FROM detections WHERE level='SCAM'"
        ).fetchone()[0]
        suspicious = conn.execute(
            "SELECT COUNT(*) FROM detections WHERE level='SUSPICIOUS'"
        ).fetchone()[0]
        by_channel = {
            row["channel"]: row["n"]
            for row in conn.execute(
                "SELECT channel, COUNT(*) n FROM detections GROUP BY channel"
            ).fetchall()
        }
        by_category = {
            row["category_label"]: row["n"]
            for row in conn.execute(
                "SELECT category_label, COUNT(*) n FROM detections "
                "WHERE level!='SAFE' GROUP BY category_label ORDER BY n DESC LIMIT 6"
            ).fetchall()
        }
    return {
        "total": total,
        "scams": scams,
        "suspicious": suspicious,
        "safe": total - scams - suspicious,
        "by_channel": by_channel,
        "by_category": by_category,
    }
