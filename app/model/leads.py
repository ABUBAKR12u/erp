from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.Base import Base


class Lead(Base):
    __tablename__ = "leads"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id:   Mapped[int]        = mapped_column(Integer)
    first_name:  Mapped[str]        = mapped_column(String(60))
    last_name:   Mapped[str | None] = mapped_column(String(60), nullable=True)
    phone:       Mapped[str]        = mapped_column(String(20))
    source_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    course_id:   Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    student_id:  Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment:     Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by:  Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at:  Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at:  Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)