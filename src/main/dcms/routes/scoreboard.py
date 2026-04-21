"""Scoreboard HTTP API."""

from fastapi import APIRouter

from ..database import get_scoreboard

router = APIRouter()


@router.get("/scoreboard")
async def get_scoreboard_api():
    return {"scoreboard": get_scoreboard()}
