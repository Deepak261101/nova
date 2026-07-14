"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers import auth, conversations, health, memory, oauth, users, voice
from app.api.ws import voice as voice_ws
from app.core.config import Settings, get_settings
from app.core.container import Container
from app.core.exceptions import NovaError
from app.core.logging import configure_logging, get_logger

log = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(debug=settings.debug)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = Container(settings)
        app.state.container = container
        await container.startup()
        log.info("nova_startup", env=settings.env, llm=settings.llm_provider)
        try:
            yield
        finally:
            await container.shutdown()
            log.info("nova_shutdown")

    app = FastAPI(
        title="Nova API",
        version="0.1.0",
        description="Production-grade AI voice assistant backend.",
        lifespan=lifespan,
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NovaError)
    async def _nova_error_handler(_: Request, exc: NovaError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    for router in (
        health.router,
        auth.router,
        oauth.router,
        users.router,
        conversations.router,
        memory.router,
        voice.router,
    ):
        app.include_router(router)
    app.include_router(voice_ws.router)

    @app.get("/", tags=["health"])
    async def root() -> dict[str, str]:
        return {"name": "Nova API", "docs": "/docs", "health": "/health"}

    return app


app = create_app()
