"""Submission history API."""

from fastapi import APIRouter

from ..database import get_db

router = APIRouter()


@router.get("/submissions")
async def list_submissions(limit: int = 100):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY timestamp DESC LIMIT ?", (limit,))
    submissions = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"submissions": submissions}


@router.get("/submissions/{user_id}")
async def get_user_submissions(user_id: str, limit: int = 50):
    """Get submissions for a specific user"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM submissions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    submissions = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"submissions": submissions, "user_id": user_id}
