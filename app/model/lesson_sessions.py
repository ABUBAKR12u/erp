import enum
from datetime import date, time, datetime, timezone

from sqlalchemy import ForeignKey, String, Text, Date, Time, DateTime, Enum, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base


class SessionStatus(str, enum.Enum):
    rejalashtirilgan = "rejalashtirilgan"
    otilgan = "otilgan"
    bekor_qilingan = "bekor_qilingan"


class LessonSession(Base):
    __tablename__ = "lesson_sessions"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_session_times"),
        UniqueConstraint("group_id", "date", "start_time", name="uq_session_group_slot"),
        Index("ix_session_date_time", "date", "start_time", "end_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.rejalashtirilgan)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    group: Mapped["Group"] = relationship("Group", lazy="selectin")
    teacher: Mapped["Employees"] = relationship("Employees", foreign_keys=[teacher_id], lazy="selectin")
    room: Mapped["Room"] = relationship("Room", lazy="selectin")
