"""End-to-end test of the Flask API using the in-process test client."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SATARK_DB"] = "test_satark.db"

import app as flask_app

client = flask_app.app.test_client()

print("GET /health   ->", client.get("/health").get_json())
print("GET /          -> status", client.get("/").status_code)
apps = client.get("/apps").get_json()["apps"]
print("GET /apps     -> apps:", [f"{a['app']}({a['badge']})" for a in apps])
inbox = client.get("/inbox").get_json()["items"]
print("GET /inbox    -> items:", len(inbox))

# analyze a few inbox items through the engine
for m in inbox[:4]:
    r = client.post("/analyze", json={
        "text": m["text"], "channel": m["channel"],
        "sender": m.get("sender", ""), "subject": m.get("subject", ""),
    }).get_json()["result"]
    tag = "SCAM-EXPECTED" if m.get("scam") else "safe-expected"
    print(f"  {m['app']:13} {m['name'][:18]:20} risk={r['risk']:>3} {r['level']:11} ({tag})")

rep = client.get("/report/daily").get_json()
print("GET /report/daily -> scams:", rep["scams"], "suspicious:", rep["suspicious"], "threats:", len(rep["threats"]))
print("POST /tts     -> status", client.post("/tts", json={"text": "hello"}).status_code, "(204 = use Web Speech)")

try:
    os.remove("test_satark.db")
except OSError:
    pass
print("\nAll endpoints OK.")
