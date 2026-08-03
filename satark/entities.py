"""Entity extraction: pull the concrete "scam ingredients" out of raw text.

These signals (a UPI id, a shortened link, an OTP request, an urgent amount)
are strong, channel-independent indicators and feed directly into the score.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

# --- regexes -------------------------------------------------------------- #
_UPI_RE = re.compile(r"\b[\w.\-]{2,}@(?:ok\w+|ybl|paytm|apl|axl|ibl|upi|sbi|hdfc|icici|axis|okhdfcbank|okaxis|oksbi|okicici)\b", re.I)
_URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>\"')]+", re.I)
# Bare domains like sbi-verify.xyz/login (no scheme) - keep it conservative.
_BARE_DOMAIN_RE = re.compile(r"\b[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.(?:xyz|top|club|online|site|info|link|buzz|shop|live|vip|cfd|icu|work|fit|store)\b(?:/[^\s]*)?", re.I)
_EMAIL_RE = re.compile(r"\b[\w.\-]+@[\w\-]+\.[\w.\-]+\b")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\-\s]?)?[6-9]\d{9}(?!\d)")
# amounts: Rs 25,000 / ₹25000 / 5 lakh / 2 crore
_AMOUNT_RE = re.compile(r"(?:₹|rs\.?|inr)\s?([\d,]+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s?(lakh|lakhs|lac|crore|cr)\b", re.I)
_OTP_RE = re.compile(r"\b(otp|o\.t\.p|one[\s\-]?time[\s\-]?password|cvv|pin|password|passcode)\b", re.I)

_URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly",
    "rebrand.ly", "rb.gy", "shorturl.at", "t.ly", "bl.ink", "tiny.cc",
}


def _domain_of(url: str) -> str:
    u = re.sub(r"^https?://", "", url, flags=re.I)
    u = re.sub(r"^www\.", "", u, flags=re.I)
    return u.split("/")[0].split("?")[0].lower()


def extract(text: str) -> Dict[str, Any]:
    """Return a dict of extracted entities for `text`."""
    if not text:
        text = ""

    upis = sorted(set(m.group(0) for m in _UPI_RE.finditer(text)))

    urls_raw = [m.group(0).rstrip(".,);") for m in _URL_RE.finditer(text)]
    urls_raw += [m.group(0).rstrip(".,);") for m in _BARE_DOMAIN_RE.finditer(text)]
    urls: List[str] = []
    for u in urls_raw:
        if u not in urls:
            urls.append(u)

    domains = sorted({_domain_of(u) for u in urls})
    shorteners = sorted(d for d in domains if d in _URL_SHORTENERS)

    emails = sorted(set(_EMAIL_RE.findall(text)))
    # Don't double-count UPI ids as emails.
    emails = [e for e in emails if e not in upis]

    phones = sorted(set(re.sub(r"[\-\s]", "", p) for p in _PHONE_RE.findall(text)))

    amounts: List[str] = []
    for m in _AMOUNT_RE.finditer(text):
        val = m.group(0).strip()
        if val.lower() not in [a.lower() for a in amounts]:
            amounts.append(val)

    otp = sorted(set(m.lower() for m in _OTP_RE.findall(text)))

    return {
        "upi": upis,
        "urls": urls,
        "domains": domains,
        "shorteners": shorteners,
        "emails": emails,
        "phones": phones,
        "amounts": amounts,
        "otp_terms": otp,
    }
