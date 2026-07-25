from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Generic Uuid: на SQLite хранится как CHAR(32), на Postgres — как native UUID.
UUID = Uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="open")
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reply_to_tg_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_type: Mapped[str] = mapped_column(Text, nullable=False, default="text")
    model_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    telegram_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    mime_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_by: Mapped[str] = mapped_column(Text, nullable=False, default="system")


class ProcessedUpdate(Base):
    __tablename__ = "processed_updates"

    update_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class LLMUsageLog(Base):
    __tablename__ = "llm_usage_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)