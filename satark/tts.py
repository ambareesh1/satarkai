"""Optional ElevenLabs text-to-speech for the call simulator.

If ELEVENLABS_API_KEY is set, `synthesize()` returns MP3 bytes for realistic
voices. Otherwise the frontend falls back to the browser's free Web Speech API.
"""

from __future__ import annotations

import os
from typing import Optional

_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel"
_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}"


def configured() -> bool:
    if not os.environ.get("ELEVENLABS_API_KEY"):
        return False
    try:
        import requests  # noqa: F401
        return True
    except Exception:
        return False


def synthesize(text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
    if not configured():
        return None
    try:
        import requests
    except Exception:
        return None

    voice = voice_id or _VOICE
    resp = requests.post(
        _URL.format(voice=voice),
        headers={
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text[:2500],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.7},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
