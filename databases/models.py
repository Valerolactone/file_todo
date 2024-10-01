from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Integer, String, text
from sqlalchemy.orm import declarative_base

from settings import settings

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    file_pk = Column(Integer, primary_key=True, autoincrement=True)
    related_type = Column(String, nullable=False)
    related_id = Column(Integer, nullable=False)
    file_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            f"related_type IN ({', '.join(map(repr, settings.allowed_categories))})",
            name="check_related_type",
        ),
        Index(
            "unique_related_type_related_id",
            "related_type",
            "related_id",
            unique=True,
            postgresql_where=text("related_type != 'task_attachment'"),
        ),
    )
