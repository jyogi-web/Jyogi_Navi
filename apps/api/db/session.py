import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


def _build_engine():
    if settings.tidb_ssl_ca:
        ssl_ctx = ssl.create_default_context(cafile=settings.tidb_ssl_ca)
    else:
        ssl_ctx = ssl.create_default_context()
    connect_args: dict = {"ssl": ssl_ctx}

    url = URL.create(
        drivername="mysql+aiomysql",
        username=settings.tidb_user,
        password=settings.tidb_password.get_secret_value(),
        host=settings.tidb_host,
        port=settings.tidb_port,
        database=settings.tidb_database,
    )
    return create_async_engine(
        url, connect_args=connect_args, pool_pre_ping=True, pool_recycle=3600
    )


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI Depends 用。リクエストスコープでセッションを提供し自動クローズ。"""
    async with AsyncSessionLocal() as session:
        yield session
