"""Regression test: the production rule engine must classify bundled samples."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satark import ScamEngine
from satark.inbox import INBOX, APP_CHANNEL
from satark.samples import SAMPLES

engine = ScamEngine(use_llm=False)
failed = []


def check(label, text, channel, sender, subject, want):
    det = engine.analyze_text(text, channel, sender, subject)
    ok = det.level == want and det.engine == "rules"
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] {label[:42]:42} {det.risk:>3} {det.level:11} (want {want})")
    if not ok:
        failed.append(f"{label}: got {det.level} want {want}")


print("SAMPLES")
for s in SAMPLES:
    want = "SAFE" if s["label"].lower().startswith("safe") else "SCAM"
    check(s["label"], s["text"], s["channel"], s.get("sender", ""), s.get("subject", ""), want)

print("INBOX")
for m in INBOX:
    want = "SCAM" if m.get("scam") else "SAFE"
    check(m.get("name") or m["sender"], m["text"], APP_CHANNEL.get(m["app"], "sms"),
          m.get("sender", ""), m.get("subject", ""), want)

if failed:
    print("\nRule engine regressions:")
    for f in failed:
        print(" -", f)
    sys.exit(1)

print("\nRule engine ready: all production fixtures classified correctly.")
