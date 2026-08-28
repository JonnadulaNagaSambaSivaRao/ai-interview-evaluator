from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from app.database import Base


class Evaluation(Base):

    __tablename__ = "evaluations"

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

    score = Column(
        Integer,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )