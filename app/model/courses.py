from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Text, SmallInteger, Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.Base import Base


class Course(Base):
    __tablename__ = "courses"

    id:              Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:            Mapped[str]        = mapped_column(String(120))
    description:     Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    lessons_count:   Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    price:           Mapped[Decimal]    = mapped_column(Numeric(14, 2), default=0)
    min_age:         Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_active:       Mapped[bool]       = mapped_column(Boolean, default=True)
    created_at:      Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=datetime.utcnow)