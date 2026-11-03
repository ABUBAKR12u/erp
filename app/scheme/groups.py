from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, Field, computed_field, model_validator

from app.model.groups import GroupStatus


class BranchInfo(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}


class CourseInfo(BranchInfo):
    price: Decimal
    duration_months: int | None = None


class TeacherInfo(BaseModel):
    id:         int
    branch_id:  int
    first_name: str
    last_name:  str
    model_config = {"from_attributes": True}


class RoomInfo(BranchInfo):
    branch_id: int
    capacity:  int


class GroupBase(BaseModel):
    branch_id:    int = Field(gt=0)
    course_id:    int = Field(gt=0)
    name:         str = Field(min_length=1, max_length=80)
    teacher_id:   int = Field(gt=0)
    room_id:      int = Field(gt=0)
    status:       GroupStatus = GroupStatus.rejalashtirilgan
    start_date:   date
    end_date:     date | None = None
    max_students: int = Field(gt=0, le=32767)
    price:        Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Tugash sanasi boshlanish sanasidan oldin bo'la olmaydi")
        return self


class GroupAdd(GroupBase):
    pass


class GroupUpdate(BaseModel):
    branch_id:    int | None = Field(default=None, gt=0)
    course_id:    int | None = Field(default=None, gt=0)
    name:         str | None = Field(default=None, min_length=1, max_length=80)
    teacher_id:   int | None = Field(default=None, gt=0)
    room_id:      int | None = Field(default=None, gt=0)
    status:       GroupStatus | None = None
    start_date:   date | None = None
    end_date:     date | None = None
    max_students: int | None = Field(default=None, gt=0, le=32767)
    price:        Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_required_fields(self):
        for field in self.model_fields_set - {"end_date", "price"}:
            if getattr(self, field) is None:
                raise ValueError(f"{field} bo'sh bo'la olmaydi")
        return self


class GroupStatusUpdate(BaseModel):
    status: GroupStatus
    model_config = {"extra": "forbid"}


class GroupResponse(GroupBase):
    id:               int
    current_students: int
    created_at:       datetime
    branch:           BranchInfo
    course:           CourseInfo
    teacher:          TeacherInfo
    room:             RoomInfo

    model_config = {"from_attributes": True, "extra": "ignore"}

    @computed_field
    @property
    def effective_price(self) -> Decimal:
        return self.price if self.price is not None else self.course.price


class GroupOptions(BaseModel):
    user:     BranchInfo
    branches: list[BranchInfo]
    courses:  list[CourseInfo]
    teachers: list[TeacherInfo]
    rooms:    list[RoomInfo]
