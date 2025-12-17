import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.settings import settings


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine_url() -> str:
    return settings.resolved_database_url


def init_async_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None:
        _engine = create_async_engine(get_engine_url(), echo=False, future=True)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _sessionmaker is None:
        init_async_engine()
    assert _sessionmaker is not None
    async with _sessionmaker() as session:
        yield session


async def create_db_and_tables() -> None:
    engine = init_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def init_async_engine_sync():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, init_async_engine)
