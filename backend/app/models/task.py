from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    task_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=True)
    payload = Column(JSON, nullable=True)
    schedule_cron = Column(String(100), nullable=True)
    priority = Column(Integer, default=5)
    status = Column(String(20), default="pending")
    celery_task_id = Column(String(255), nullable=True)
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="tasks")
    account = relationship("Account", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status})>"
