"""SatarkAI - Flask dashboard.

The rule engine is the production path. Optional LLM / TTS / email only
augment it; the app stays usable with Flask + the local rules.

Run:
    python app.py
Then open http://127.0.0.1:7000
"""

from __future__ import annotations

import logging
import os

from flask import Flask, Response, jsonify, render_template, request

from satark.env import load_dotenv
load_dotenv()  # pull optional keys from .env before anything reads os.environ

from satark import ScamEngine, Message, CHANNELS
from satark.message import CHANNEL_LABELS
from satark import store, report as report_mod, mailer, tts
from satark.samples import SAMPLES
from satark.inbox import list_inbox, apps_summary

MAX_TEXT = 8000

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
app.config["SECRET_KEY"] = os.environ.get("SATARK_SECRET", "satark-local-dev")
app.logger.setLevel(logging.INFO)

store.init()
_engine = ScamEngine(use_llm=os.environ.get("SATARK_USE_LLM", "1") != "0")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    return render_template(
        "index.html",
        channels=[{"id": c, "label": CHANNEL_LABELS[c]} for c in CHANNELS],
        llm_active=_engine.llm_active,
        voice_active=tts.configured(),
        email_active=mailer.configured(),
    )


@app.route("/apps")
def apps():
    return jsonify({"apps": apps_summary()})


@app.route("/inbox")
def inbox():
    return jsonify({"items": list_inbox()})


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a message to analyze."}), 400
    if len(text) > MAX_TEXT:
        return jsonify({"ok": False, "error": f"Message is too long (max {MAX_TEXT} characters)."}), 400

    channel = data.get("channel") or "sms"
    if channel not in CHANNELS:
        channel = "sms"

    msg = Message(
        text=text,
        channel=channel,
        sender=(data.get("sender") or "").strip()[:200],
        subject=(data.get("subject") or "").strip()[:300],
    )
    try:
        det = _engine.analyze(msg)
        det_id = store.record(msg, det)
    except Exception:
        app.logger.exception("Rule engine failed")
        return jsonify({"ok": False, "error": "Analysis failed. Please try again."}), 500

    result = det.to_dict()
    result["id"] = det_id
    result["channel"] = channel
    result["channel_label"] = CHANNEL_LABELS[channel]
    result.setdefault("engine", "rules")
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


@app.route("/report/daily")
def report_daily():
    rep = report_mod.build("today")
    rep["text"] = report_mod.render_text(rep)
    rep["email_available"] = mailer.configured()
    return jsonify(rep)


@app.route("/report/email", methods=["POST"])
def report_email():
    data = request.get_json(silent=True) or {}
    to = (data.get("to") or "").strip() or None
    rep = report_mod.build("today")
    if not mailer.configured():
        return jsonify({
            "ok": False,
            "error": "Email not configured. Add SMTP_* to your .env to enable daily report emails.",
        }), 400
    try:
        sent = mailer.send_report(
            subject=f"SatarkAI Daily Scam Report — {rep['date']}",
            text=report_mod.render_text(rep),
            html=report_mod.render_html(rep),
            to=to,
        )
        return jsonify({"ok": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/tts", methods=["POST"])
def tts_route():
    """Return MP3 audio if ElevenLabs is configured, else 204 (use Web Speech)."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "No text"}), 400
    if not tts.configured():
        return ("", 204)
    try:
        audio = tts.synthesize(text)
        if not audio:
            return ("", 204)
        return Response(audio, mimetype="audio/mpeg")
    except Exception:
        return ("", 204)


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "engine": "rules",
        "engine_ready": True,
        "llm": _engine.llm_active,
        "voice": tts.configured(),
        "email": mailer.configured(),
    })


if __name__ == "__main__":
    host = os.environ.get("SATARK_HOST", "0.0.0.0")
    port = int(os.environ.get("SATARK_PORT", "7000"))
    try:
        from waitress import serve
        print(f"SatarkAI ready  http://127.0.0.1:{port}  (rule engine live)", flush=True)
        serve(app, host=host, port=port, threads=8)
    except ImportError:
        app.run(host=host, port=port, debug=False)
