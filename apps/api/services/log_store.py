import json
import logging
from datetime import UTC, datetime, time

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UsageLog

logger = logging.getLogger(__name__)


def _emit_structured_log(
    level: str,
    action: str,
    trace_id: str,
    metadata: dict,
) -> None:
    """docs/08_logging.md 準拠の構造化ログを出力する。"""
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": level,
        "service": "api",
        "trace_id": trace_id,
        "action": action,
        "metadata": metadata,
    }
    normalized = level.lower().replace("warn", "warning")
    log_fn = getattr(logger, normalized, logger.info)
    log_fn(json.dumps(record, ensure_ascii=False))


async def ping(session: AsyncSession) -> bool:
    """DB疎通確認。ヘルスチェックに使用。"""
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def save_usage_log(
    session: AsyncSession,
    session_id: str,
    tokens: int,
    trace_id: str,
    category: str | None = None,
) -> UsageLog:
    """usage_logs にトークン消費を保存する。メッセージ本文は保存しない。"""
    log = UsageLog(
        session_id=session_id,
        tokens=tokens,
        category=category or "",
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)

    _emit_structured_log(
        level="INFO",
        action="chat.request",
        trace_id=trace_id,
        metadata={"session_id": session_id, "tokens": tokens},
    )
    return log


async def get_daily_token_usage(session: AsyncSession, session_id: str) -> int:
    """当日の session_id に紐づくトークン消費合計を返す。レート制御に使用。"""
    utc_today_start = datetime.combine(datetime.now(UTC).date(), time.min)
    result = await session.execute(
        select(func.coalesce(func.sum(UsageLog.tokens), 0)).where(
            UsageLog.session_id == session_id,
            UsageLog.created_at >= utc_today_start,
        )
    )
    return int(result.scalar())
