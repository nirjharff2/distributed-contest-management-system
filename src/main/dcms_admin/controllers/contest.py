from __future__ import annotations

from ..services.api import AdminApi


def start_contest(api: AdminApi, minutes: int) -> None:
    api.start_contest(minutes)


def end_contest(api: AdminApi) -> None:
    api.end_contest()

