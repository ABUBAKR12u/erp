from datetime import date, time

from pydantic import BaseModel, Field, model_validator

from app.scheme.groups import RoomInfo, TeacherInfo
from app.model.groups import GroupStatus


class TimetableGroup(BaseModel):
    id: int
    name: str
    branch_id: int
    teacher_id: int
    room_id: int
    status: GroupStatus
    start_date: date
    end_date: date | None
    max_students: int
    teacher: TeacherInfo
    model_config = {"from_attributes": True}


class TimetableTimes(BaseModel):
    start_time: time
    end_time: time
    room_id: int = Field(gt=0)
    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time.tzinfo or self.end_time.tzinfo or self.end_time <= self.start_time:
            raise ValueError("Tugash vaqti boshlanishdan keyin bo'lishi kerak; vaqt Toshkent vaqti bilan kiritiladi")
        if self.start_time.second or self.end_time.second or self.start_time.microsecond or self.end_time.microsecond:
            raise ValueError("Vaqtni soat va daqiqa bilan kiriting")
        return self


class ScheduleAdd(TimetableTimes):
    group_id: int = Field(gt=0)
    weekday: int = Field(ge=1, le=7)


class ScheduleUpdate(ScheduleAdd):
    pass


class ScheduleResponse(ScheduleAdd):
    id: int
    group: TimetableGroup
    room: RoomInfo
    model_config = {"from_attributes": True, "extra": "ignore"}
