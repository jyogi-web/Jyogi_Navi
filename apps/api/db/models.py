"""SQLAlchemy ORM モデル定義 (TiDB Serverless)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """全モデルの基底クラス。"""


class Session(Base):
    """新入生セッション。"""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    is_guest: Mapped[bool] = mapped_column(default=True)
    consented: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    usage_logs: Mapped[list["UsageLog"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class UsageLog(Base):
    """トークン消費ログ。"""

    __tablename__ = "usage_logs"
    __table_args__ = (
        Index("ix_usage_logs_session_id", "session_id"),
        Index("ix_usage_logs_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id"),
    )
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    session: Mapped["Session"] = relationship(back_populates="usage_logs")
