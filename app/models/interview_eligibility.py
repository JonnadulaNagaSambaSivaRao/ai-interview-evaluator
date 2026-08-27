from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Float,
    Text,
    ForeignKey
)

from app.database import Base


class InterviewEligibility(Base):
    __tablename__ = "interview_eligibility"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.id"),
        nullable=False,
        unique=True
    )

    eligible = Column(
        Boolean,
        nullable=False,
        default=False
    )

    score = Column(
        Float,
        nullable=True
    )

    reason = Column(
        Text,
        nullable=True
    )