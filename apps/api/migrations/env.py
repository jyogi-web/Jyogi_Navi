"""Alembic 環境設定 (非同期対応)."""

import asyncio
import ssl as ssl_mod
import sys

# Windows の ProactorEventLoop は SSL + aiomysql と非互換のため SelectorEventLoop を使用
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import URL, Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# apps/api をモジュール検索パスに追加
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """環境変数から接続URLを構築する。alembic.ini の値より優先。

    必須フィールド (tidb_user, tidb_host, tidb_database) がすべて設定されている
    場合は環境変数から URL を生成する。いずれかが空の場合は alembic.ini の
    sqlalchemy.url にフォールバックする。
    """
    from config import settings

    if settings.tidb_user and settings.tidb_host and settings.tidb_database:
        url = URL.create(
            drivername="mysql+aiomysql",
            username=settings.tidb_user,
            password=settings.tidb_password.get_secret_value(),
            host=settings.tidb_host,
            port=settings.tidb_port,
            database=settings.tidb_database,
        )
        return url.render_as_string(hide_password=False)

    fallback = config.get_main_option("sqlalchemy.url")
    if fallback:
        return fallback

    raise RuntimeError(
        "DB接続情報が不足しています。環境変数 (TIDB_USER, TIDB_HOST, TIDB_DATABASE) "
        "を設定するか、alembic.ini の sqlalchemy.url を指定してください。"
    )


def _get_connect_args() -> dict:
    """SSL 接続引数を構築する。db/session.py と同じパターン。"""
    from config import settings

    if settings.tidb_ssl_ca:
        ssl_ctx = ssl_mod.create_default_context(cafile=settings.tidb_ssl_ca)
        return {"ssl": ssl_ctx}
    return {}


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
        connect_args=_get_connect_args(),
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
