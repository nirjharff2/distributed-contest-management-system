from __future__ import annotations

from typing import Any, Dict

from ..services.api import AdminApi


def get_problem(api: AdminApi, problem_id: str) -> Dict[str, Any]:
    return api.get_problem(problem_id).get("problem", {})


def create_problem(api: AdminApi, payload: Dict[str, Any]) -> None:
    api.create_problem(payload)


def delete_problem(api: AdminApi, problem_id: str) -> None:
    api.delete_problem(problem_id)

