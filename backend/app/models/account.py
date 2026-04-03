from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    platform = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    credentials = Column(JSON, nullable=True)
    proxy = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="active")
    last_used_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="accounts")
    tasks = relationship("Task", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, platform={self.platform}, label={self.label})>"
