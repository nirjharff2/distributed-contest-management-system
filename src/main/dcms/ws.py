"""WebSocket endpoint for contest clients."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from . import state
from .broadcast import broadcast_scoreboard
from .database import (
    add_participant,
    get_db,
    get_problem_with_tests,
    get_scoreboard,
    log_submission,
)

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str):
    await ws.accept()
    state.clients[user_id] = ws
    print(f"✅ Client connected: {user_id}")

    add_participant(user_id)

    try:
        await ws.send_json({
            "type": "CONNECTED",
            "user_id": user_id,
            "contest_active": state.contest_active,
            "end_time": state.contest_end_time.isoformat() if state.contest_end_time else None,
        })

        await ws.send_json({
            "type": "SCOREBOARD",
            "scoreboard": get_scoreboard(),
        })

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 20")
        announcements = [dict(row) for row in c.fetchall()]
        conn.close()

        if announcements:
            await ws.send_json({
                "type": "ANNOUNCEMENTS",
                "announcements": announcements,
            })
    except Exception as e:
        print(f"Error sending initial state: {e}")

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            print(f"📨 Received from {user_id}: {msg_type}")

            if msg_type == "GET_PROBLEM":
                problem_id = data.get("problem_id")
                print(f"   Looking for problem: {problem_id}")

                problem = get_problem_with_tests(problem_id)

                if problem:
                    print(f"   Found problem: {problem['title']}, {len(problem.get('test_cases', []))} test cases")
                    await ws.send_json({
                        "type": "PROBLEM_DATA",
                        "problem": problem,
                    })
                else:
                    print(f"   Problem NOT found: {problem_id}")
                    await ws.send_json({
                        "type": "ERROR",
                        "message": f"Problem '{problem_id}' not found in database",
                    })

            elif msg_type == "SUBMISSION":
                if not state.contest_active:
                    await ws.send_json({
                        "type": "ERROR",
                        "message": "Contest is not active",
                    })
                    continue

                problem_id = data.get("problem_id")
                language = data.get("language", "python")
                verdict = data.get("verdict", "Wrong Answer")
                passed_tests = data.get("passed_tests", 0)
                total_tests = data.get("total_tests", 0)
                execution_time = data.get("execution_time", 0.0)

                log_submission(
                    user_id,
                    problem_id,
                    language,
                    verdict,
                    passed_tests,
                    total_tests,
                    execution_time,
                )

                await ws.send_json({
                    "type": "SUBMISSION_CONFIRMED",
                    "problem_id": problem_id,
                    "verdict": verdict,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                })

                await broadcast_scoreboard()

            elif msg_type == "GET_SUBMISSIONS":
                conn = get_db()
                c = conn.cursor()
                c.execute("""
                    SELECT submission_id, problem_id, language, verdict,
                           passed_tests, total_tests, execution_time, timestamp
                    FROM submissions WHERE user_id = ?
                    ORDER BY timestamp DESC LIMIT 50
                """, (user_id,))
                submissions = [dict(row) for row in c.fetchall()]
                conn.close()

                await ws.send_json({
                    "type": "SUBMISSIONS_LIST",
                    "submissions": submissions,
                })

            elif msg_type == "PING":
                await ws.send_json({"type": "PONG"})

    except WebSocketDisconnect:
        print(f"❌ Client disconnected: {user_id}")
        state.clients.pop(user_id, None)
    except Exception as e:
        print(f"❌ WebSocket error for {user_id}: {e}")
        state.clients.pop(user_id, None)
