import re
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

class Base(DeclarativeBase):
    pass


def normalize_database_url(url: str) -> tuple[str, dict]:
    """Make Supabase/PostgreSQL URLs compatible with asyncpg."""
    connect_args: dict = {}
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    if "+asyncpg" in url and "sslmode=" in url:
        ssl_required = re.search(r"(?:[?&])sslmode=require(?:&|$)", url) is not None
        url = re.sub(r"([?&])sslmode=[^&]*&?", r"\1", url).rstrip("?&")
        if ssl_required:
            connect_args["ssl"] = "require"
    return url, connect_args


database_url, engine_args = normalize_database_url(settings.DATABASE_URL)
if database_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, echo=False, future=True, **engine_args)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
