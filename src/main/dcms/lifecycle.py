"""Startup hooks and background contest timer."""

import asyncio
import datetime

from fastapi import FastAPI

from . import state
from .broadcast import broadcast_contest_state, broadcast_to_all
from .config import DB_PATH
from .database import get_db


async def contest_timer():
    while state.contest_active and state.contest_end_time:
        if datetime.datetime.now() >= state.contest_end_time:
            state.contest_active = False

            conn = get_db()
            c = conn.cursor()
            c.execute("UPDATE contest_state SET active = 0 WHERE id = 1")
            conn.commit()
            conn.close()

            await broadcast_to_all({"type": "CONTEST_END"})
            await broadcast_contest_state()

            print("⏰ Contest ended automatically")
            break

        await asyncio.sleep(1)


def register_lifecycle(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        print("🚀 DCMS Server v2.1 starting...")
        print(f"📊 Database: {DB_PATH}")

        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM contest_state WHERE id = 1")
            row = c.fetchone()

            if row:
                state.contest_active = bool(row["active"])
                if row["start_time"]:
                    state.contest_start_time = datetime.datetime.fromisoformat(row["start_time"])
                if row["end_time"]:
                    state.contest_end_time = datetime.datetime.fromisoformat(row["end_time"])
                if row["penalty_time"]:
                    state.penalty_time = row["penalty_time"]

                if state.contest_active and state.contest_end_time:
                    if datetime.datetime.now() < state.contest_end_time:
                        asyncio.create_task(contest_timer())
                    else:
                        state.contest_active = False

            c.execute("SELECT COUNT(*) FROM problems")
            prob_count = c.fetchone()[0]
            print(f"📚 Problems in database: {prob_count}")

            c.execute("SELECT COUNT(*) FROM announcements")
            ann_count = c.fetchone()[0]
            print(f"📢 Announcements in database: {ann_count}")

            conn.close()
        except Exception as e:
            print(f"⚠️ Startup error: {e}")

        print(f"✅ Server ready! Contest active: {state.contest_active}")
        print("📡 Endpoints available:")
        print("   - DELETE /problems/{problem_id}")
        print("   - GET /problems/{problem_id}/testcases")
        print("   - DELETE /announcements/{announcement_id}")
        print("   - POST /broadcast")
