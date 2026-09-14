"""ScamEngine - the single brain every channel talks to.

Pipeline:  Message -> rule-based risk -> (optional) LLM refinement -> Detection
The LLM layer only augments; if it's unavailable the rule verdict stands.
"""

from __future__ import annotations

from typing import Optional

from .message import Message, Detection, level_for, action_for
from . import risk as risk_mod


class ScamEngine:
    def __init__(self, use_llm: bool = True) -> None:
        self.use_llm = use_llm
        self._llm = None
        if use_llm:
            try:
                from . import llm
                if llm.configured():
                    self._llm = llm
            except Exception:
                self._llm = None

    @property
    def llm_active(self) -> bool:
        return self._llm is not None

    def analyze(self, message: Message) -> Detection:
        text = (message.text or "").strip()
        if not text and not (message.subject or "").strip():
            return Detection(
                risk=0,
                level="SAFE",
                category="none",
                category_label="None",
                confidence=0.9,
                reasons=["No message text to analyze"],
                entities={"upi": [], "urls": [], "domains": [], "shorteners": [],
                          "emails": [], "phones": [], "amounts": [], "otp_terms": []},
                advice="Paste the full message so SatarkAI can score it.",
                action=action_for("SAFE"),
                matched=[],
                engine="rules",
            )

        det = risk_mod.score(message)

        if self._llm is not None:
            try:
                refined = self._llm.refine(message, det)
                if refined is not None:
                    det = refined
            except Exception:
                pass  # never let the LLM break a verdict

        if not getattr(det, "engine", None):
            det.engine = "rules"
        return det

    def analyze_text(self, text: str, channel: str = "sms",
                     sender: str = "", subject: str = "") -> Detection:
        return self.analyze(Message(text=text, channel=channel,
                                    sender=sender, subject=subject))
