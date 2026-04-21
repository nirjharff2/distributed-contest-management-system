"""WebSocket fan-out helpers."""

from . import state
from .database import get_problem_with_tests, get_scoreboard


async def broadcast_to_all(msg: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    for user_id, ws in list(state.clients.items()):
        try:
            await ws.send_json(msg)
        except Exception:
            disconnected.append(user_id)
    for user_id in disconnected:
        state.clients.pop(user_id, None)

    print(f"📤 Broadcasted '{msg.get('type', 'unknown')}' to {len(state.clients)} clients")


async def broadcast_scoreboard():
    await broadcast_to_all({
        "type": "SCOREBOARD",
        "scoreboard": get_scoreboard(),
    })


async def broadcast_contest_state():
    await broadcast_to_all({
        "type": "CONTEST_STATE",
        "active": state.contest_active,
        "start_time": state.contest_start_time.isoformat() if state.contest_start_time else None,
        "end_time": state.contest_end_time.isoformat() if state.contest_end_time else None,
    })


async def broadcast_problem(problem_id: str):
    """Send problem to all connected clients"""
    problem = get_problem_with_tests(problem_id)
    if problem:
        print(f"📤 Broadcasting problem {problem_id} to {len(state.clients)} clients")
        await broadcast_to_all({
            "type": "PROBLEM_AVAILABLE",
            "problem": problem,
        })
    else:
        print(f"⚠️ Cannot broadcast - problem {problem_id} not found")


async def broadcast_announcement(announcement: dict):
    """Send announcement to all connected clients"""
    await broadcast_to_all({
        "type": "ANNOUNCEMENT",
        "announcement": announcement,
    })
