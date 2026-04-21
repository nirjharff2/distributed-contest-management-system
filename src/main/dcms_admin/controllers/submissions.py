from __future__ import annotations

from typing import Any, Dict, List, Optional


def find_submission_record(
    submissions: List[Dict[str, Any]],
    timestamp_prefix: str,
    user_id: str,
    problem_id: str,
) -> Optional[Dict[str, Any]]:
    for s in submissions:
        if (s.get("timestamp") or "")[:19] == timestamp_prefix and s.get("user_id") == user_id and s.get("problem_id") == problem_id:
            return s
    return None

