"""Attachment model for SimpleCRM."""

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Attachment(Base):
    """Attachment model representing files attached to activities."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    activity = relationship("Activity", back_populates="attachments")
