from __future__ import annotations

from typing import Any, Dict

from ..services.api import AdminApi


def create_announcement(api: AdminApi, payload: Dict[str, Any]) -> None:
    api.create_announcement(payload)


def delete_announcement(api: AdminApi, announcement_id: int | str) -> None:
    api.delete_announcement(announcement_id)

