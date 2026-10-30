"""Async SQLAlchemy engine, session factory, and base model."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Engine ────────────────────────────────────────────────────────────────
# For SQLite we must disable check_same_thread; for PostgreSQL it is a no-op.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# ── Session factory ───────────────────────────────────────────────────────
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative base ─────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ── FastAPI dependency ────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, ensuring it is closed after use."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create every table that inherits from Base (used on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
