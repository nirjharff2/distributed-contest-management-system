from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..services.api import AdminApi


def contest_state(api: AdminApi) -> Dict[str, Any]:
    return api.contest_state()


def participants(api: AdminApi) -> Tuple[List[tuple], int, int]:
    payload = api.list_participants()
    participants = payload.get("participants", [])
    online_count = int(payload.get("online_count", 0) or 0)

    rows = []
    for p in participants:
        status = "🟢 Online" if p.get("online") else "⚪ Offline"
        rows.append((status, p.get("user_id", ""), (p.get("registered_at") or "")[:19]))

    return rows, len(participants), online_count


def submissions(api: AdminApi, limit: int = 100) -> Tuple[List[dict], List[tuple]]:
    subs = api.list_submissions(limit=limit).get("submissions", [])
    rows = []
    for s in subs:
        rows.append(
            (
                (s.get("timestamp") or "")[:19],
                s.get("user_id", ""),
                s.get("problem_id", ""),
                s.get("language", ""),
                s.get("verdict", ""),
                f"{s.get('passed_tests', 0)}/{s.get('total_tests', 0)}",
            )
        )
    return subs, rows


def problems(api: AdminApi) -> Tuple[List[dict], List[tuple]]:
    problems = api.list_problems().get("problems", [])
    rows = []
    for p in problems:
        rows.append(
            (
                p.get("problem_id", ""),
                p.get("title", ""),
                p.get("difficulty", ""),
                p.get("points", 0),
                p.get("time_limit", 0),
                p.get("test_count", 0),
            )
        )
    return problems, rows


def scoreboard(api: AdminApi) -> Tuple[List[dict], List[tuple], Dict[str, Any]]:
    sb = api.scoreboard().get("scoreboard", [])

    rows = []
    for e in sb:
        probs = e.get("problems", {})
        probs_str = " ".join(
            f"{pid}:{'✅' if v.get('solved') else '—'}({v.get('attempts',0)})" for pid, v in probs.items()
        )
        rows.append(
            (
                e.get("rank", ""),
                e.get("user_id", ""),
                e.get("problems_solved", 0),
                e.get("penalty", 0),
                probs_str,
            )
        )

    derived = {
        "first_user": sb[0].get("user_id", "—") if sb else "—",
        "participants": len(sb),
        "accepted_total": sum(int(x.get("problems_solved", 0) or 0) for x in sb),
        "avg_penalty": int(sum(int(x.get("penalty", 0) or 0) for x in sb) / len(sb)) if sb else 0,
    }
    return sb, rows, derived


def announcements(api: AdminApi) -> List[tuple]:
    anns = api.list_announcements().get("announcements", [])
    rows = []
    for a in anns:
        rows.append(
            (
                a.get("id", ""),
                a.get("priority", ""),
                a.get("title", ""),
                (a.get("content", "") or "")[:120],
                (a.get("created_at") or "")[:19],
            )
        )
    return rows

