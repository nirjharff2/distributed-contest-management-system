"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lifecycle import register_lifecycle
from .routes import (
    announcements,
    broadcast_api,
    contest,
    participants,
    problems,
    scoreboard,
    submissions,
    testcases,
)
from .ws import router as ws_router


def create_app() -> FastAPI:
    application = FastAPI(title="DCMS Server", version="2.1")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(contest.router, tags=["contest"])
    application.include_router(problems.router, tags=["problems"])
    application.include_router(testcases.router, tags=["testcases"])
    application.include_router(scoreboard.router, tags=["scoreboard"])
    application.include_router(participants.router, tags=["participants"])
    application.include_router(submissions.router, tags=["submissions"])
    application.include_router(announcements.router, tags=["announcements"])
    application.include_router(broadcast_api.router, tags=["broadcast"])
    application.include_router(ws_router, tags=["websocket"])

    register_lifecycle(application)
    return application


app = create_app()
