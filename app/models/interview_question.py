from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    ForeignKey
)

from app.database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

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

    question_text = Column(
        Text,
        nullable=False
    )

    question_type = Column(
        String(50),
        default="technical"
    )

    order_no = Column(
        Integer,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=True
    )

    score = Column(
        Float,
        nullable=True
    )