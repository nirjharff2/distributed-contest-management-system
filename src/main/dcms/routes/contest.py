"""Contest control and root metadata."""

import asyncio
import datetime

from fastapi import APIRouter

from .. import state
from ..broadcast import (
    broadcast_contest_state,
    broadcast_problem,
    broadcast_to_all,
)
from ..database import get_db, get_all_problems
from ..lifecycle import contest_timer

router = APIRouter()


@router.get("/")
async def root():
    return {
        "name": "DCMS Server",
        "version": "2.1",
        "contest_active": state.contest_active,
        "connected_clients": len(state.clients),
    }


@router.get("/contest_state")
async def get_contest_state():
    return {
        "active": state.contest_active,
        "start_time": state.contest_start_time.isoformat() if state.contest_start_time else None,
        "end_time": state.contest_end_time.isoformat() if state.contest_end_time else None,
        "penalty_time": state.penalty_time,
        "connected_clients": len(state.clients),
    }


@router.get("/start_contest/{minutes}")
async def start_contest(minutes: int):
    state.contest_active = True
    state.contest_start_time = datetime.datetime.now()
    state.contest_end_time = state.contest_start_time + datetime.timedelta(minutes=minutes)

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE contest_state
        SET active = 1, start_time = ?, end_time = ?
        WHERE id = 1
    """, (state.contest_start_time.isoformat(), state.contest_end_time.isoformat()))
    conn.commit()
    conn.close()

    asyncio.create_task(contest_timer())
    await broadcast_contest_state()

    problems = get_all_problems()
    for p in problems:
        await broadcast_problem(p["problem_id"])

    return {
        "status": "Contest started",
        "duration_minutes": minutes,
        "end_time": state.contest_end_time.isoformat(),
        "problems_sent": len(problems),
    }


@router.get("/end_contest")
async def end_contest():
    state.contest_active = False

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE contest_state SET active = 0 WHERE id = 1")
    conn.commit()
    conn.close()

    await broadcast_to_all({"type": "CONTEST_END"})
    await broadcast_contest_state()

    return {"status": "Contest ended"}
