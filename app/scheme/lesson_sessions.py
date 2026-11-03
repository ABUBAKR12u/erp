from datetime import date as Date, datetime

from pydantic import BaseModel, Field, model_validator

from app.model.lesson_sessions import SessionStatus
from app.scheme.group_schedules import TimetableTimes, TimetableGroup
from app.scheme.groups import TeacherInfo, RoomInfo


class SessionAdd(TimetableTimes):
    group_id: int = Field(gt=0)
    date: Date
    teacher_id: int = Field(gt=0)
    topic: str | None = Field(default=None, max_length=200)
    status: SessionStatus = SessionStatus.rejalashtirilgan
    note: str | None = Field(default=None, max_length=5000)

class SessionUpdate(SessionAdd):
    pass


class SessionResponse(SessionAdd):
    id: int
    group: TimetableGroup
    teacher: TeacherInfo
    room: RoomInfo
    created_at: datetime
    model_config = {"from_attributes": True, "extra": "ignore"}


class SessionStatusUpdate(BaseModel):
    status: SessionStatus
    model_config = {"extra": "forbid"}


class GenerateSessions(BaseModel):
    group_id: int = Field(gt=0)
    date_from: Date
    date_to: Date
    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_range(self):
        if self.date_to < self.date_from or (self.date_to - self.date_from).days > 92:
            raise ValueError("Davr 1 kundan 93 kungacha bo'lishi kerak")
        return self
