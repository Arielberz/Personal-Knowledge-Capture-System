from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from app.database import Base
except ModuleNotFoundError:
    from database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    importance_score: Mapped[float] = mapped_column(Float, default=5.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    captures: Mapped[list["Capture"]] = relationship(back_populates="topic")
    questions: Mapped[list["OpenQuestion"]] = relationship(back_populates="topic")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="topic")


class Capture(Base):
    __tablename__ = "captures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), default="image")
    file_path: Mapped[str] = mapped_column(String(300))
    original_filename: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)
    main_topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    knowledge_score: Mapped[int] = mapped_column(Integer, default=5)
    confidence: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="pending_review")

    topic: Mapped["Topic"] = relationship(back_populates="captures")
    questions: Mapped[list["OpenQuestion"]] = relationship(back_populates="capture")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="capture")


class OpenQuestion(Base):
    __tablename__ = "open_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    capture_id: Mapped[int | None] = mapped_column(ForeignKey("captures.id"), nullable=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    importance_score: Mapped[float] = mapped_column(Float, default=5.0)
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    capture: Mapped["Capture"] = relationship(back_populates="questions")
    topic: Mapped["Topic"] = relationship(back_populates="questions")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    capture_id: Mapped[int | None] = mapped_column(ForeignKey("captures.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    due_date: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reminder_type: Mapped[str] = mapped_column(String(40), default="review_question")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    topic: Mapped["Topic"] = relationship(back_populates="reminders")
    capture: Mapped["Capture"] = relationship(back_populates="reminders")


class AllowedSource(Base):
    __tablename__ = "allowed_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    path_prefix: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="running")
    files_found: Mapped[int] = mapped_column(Integer, default=0)
    files_processed: Mapped[int] = mapped_column(Integer, default=0)
    files_failed: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_path: Mapped[str] = mapped_column(String(700), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(250))
    file_type: Mapped[str] = mapped_column(String(60))
    file_hash: Mapped[str] = mapped_column(String(128), index=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(40), default="pending_review")


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_file_id: Mapped[int] = mapped_column(ForeignKey("source_files.id"), index=True)
    capture_id: Mapped[int | None] = mapped_column(ForeignKey("captures.id"), nullable=True)
    suggested_topic: Mapped[str] = mapped_column(String(180))
    suggested_status: Mapped[str] = mapped_column(String(40), default="pending_review")
    knowledge_score: Mapped[int] = mapped_column(Integer, default=5)
    confidence: Mapped[str] = mapped_column(String(20), default="medium")
    reason_for_topic: Mapped[str] = mapped_column(Text)
    reason_for_score: Mapped[str] = mapped_column(Text)
    what_to_learn_from_this: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_questions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_by_user: Mapped[bool] = mapped_column(default=False)
    user_correction: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("agent_runs.id"), nullable=True, index=True)
    file_path: Mapped[str | None] = mapped_column(String(700), nullable=True)
    step: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
