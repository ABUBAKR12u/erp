import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Integer, String, Date, DateTime, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.Base import Base


class StudentStatus(str, enum.Enum):
    sinovda     = "sinovda"
    faol        = "faol"
    muzlatilgan = "muzlatilgan"
    bitirgan    = "bitirgan"
    ketgan      = "ketgan"


class Student(Base):
    __tablename__ = "students"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id:    Mapped[int]           = mapped_column(Integer)
    first_name:   Mapped[str]           = mapped_column(String(60))
    last_name:    Mapped[str]           = mapped_column(String(60))
    phone:        Mapped[str]           = mapped_column(String(20))
    parent_phone: Mapped[str]           = mapped_column(String(20))
    birth_date:   Mapped[date | None]   = mapped_column(Date, nullable=True)
    source_id:    Mapped[int | None]    = mapped_column(Integer, nullable=True)
    lead_id:      Mapped[int | None]    = mapped_column(Integer, nullable=True)
    status:       Mapped[StudentStatus] = mapped_column(Enum(StudentStatus), default=StudentStatus.sinovda)
    balance:      Mapped[Decimal]       = mapped_column(Numeric(14, 2), default=0)
    created_at:   Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at:   Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)