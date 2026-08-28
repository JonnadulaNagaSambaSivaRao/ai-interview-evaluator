from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint
)

from app.database import Base


class InterviewEligibility(Base):

    __tablename__ = "interview_eligibility"

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
        default="assigned"
    )

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "interview_id",
            name="unique_candidate_interview"
        ),
    )