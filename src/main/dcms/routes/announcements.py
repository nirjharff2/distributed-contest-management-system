"""Announcements CRUD and broadcast-on-create."""

import datetime

from fastapi import APIRouter, HTTPException

from ..broadcast import broadcast_announcement, broadcast_to_all
from ..database import get_db
from ..models import AnnouncementCreate

router = APIRouter()


@router.get("/announcements")
async def list_announcements():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM announcements ORDER BY created_at DESC")
    announcements = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"announcements": announcements}


@router.get("/announcements/{announcement_id}")
async def get_announcement(announcement_id: int):
    """Get a specific announcement"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM announcements WHERE id = ?", (announcement_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"announcement": dict(row)}


@router.post("/announcements")
async def create_announcement(data: AnnouncementCreate):
    conn = get_db()
    c = conn.cursor()
    created_at = datetime.datetime.now().isoformat()
    c.execute("""
        INSERT INTO announcements (title, content, priority, created_at)
        VALUES (?, ?, ?, ?)
    """, (data.title, data.content, data.priority, created_at))
    ann_id = c.lastrowid
    conn.commit()
    conn.close()

    announcement = {
        "id": ann_id,
        "title": data.title,
        "content": data.content,
        "priority": data.priority,
        "created_at": created_at,
    }

    await broadcast_announcement(announcement)

    return {"status": "Announcement created", "id": ann_id, "announcement": announcement}


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(announcement_id: int):
    """Delete an announcement"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM announcements WHERE id = ?", (announcement_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Announcement not found")

    c.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    conn.commit()
    conn.close()

    print(f"🗑️ Deleted announcement: {announcement_id}")

    await broadcast_to_all({
        "type": "ANNOUNCEMENT_DELETED",
        "id": announcement_id,
    })

    return {"status": "Announcement deleted", "id": announcement_id}
