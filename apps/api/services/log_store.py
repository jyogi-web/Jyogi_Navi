from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Feedback, Session, UsageLog
from schemas.feedback import FeedbackCreate
from schemas.session import SessionCreate, UsageLogCreate


async def ping(session: AsyncSession) -> bool:
    """DB疎通確認。ヘルスチェックに使用。"""
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def create_session(db: AsyncSession, data: SessionCreate) -> Session:
    """新しいセッションを作成して返す。"""
    record = Session(is_guest=data.is_guest, consented=False)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def save_usage_log(db: AsyncSession, data: UsageLogCreate) -> UsageLog:
    """トークン消費ログを保存して返す。"""
    record = UsageLog(
        session_id=data.session_id,
        tokens=data.tokens,
        category=data.category,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def save_feedback(db: AsyncSession, data: FeedbackCreate) -> Feedback:
    """フィードバックを保存して返す。"""
    record = Feedback(
        session_id=data.session_id,
        message_id=data.message_id,
        rating=data.rating,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
