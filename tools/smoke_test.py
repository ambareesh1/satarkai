"""Quick smoke test: run the rule engine over the bundled samples."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satark import ScamEngine
from satark.samples import SAMPLES

engine = ScamEngine(use_llm=False)

print(f"{'MESSAGE':30} {'RISK':>4}  {'LEVEL':11} CATEGORY")
print("-" * 78)
for s in SAMPLES:
    det = engine.analyze_text(
        s["text"], s["channel"], s.get("sender", ""), s.get("subject", "")
    )
    print(f"{s['label'][:29]:30} {det.risk:>4}  {det.level:11} {det.category_label}")
    if det.reasons:
        print(f"    reasons: {'; '.join(det.reasons[:3])}")
