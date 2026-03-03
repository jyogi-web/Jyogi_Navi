from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import settings

_engine: Engine | None = None

# TODO: ログ保存の実装(P1)

# TiDBへの接続
def _get_engine() -> Engine:
    global _engine
    # シングルトンパターンでエンジンを生成
    if _engine is None:
        connect_args: dict = {}
        if settings.tidb_ssl_ca:
            connect_args["ssl"] = {"ca": settings.tidb_ssl_ca}

        url = (
            f"mysql+pymysql://{settings.tidb_user}:{settings.tidb_password}"
            f"@{settings.tidb_host}:{settings.tidb_port}/{settings.tidb_database}"
        )
        _engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    return _engine

def ping() -> bool:
    """DB疎通確認。ヘルスチェックに使用。"""
    try:
        with _get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
