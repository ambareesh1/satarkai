"""SatarkAI - Flask dashboard.

Exposes the multi-channel scam engine over a small JSON API and serves a
single-page dashboard with an "analyze-anything" box, live verdicts, a unified
cross-channel history, and stats.

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from satark import ScamEngine, Message, CHANNELS
from satark.message import CHANNEL_LABELS
from satark import store
from satark.samples import SAMPLES

app = Flask(__name__)

store.init()
_engine = ScamEngine(use_llm=True)


@app.route("/")
def index():
    return render_template(
        "index.html",
        channels=[{"id": c, "label": CHANNEL_LABELS[c]} for c in CHANNELS],
        llm_active=_engine.llm_active,
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a message to analyze."}), 400

    channel = data.get("channel") or "sms"
    if channel not in CHANNELS:
        channel = "sms"

    msg = Message(
        text=text,
        channel=channel,
        sender=(data.get("sender") or "").strip(),
        subject=(data.get("subject") or "").strip(),
    )
    det = _engine.analyze(msg)
    det_id = store.record(msg, det)

    result = det.to_dict()
    result["id"] = det_id
    result["channel"] = channel
    result["channel_label"] = CHANNEL_LABELS[channel]
    return jsonify({"ok": True, "result": result})


@app.route("/history")
def history():
    return jsonify({"items": store.recent(limit=50)})


@app.route("/stats")
def stats():
    return jsonify(store.stats())


@app.route("/samples")
def samples():
    items = []
    for i, s in enumerate(SAMPLES):
        items.append({
            "id": i,
            "channel": s["channel"],
            "channel_label": CHANNEL_LABELS.get(s["channel"], s["channel"]),
            "label": s["label"],
            "sender": s.get("sender", ""),
            "subject": s.get("subject", ""),
            "text": s["text"],
        })
    return jsonify({"samples": items})


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    det_id = data.get("id")
    label = data.get("label")
    if det_id is None or label not in ("scam", "safe"):
        return jsonify({"ok": False, "error": "Invalid feedback."}), 400
    ok = store.set_feedback(int(det_id), label)
    return jsonify({"ok": ok})


@app.route("/health")
def health():
    return jsonify({"ok": True, "llm": _engine.llm_active})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
