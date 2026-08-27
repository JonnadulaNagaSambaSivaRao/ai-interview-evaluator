from sqlalchemy import Column, Integer, String, Float, Text

from app.database import Base


class EvaluationCriteria(Base):
    __tablename__ = "evaluation_criteria"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    weight = Column(
        Float,
        default=1.0
    )