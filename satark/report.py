"""Daily spam report generation (text + HTML).

Summarizes the last 24h (or since local midnight) of analyzed messages so
SatarkAI can show / email a "here's what tried to scam you today" digest.
"""

from __future__ import annotations

import time
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

from . import store


def _midnight_ts() -> float:
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()


def build(period: str = "today") -> Dict[str, Any]:
    ts = _midnight_ts() if period == "today" else time.time() - 86400
    rows = store.since(ts)

    scams = [r for r in rows if r["level"] == "SCAM"]
    suspicious = [r for r in rows if r["level"] == "SUSPICIOUS"]

    by_channel = Counter(r["channel"] for r in rows if r["level"] != "SAFE")
    by_category = Counter(r["category_label"] for r in scams + suspicious)
    top_senders = Counter(
        (r["sender"] or "unknown") for r in scams if (r["sender"] or "").strip()
    )

    threats = []
    for r in (scams + suspicious):
        threats.append({
            "channel": r["channel"],
            "sender": r["sender"] or "unknown",
            "risk": r["risk"],
            "level": r["level"],
            "category": r["category_label"],
            "preview": (r["text"] or "")[:120],
        })

    return {
        "date": datetime.now().strftime("%A, %d %B %Y"),
        "total": len(rows),
        "scams": len(scams),
        "suspicious": len(suspicious),
        "safe": len(rows) - len(scams) - len(suspicious),
        "by_channel": dict(by_channel),
        "by_category": dict(by_category.most_common(6)),
        "top_senders": dict(top_senders.most_common(5)),
        "threats": threats[:25],
    }


def render_text(rep: Dict[str, Any]) -> str:
    lines = [
        "SatarkAI — Daily Scam Report",
        rep["date"],
        "=" * 40,
        f"Messages analyzed : {rep['total']}",
        f"Scams blocked     : {rep['scams']}",
        f"Suspicious        : {rep['suspicious']}",
        f"Safe              : {rep['safe']}",
        "",
    ]
    if rep["by_category"]:
        lines.append("Top scam types:")
        for k, v in rep["by_category"].items():
            lines.append(f"  - {k}: {v}")
        lines.append("")
    if rep["top_senders"]:
        lines.append("Most active scam senders:")
        for k, v in rep["top_senders"].items():
            lines.append(f"  - {k}: {v}")
        lines.append("")
    if rep["threats"]:
        lines.append("Flagged messages:")
        for t in rep["threats"]:
            lines.append(f"  [{t['risk']:>3} {t['level']}] {t['channel']} · {t['sender']}")
            lines.append(f"        {t['category']} — {t['preview']}")
    lines.append("")
    lines.append("Report scams at cybercrime.gov.in or call 1930.")
    return "\n".join(lines)


def render_html(rep: Dict[str, Any]) -> str:
    rows = ""
    for t in rep["threats"]:
        color = "#ff5470" if t["level"] == "SCAM" else "#ffb020"
        rows += (
            f"<tr><td style='padding:6px 10px;font-weight:700;color:{color}'>{t['risk']} {t['level']}</td>"
            f"<td style='padding:6px 10px'>{t['channel']}</td>"
            f"<td style='padding:6px 10px'>{t['sender']}</td>"
            f"<td style='padding:6px 10px'>{t['category']}</td>"
            f"<td style='padding:6px 10px;color:#555'>{t['preview']}</td></tr>"
        )
    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:720px;margin:auto;color:#1b2333">
      <h2 style="color:#1a8cff">🛡️ SatarkAI — Daily Scam Report</h2>
      <p style="color:#667">{rep['date']}</p>
      <div style="display:flex;gap:10px;margin:14px 0">
        <div style="flex:1;background:#fff0f2;border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:26px;font-weight:800;color:#ff5470">{rep['scams']}</div><small>Scams</small></div>
        <div style="flex:1;background:#fff8e8;border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:26px;font-weight:800;color:#ffb020">{rep['suspicious']}</div><small>Suspicious</small></div>
        <div style="flex:1;background:#eefaf3;border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:26px;font-weight:800;color:#2fd18a">{rep['safe']}</div><small>Safe</small></div>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead><tr style="background:#f4f6fb;text-align:left">
          <th style="padding:6px 10px">Risk</th><th style="padding:6px 10px">Channel</th>
          <th style="padding:6px 10px">Sender</th><th style="padding:6px 10px">Type</th>
          <th style="padding:6px 10px">Preview</th></tr></thead>
        <tbody>{rows or '<tr><td colspan=5 style="padding:10px;color:#999">No threats today 🎉</td></tr>'}</tbody>
      </table>
      <p style="color:#889;font-size:12px;margin-top:16px">Report scams at cybercrime.gov.in or call 1930.</p>
    </div>
    """
