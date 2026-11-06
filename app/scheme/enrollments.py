from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.model.enrollments import EnrollmentStatus
from app.model.students import StudentStatus
from app.scheme.groups import GroupResponse


class EnrollmentAdd(BaseModel):
    student_id: int = Field(gt=0)
    group_id: int = Field(gt=0)
    status: EnrollmentStatus = EnrollmentStatus.faol
    price: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    joined_at: date
    left_at: date | None = None
    model_config = {"extra": "forbid"}


class EnrollmentUpdate(BaseModel):
    status: EnrollmentStatus | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    joined_at: date | None = None
    left_at: date | None = None
    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_required_fields(self):
        for field in self.model_fields_set & {"status", "joined_at"}:
            if getattr(self, field) is None:
                raise ValueError(f"{field} bo'sh bo'la olmaydi")
        return self


class EnrollmentStatusUpdate(BaseModel):
    status: EnrollmentStatus
    model_config = {"extra": "forbid"}


class EnrollmentStudent(BaseModel):
    id: int
    branch_id: int
    first_name: str
    last_name: str
    phone: str
    status: StudentStatus
    model_config = {"from_attributes": True}


class EnrollmentResponse(EnrollmentAdd):
    id: int
    price: Decimal
    created_at: datetime
    student: EnrollmentStudent
    group: GroupResponse
    model_config = {"from_attributes": True, "extra": "ignore"}
