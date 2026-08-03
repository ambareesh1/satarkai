"""Lightweight URL & sender reputation heuristics (no network calls).

Catches the classic tricks: link shorteners hiding the real destination,
throwaway TLDs, and brand-lookalike domains (e.g. `sbi-kyc-verify.xyz`).
"""

from __future__ import annotations

from typing import Any, Dict, List

# Brands commonly impersonated in India + their legit domains.
_BRANDS = {
    "sbi": "onlinesbi.sbi", "hdfc": "hdfcbank.com", "icici": "icicibank.com",
    "axis": "axisbank.com", "kotak": "kotak.com", "pnb": "pnbindia.in",
    "paytm": "paytm.com", "phonepe": "phonepe.com", "gpay": "pay.google.com",
    "amazon": "amazon.in", "flipkart": "flipkart.com", "irctc": "irctc.co.in",
    "epfo": "epfindia.gov.in", "income tax": "incometax.gov.in",
    "aadhaar": "uidai.gov.in", "trai": "trai.gov.in",
}

_SUSPECT_TLDS = {
    "xyz", "top", "club", "online", "site", "info", "link", "buzz", "shop",
    "live", "vip", "cfd", "icu", "work", "fit", "store", "rest", "gq", "tk",
}

_URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly",
    "rebrand.ly", "rb.gy", "shorturl.at", "t.ly", "bl.ink", "tiny.cc",
}


def assess_urls(domains: List[str]) -> Dict[str, Any]:
    """Return reputation signals for a list of domains."""
    flags: List[str] = []
    score = 0
    for d in domains:
        d = d.lower()
        tld = d.rsplit(".", 1)[-1] if "." in d else ""

        if d in _URL_SHORTENERS:
            score += 2
            flags.append(f"Shortened link hides destination ({d})")
            continue

        if tld in _SUSPECT_TLDS:
            score += 2
            flags.append(f"Throwaway domain (.{tld}): {d}")

        for brand, legit in _BRANDS.items():
            token = brand.replace(" ", "")
            if token in d.replace("-", "").replace(".", "") and not d.endswith(legit):
                score += 3
                flags.append(f"Fake '{brand}' domain: {d} (official is {legit})")
                break

    return {"score": min(score, 6), "flags": flags}


def assess_sender(channel: str, sender: str, domains: List[str]) -> Dict[str, Any]:
    """Sender-level heuristics (mainly for email display-name/domain mismatch)."""
    flags: List[str] = []
    score = 0
    s = (sender or "").lower()

    if channel == "email" and "@" in s:
        sender_domain = s.split("@")[-1].strip("> ")
        for brand, legit in _BRANDS.items():
            token = brand.replace(" ", "")
            if token in s and legit not in sender_domain:
                score += 2
                flags.append(f"Email claims to be '{brand}' but domain is {sender_domain}")
                break
        if any(sender_domain.endswith("." + t) or sender_domain.endswith(t) for t in _SUSPECT_TLDS):
            score += 1
            flags.append(f"Sender uses a throwaway domain: {sender_domain}")

    # SMS from a 10-digit personal mobile impersonating an org is a classic tell.
    if channel == "sms" and sender and sender.replace("+91", "").isdigit() and len(sender.replace("+91", "")) == 10:
        flags.append("SMS from a personal 10-digit number (banks use short sender IDs)")
        score += 1

    return {"score": min(score, 4), "flags": flags}
