from datetime import time

from sqlalchemy import ForeignKey, SmallInteger, Time, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.Base import Base


class GroupSchedule(Base):
    __tablename__ = "group_schedules"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 1 AND 7", name="ck_schedule_weekday"),
        CheckConstraint("end_time > start_time", name="ck_schedule_times"),
        UniqueConstraint("group_id", "weekday", "start_time", name="uq_schedule_group_slot"),
        Index("ix_schedule_day_time", "weekday", "start_time", "end_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    weekday: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    group: Mapped["Group"] = relationship("Group", lazy="selectin")
    room: Mapped["Room"] = relationship("Room", lazy="selectin")
