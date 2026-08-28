from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from app.database import Base


class FinalReport(Base):

    __tablename__ = "final_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    attempt_id = Column(
        Integer,
        ForeignKey(
            "interview_attempts.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    overall_score = Column(
        Integer,
        nullable=True
    )

    recommendation = Column(
        Text,
        nullable=True
    )

    summary = Column(
        Text,
        nullable=True
    )