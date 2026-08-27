from sqlalchemy import Column, Integer, String, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    required_skills = Column(
        JSONB,
        default=list
    )

    min_experience = Column(
        Integer,
        default=0
    )