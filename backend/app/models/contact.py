"""Contact model for SimpleCRM."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Contact(Base):
    """Contact model representing business contacts."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True, index=True)
    job_title = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    notes = Column(Text(5000), nullable=True)
    pipeline_stage = Column(String(50), nullable=False, default="Lead", index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="contacts")
    activities = relationship(
        "Activity",
        back_populates="contact",
        cascade="all, delete-orphan"
    )

    @property
    def current_pipeline_stage(self) -> str:
        """
        Compute current pipeline stage from most recent activity.

        Returns:
            Pipeline stage from the most recent activity, or "Lead" if no activities exist.
        """
        if not self.activities:
            return "Lead"

        # Get the most recent activity by activity_date
        latest_activity = max(self.activities, key=lambda a: a.activity_date)
        return latest_activity.pipeline_stage
