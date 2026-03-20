"""Alembic 環境設定 (非同期対応)."""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# apps/api をモジュール検索パスに追加
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """環境変数から接続URLを構築する。alembic.ini の値より優先。"""
    from config import settings

    return (
        f"mysql+aiomysql://{settings.tidb_user}"
        f":{settings.tidb_password.get_secret_value()}"
        f"@{settings.tidb_host}:{settings.tidb_port}"
        f"/{settings.tidb_database}"
    )


def run_migrations_offline() -> None:
    """オフラインモード: SQL文を生成のみ。"""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """接続を使ってマイグレーションを実行する。"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """非同期エンジンでマイグレーションを実行する。"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """オンラインモード: 非同期エンジン経由で実行。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
