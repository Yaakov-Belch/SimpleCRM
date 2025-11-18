"""Activity model for SimpleCRM."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Activity(Base):
    """Activity model representing interactions with contacts."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type = Column(
        Enum("Call", "Meeting", "Email", "Note", name="activity_type_enum"),
        nullable=False,
        index=True
    )
    subject = Column(String(255), nullable=True, default="")
    notes = Column(Text, nullable=True)
    activity_date = Column(DateTime, nullable=False, index=True)
    pipeline_stage = Column(
        String(50),
        nullable=False,
        default="Lead",
        index=True
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    contact = relationship("Contact", back_populates="activities")
    attachments = relationship(
        "Attachment",
        back_populates="activity",
        cascade="all, delete-orphan"
    )
