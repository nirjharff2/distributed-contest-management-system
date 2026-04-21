"""Admin-triggered generic and legacy announcement broadcasts."""

import datetime

from fastapi import APIRouter

from .. import state
from ..broadcast import broadcast_announcement, broadcast_to_all
from ..models import AnnouncementCreate, BroadcastMessage

router = APIRouter()


@router.post("/broadcast")
async def generic_broadcast(message: BroadcastMessage):
    """Generic broadcast endpoint for admin to send any message to clients"""
    broadcast_data = {
        "type": message.type,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if message.data:
        broadcast_data["data"] = message.data
    if message.title:
        broadcast_data["title"] = message.title
    if message.content:
        broadcast_data["content"] = message.content
    if message.priority:
        broadcast_data["priority"] = message.priority

    await broadcast_to_all(broadcast_data)

    return {
        "status": "Broadcast sent",
        "type": message.type,
        "clients": len(state.clients),
    }


@router.post("/broadcast_announcement")
async def broadcast_announcement_endpoint(data: AnnouncementCreate):
    """Broadcast an announcement without saving to database"""
    announcement = {
        "title": data.title,
        "content": data.content,
        "priority": data.priority,
        "created_at": datetime.datetime.now().isoformat(),
    }

    await broadcast_announcement(announcement)

    return {
        "status": "Announcement broadcasted",
        "clients": len(state.clients),
    }


@router.get("/broadcast_announcement")
async def broadcast_announcement_get(content: str, priority: str = "normal"):
    """Broadcast an announcement via GET request (for simpler integration)"""
    announcement = {
        "title": "📢 Announcement",
        "content": content,
        "priority": priority,
        "created_at": datetime.datetime.now().isoformat(),
    }

    await broadcast_announcement(announcement)

    return {
        "status": "Announcement broadcasted",
        "clients": len(state.clients),
    }
