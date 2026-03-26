import ssl
import warnings
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


def _build_engine():
    connect_args: dict = {}
    tidb_ssl_ca = settings.tidb_ssl_ca.strip()
    if tidb_ssl_ca:
        ca = tidb_ssl_ca if Path(tidb_ssl_ca).is_file() else None
        if ca is None:
            warnings.warn(
                f"TIDB_SSL_CA '{tidb_ssl_ca}' not found. "
                "Falling back to the system default CA bundle.",
                RuntimeWarning,
                stacklevel=2,
            )
        ssl_ctx = ssl.create_default_context(cafile=ca)
        connect_args["ssl"] = ssl_ctx

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
