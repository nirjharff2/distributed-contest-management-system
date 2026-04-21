"""Participant listing."""

from fastapi import APIRouter

from .. import state
from ..database import get_db

router = APIRouter()


@router.get("/participants")
async def list_participants():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM participants ORDER BY registered_at DESC")
    participants = [dict(row) for row in c.fetchall()]
    conn.close()

    for p in participants:
        p["online"] = p["user_id"] in state.clients

    return {"participants": participants, "online_count": len(state.clients)}
