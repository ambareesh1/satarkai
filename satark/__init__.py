"""SatarkAI - multi-channel scam detection engine."""

from .message import Message, Detection, CHANNELS
from .engine import ScamEngine

__all__ = ["Message", "Detection", "CHANNELS", "ScamEngine"]

__version__ = "1.0.0"
