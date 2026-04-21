from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class AdminApi:
    """Pure HTTP client for the DCMS server.

    This module must not import Tkinter.
    """

    base_url: str
    timeout_s: float = 8.0

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.pop("timeout", self.timeout_s)
        r = requests.request(method, self._url(path), timeout=timeout, **kwargs)
        r.raise_for_status()
        if not r.content:
            return {}
        return r.json()

    # ---- contest ----
    def contest_state(self) -> Dict[str, Any]:
        return self._request("GET", "/contest_state", timeout=5)

    def start_contest(self, minutes: int) -> Dict[str, Any]:
        return self._request("GET", f"/start_contest/{minutes}")

    def end_contest(self) -> Dict[str, Any]:
        return self._request("GET", "/end_contest")

    # ---- broadcast ----
    def send_problem(self, problem_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/send_problem/{problem_id}")

    # ---- problems ----
    def list_problems(self) -> Dict[str, Any]:
        return self._request("GET", "/problems")

    def get_problem(self, problem_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/problems/{problem_id}")

    def create_problem(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/problems", json=payload)

    def delete_problem(self, problem_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/problems/{problem_id}")

    # ---- participants ----
    def list_participants(self) -> Dict[str, Any]:
        return self._request("GET", "/participants")

    # ---- submissions ----
    def list_submissions(self, limit: int = 100) -> Dict[str, Any]:
        return self._request("GET", "/submissions", params={"limit": limit})

    # ---- scoreboard ----
    def scoreboard(self) -> Dict[str, Any]:
        return self._request("GET", "/scoreboard")

    # ---- announcements ----
    def list_announcements(self) -> Dict[str, Any]:
        return self._request("GET", "/announcements")

    def create_announcement(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/announcements", json=payload)

    def delete_announcement(self, announcement_id: int | str) -> Dict[str, Any]:
        return self._request("DELETE", f"/announcements/{announcement_id}")

