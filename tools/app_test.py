"""End-to-end test of the Flask API using the in-process test client."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a throwaway DB so the test doesn't pollute real history.
os.environ["SATARK_DB"] = "test_satark.db"

import app as flask_app

client = flask_app.app.test_client()

print("GET /health ->", client.get("/health").get_json())
print("GET /samples -> count:", len(client.get("/samples").get_json()["samples"]))

payload = {
    "channel": "sms",
    "sender": "+918877665544",
    "text": "Your SBI account will be BLOCKED today, complete KYC now: http://sbi-kyc-verify.xyz/login",
}
r = client.post("/analyze", json=payload).get_json()
res = r["result"]
print(f"POST /analyze -> risk={res['risk']} level={res['level']} category={res['category_label']}")
print("  reasons:", res["reasons"][:3])

print("GET /stats ->", client.get("/stats").get_json())
print("GET /history -> items:", len(client.get("/history").get_json()["items"]))
print("GET / (dashboard) -> status", client.get("/").status_code)

# cleanup
try:
    os.remove("test_satark.db")
except OSError:
    pass
print("\nAll endpoints OK.")
