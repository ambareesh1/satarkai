"""Optional LLM intent layer via OpenRouter.

Enabled only when OPENROUTER_API_KEY is set AND `requests` is installed.
It never runs the show: it can nudge the risk a little and add a clearer,
human explanation, but the rule engine remains the safety net.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .message import Message, Detection, level_for, action_for

_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def configured() -> bool:
    if not os.environ.get("OPENROUTER_API_KEY"):
        return False
    try:
        import requests  # noqa: F401
        return True
    except Exception:
        return False


_SYSTEM = (
    "You are SatarkAI, an expert at detecting scam/fraud messages targeting people in India "
    "across SMS, WhatsApp, email, phone-call transcripts and app notifications. "
    "You understand English, Hindi and Hinglish. Given a message and a preliminary rule-based "
    "verdict, respond with STRICT JSON only: "
    '{"risk": <0-100 int>, "category_label": <short string>, '
    '"reasons": [<up to 4 short strings>], "advice": <one short actionable sentence>}. '
    "Be decisive: obvious scams should score 80-99, clearly safe messages 0-20."
)


def refine(message: Message, det: Detection) -> Optional[Detection]:
    """Ask the LLM to refine the verdict. Returns a new Detection or None."""
    try:
        import requests
    except Exception:
        return None

    payload = {
        "model": _MODEL,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": json.dumps({
                "channel": message.channel,
                "sender": message.sender,
                "subject": message.subject,
                "message": message.text[:4000],
                "rule_verdict": {
                    "risk": det.risk,
                    "category": det.category_label,
                    "reasons": det.reasons,
                },
            }, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/satarkai",
        "X-Title": "SatarkAI",
    }

    resp = requests.post(_API_URL, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)

    # Blend LLM risk with rule risk (favor the higher for safety).
    # Production rule: a rule-engine SCAM can never be talked down to SAFE.
    llm_risk = int(max(0, min(100, data.get("risk", det.risk))))
    blended = max(det.risk, llm_risk) if llm_risk >= det.risk else int(round(0.6 * llm_risk + 0.4 * det.risk))
    if det.level == "SCAM":
        blended = max(blended, 70)
    elif det.level == "SUSPICIOUS":
        blended = max(blended, 40)
    level = level_for(blended)

    reasons = data.get("reasons") or det.reasons
    if isinstance(reasons, str):
        reasons = [reasons]

    return Detection(
        risk=blended,
        level=level,
        category=det.category,
        category_label=data.get("category_label") or det.category_label,
        confidence=max(det.confidence, 0.8),
        reasons=list(reasons)[:5],
        entities=det.entities,
        advice=data.get("advice") or det.advice,
        action=action_for(level),
        matched=det.matched,
        engine="rules+llm",
    )
