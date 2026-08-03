"""Risk fusion: turn raw signals into a 0-100 score + human reasons.

The score blends four signal sources:
  * category pattern strength (the dominant driver)
  * dangerous entities (UPI request, links, OTP ask, urgent money)
  * URL / sender reputation
  * urgency & threat language (multipliers)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from . import patterns
from .message import Message, Detection, level_for, action_for
from .reputation import assess_urls, assess_sender


def _category_points(cat_score: int) -> int:
    """Map a category's matched-weight sum to points (diminishing returns)."""
    # 3 -> 45, 5 -> 60, 6+ -> 70, saturating.
    table = {0: 0, 1: 22, 2: 35, 3: 47, 4: 55, 5: 62, 6: 68}
    return table.get(cat_score, 72 if cat_score >= 7 else 0)


def score(message: Message) -> Detection:
    text = message.combined_text()
    from .entities import extract  # local import to avoid cycle at import time

    ent = extract(text)
    cats = patterns.scan(text)
    low = text.lower()

    # A request to hand over an OTP/PIN/CVV is one of the strongest tells there
    # is - promote it to a full category hit even if phrasing dodged the library.
    _share_verbs = ("share", "tell", "send", "enter", "read", "give", "provide",
                    "batao", "bataye", "bhejo", "bhej", "confirm")
    # Legit OTP messages say "do NOT share" - don't mistake that for a request.
    _protective = ("do not share", "don't share", "dont share", "never share",
                   "do not disclose", "never disclose", "not share it with anyone",
                   "kisi ko mat", "kisi ko na", "mat batao", "kisi se share na")
    is_protective = any(p in low for p in _protective)
    otp_ask = (bool(ent["otp_terms"]) and any(v in low for v in _share_verbs)
               and not is_protective)
    if otp_ask:
        cur = cats.get("otp_pin", {"score": 0, "matched": []})
        cur["score"] = max(cur["score"], 4)
        cur.setdefault("matched", []).append("asks you to share an OTP/PIN/CVV")
        cats["otp_pin"] = cur

    reasons: List[str] = []
    matched_all: List[str] = []
    points = 0

    # --- 1) strongest category ------------------------------------------- #
    top_cat = "none"
    top_label = "No known scam pattern"
    advice = "No obvious scam signals. Still, never share OTP/PIN or pay strangers."
    if cats:
        top_cat = max(cats, key=lambda c: cats[c]["score"])
        cat_score = cats[top_cat]["score"]
        points += _category_points(cat_score)
        meta = patterns.CATEGORIES[top_cat]
        top_label = meta["label"]
        advice = meta["advice"]
        matched_all = cats[top_cat]["matched"]
        reasons.append(f"Matches '{top_label}' scam pattern")
        # secondary categories add a little.
        for c in cats:
            if c != top_cat:
                points += min(cats[c]["score"], 3) * 2

    # --- 2) dangerous entities ------------------------------------------- #
    if otp_ask:
        points += 20
        reasons.append("Asks you to share an OTP / PIN / CVV (never do this)")
    elif ent["otp_terms"]:
        points += 6
        reasons.append("Mentions an OTP / PIN / CVV")
    if ent["upi"]:
        points += 12
        reasons.append(f"Contains a UPI ID to pay ({', '.join(ent['upi'][:2])})")
    if ent["shorteners"]:
        points += 8
        reasons.append("Contains a shortened link that hides its real destination")
    elif ent["urls"]:
        points += 6
        reasons.append("Contains a clickable link")
    if ent["amounts"]:
        points += 4
        reasons.append(f"Mentions money ({', '.join(ent['amounts'][:2])})")

    # --- 3) URL & sender reputation -------------------------------------- #
    url_rep = assess_urls(ent["domains"])
    points += url_rep["score"] * 3
    for f in url_rep["flags"]:
        reasons.append(f)
    matched_all += url_rep["flags"]

    sender_rep = assess_sender(message.channel, message.sender, ent["domains"])
    points += sender_rep["score"] * 3
    for f in sender_rep["flags"]:
        reasons.append(f)

    # --- 4) urgency & threat language ------------------------------------ #
    urgency = patterns.find_terms(text, patterns.URGENCY_TERMS)
    threat = patterns.find_terms(text, patterns.THREAT_TERMS)
    if urgency:
        points += 8
        reasons.append("Creates false urgency / time pressure")
    if threat:
        points += 8
        reasons.append("Uses fear / threat of legal or account action")

    # A category hit + urgency + a payment/link ask is the classic combo.
    if cats and (ent["upi"] or ent["urls"]) and (urgency or threat):
        points += 6

    risk = max(0, min(100, int(round(points))))
    level = level_for(risk)

    # Confidence: how many independent signal types fired.
    signal_types = sum(bool(x) for x in [
        cats, ent["upi"], ent["urls"], ent["otp_terms"], urgency, threat,
        url_rep["flags"], sender_rep["flags"],
    ])
    confidence = min(0.95, 0.35 + 0.12 * signal_types) if risk >= 40 else max(0.5, 0.9 - 0.1 * signal_types)

    if not reasons:
        reasons.append("No scam indicators found")

    return Detection(
        risk=risk,
        level=level,
        category=top_cat,
        category_label=top_label if cats else "None",
        confidence=confidence,
        reasons=reasons,
        entities=ent,
        advice=advice,
        action=action_for(level),
        matched=sorted(set(matched_all)),
        engine="rules",
    )
