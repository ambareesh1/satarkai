"""Tiny .env loader (no external dependency).

Reads a `.env` file from the project root into os.environ if present, so users
can drop OPENROUTER_API_KEY / ELEVENLABS_API_KEY / SMTP_* there. Existing
environment variables always win over the file.
"""

from __future__ import annotations

import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_dotenv(path: str | None = None) -> None:
    path = path or os.path.join(_ROOT, ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass  # never let a malformed .env break startup
