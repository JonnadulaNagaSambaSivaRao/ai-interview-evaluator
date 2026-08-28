from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.database import Base


class InterviewAttempt(Base):

    __tablename__ = "interview_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    interview_id = Column(
        Integer,
        ForeignKey(
            "interviews.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="started"
    )

    started_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    submitted_at = Column(
        DateTime,
        nullable=True
    )

    score = Column(
        Integer,
        nullable=True
    )