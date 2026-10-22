from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional
from app.model.students import StudentStatus


class BranchInfo(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}

class SourceInfo(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}

class LeadInfo(BaseModel):
    id:         int
    first_name: str
    last_name:  Optional[str]
    phone:      str
    model_config = {"from_attributes": True}


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
    first_name:   str
    last_name:    str
    phone:        str
    parent_phone: str
    birth_date:   Optional[date]
    status:       StudentStatus
    balance:      Decimal
    created_at:   datetime
    updated_at:   datetime

    branch: Optional[BranchInfo] = None
    source: Optional[SourceInfo] = None
    lead:   Optional[LeadInfo]   = None

    model_config = {"from_attributes": True}