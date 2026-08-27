from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    ForeignKey,
    DateTime
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class FinalReport(Base):
    __tablename__ = "final_reports"

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

    overall_score = Column(
        Float,
        nullable=True
    )

    recommendation = Column(
        String(50),
        nullable=True
    )

    summary = Column(
        Text,
        nullable=True
    )

    strengths = Column(
        JSONB,
        default=list
    )

    weaknesses = Column(
        JSONB,
        default=list
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )