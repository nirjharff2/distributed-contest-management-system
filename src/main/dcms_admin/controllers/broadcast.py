from __future__ import annotations

from ..services.api import AdminApi


def send_problem(api: AdminApi, problem_id: str) -> None:
    api.send_problem(problem_id)


def send_all_problems(api: AdminApi) -> int:
    problems = api.list_problems().get("problems", [])
    sent = 0
    for p in problems:
        pid = p.get("problem_id")
        if not pid:
            continue
        try:
            api.send_problem(pid)
            sent += 1
        except Exception:
            # best-effort broadcast; keep going
            pass
    return sent

