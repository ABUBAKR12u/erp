import enum
from datetime import datetime, date, timezone
from decimal import Decimal

from sqlalchemy import Integer, String, Date, DateTime, SmallInteger, Numeric, Enum, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base


class GroupStatus(str, enum.Enum):
    rejalashtirilgan = "rejalashtirilgan"
    faol            = "faol"
    tugagan         = "tugagan"
    bekor_qilingan  = "bekor_qilingan"


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint("branch_id", "name", name="uq_group_branch_name"),
        CheckConstraint("max_students > 0", name="ck_group_max_students"),
        CheckConstraint("current_students >= 0 AND current_students <= max_students", name="ck_group_current_students"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_group_dates"),
        CheckConstraint("price IS NULL OR price >= 0", name="ck_group_price"),
    )

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id:        Mapped[int]           = mapped_column(ForeignKey("branches.id"))
    course_id:        Mapped[int]           = mapped_column(ForeignKey("courses.id"))
    name:             Mapped[str]           = mapped_column(String(80))
    teacher_id:       Mapped[int]           = mapped_column(ForeignKey("employees.id"))
    room_id:          Mapped[int]           = mapped_column(ForeignKey("rooms.id"))
    status:           Mapped[GroupStatus]   = mapped_column(Enum(GroupStatus), default=GroupStatus.rejalashtirilgan)
    start_date:       Mapped[date]          = mapped_column(Date)
    end_date:         Mapped[date | None]   = mapped_column(Date, nullable=True)
    max_students:     Mapped[int]           = mapped_column(SmallInteger)
    current_students: Mapped[int]           = mapped_column(SmallInteger, default=0, server_default="0")
    price:            Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    created_at:       Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    branch:  Mapped["Branch"]    = relationship("Branch", lazy="selectin")
    course:  Mapped["Course"]    = relationship("Course", lazy="selectin")
    teacher: Mapped["Employees"] = relationship("Employees", foreign_keys=[teacher_id], lazy="selectin")
    room:    Mapped["Room"]      = relationship("Room", lazy="selectin")
