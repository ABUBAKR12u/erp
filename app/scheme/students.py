from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

from app.model.students import StudentStatus


class StudentBase(BaseModel):
    branch_id:    int
    first_name:   str
    last_name:    str
    phone:        str
    parent_phone: str
    birth_date:   Optional[date] = None
    source_id:    Optional[int] = None
    lead_id:      Optional[int] = None


class StudentAdd(StudentBase):
    pass


class StudentUpdate(BaseModel):
    branch_id:    Optional[int] = None
    first_name:   Optional[str] = None
    last_name:    Optional[str] = None
    phone:        Optional[str] = None
    parent_phone: Optional[str] = None
    birth_date:   Optional[date] = None
    source_id:    Optional[int] = None
    lead_id:      Optional[int] = None


class StudentStatusUpdate(BaseModel):
    status: StudentStatus


class StudentResponse(BaseModel):
    id:           int
    branch_id:    int
    first_name:   str
    last_name:    str
    phone:        str
    parent_phone: str
    birth_date:   Optional[date]
    source_id:    Optional[int]
    lead_id:      Optional[int]
    status:       StudentStatus
    balance:      Decimal
    created_at:   datetime
    updated_at:   datetime

    class Config:
        from_attributes = True