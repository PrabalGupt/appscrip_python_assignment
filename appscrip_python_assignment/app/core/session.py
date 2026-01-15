from typing import Dict, Any
import time

# key: username (or session id), value: simple stats
_session_store: Dict[str, Dict[str, Any]] = {}


def touch_session(user_id: str) -> Dict[str, Any]:
    """Update or create a simple in-memory session record."""
    now = time.time()
    session = _session_store.get(user_id, {"calls": 0, "created_at": now})
    session["calls"] = session.get("calls", 0) + 1
    session["last_call_at"] = now
    _session_store[user_id] = session
    return session


# def get_session(user_id: str) -> Dict[str, Any] | None:
#     return _session_store.get(user_id)
