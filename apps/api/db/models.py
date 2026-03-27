"""SQLAlchemy ORM モデル定義 (TiDB Serverless)."""

import enum
import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
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
        server_default=text("CURRENT_TIMESTAMP"),
    )

    usage_logs: Mapped[list["UsageLog"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
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
        server_default=text("CURRENT_TIMESTAMP"),
    )

    session: Mapped["Session"] = relationship(back_populates="usage_logs")


class Feedback(Base):
    """チャット回答へのフィードバック。"""

    __tablename__ = "feedbacks"
    __table_args__ = (Index("ix_feedbacks_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id"),
    )
    rating: Mapped[Literal["good", "bad"]] = mapped_column(
        Enum("good", "bad"), nullable=False
    )
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    session: Mapped["Session"] = relationship(back_populates="feedbacks")


class UserRole(enum.StrEnum):
    """管理ユーザーのロール。"""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class User(Base):
    """管理画面ユーザー (Discord OAuth で認証)。"""

    __tablename__ = "users"
    __table_args__ = (Index("ix_users_discord_user_id", "discord_user_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    discord_user_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.MEMBER,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class FaqEmbedding(Base):
    """FAQベクトルデータ(RAG用)。"""

    __tablename__ = "faq_embeddings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )
