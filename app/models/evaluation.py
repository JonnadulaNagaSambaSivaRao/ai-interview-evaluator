from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("interview_questions.id"),
        nullable=True
    )

    criteria_scores = Column(
        JSONB,
        default=dict
    )

    overall_score = Column(
        Float,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )