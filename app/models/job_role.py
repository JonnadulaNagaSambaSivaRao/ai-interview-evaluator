from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class JobRole(Base):

    __tablename__ = "job_roles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )