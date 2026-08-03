"""Common data structures shared across every channel.

Every channel connector (call, sms, whatsapp, notification, email) normalizes
its raw input into a `Message`. The engine returns a `Detection`. Keeping these
two shapes fixed is what lets one brain serve every channel.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

CHANNELS = ("call", "sms", "whatsapp", "notification", "email")

# Human-friendly channel labels for the UI.
CHANNEL_LABELS = {
    "call": "Phone Call",
    "sms": "SMS",
    "whatsapp": "WhatsApp",
    "notification": "Notification",
    "email": "Email",
}

# Risk band thresholds (0-100).
SAFE_MAX = 39
SUSPICIOUS_MAX = 69  # >= 70 is treated as SCAM


@dataclass
class Message:
    """A normalized inbound message from any channel."""

    text: str
    channel: str = "sms"
    sender: str = ""
    subject: str = ""
    timestamp: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)

    def combined_text(self) -> str:
        """Subject + body, used for scanning email-like messages."""
        return f"{self.subject}\n{self.text}".strip() if self.subject else self.text


@dataclass
class Detection:
    """The verdict for a single message."""

    risk: int
    level: str  # SAFE / SUSPICIOUS / SCAM
    category: str
    category_label: str
    confidence: float
    reasons: List[str]
    entities: Dict[str, Any]
    advice: str
    action: str  # ALLOW / WARN / BLOCK
    matched: List[str] = field(default_factory=list)
    engine: str = "rules"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk": self.risk,
            "level": self.level,
            "category": self.category,
            "category_label": self.category_label,
            "confidence": round(self.confidence, 2),
            "reasons": self.reasons,
            "entities": self.entities,
            "advice": self.advice,
            "action": self.action,
            "matched": self.matched,
            "engine": self.engine,
        }


def level_for(risk: int) -> str:
    if risk <= SAFE_MAX:
        return "SAFE"
    if risk <= SUSPICIOUS_MAX:
        return "SUSPICIOUS"
    return "SCAM"


def action_for(level: str) -> str:
    return {"SAFE": "ALLOW", "SUSPICIOUS": "WARN", "SCAM": "BLOCK"}[level]
