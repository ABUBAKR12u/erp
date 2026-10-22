from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from typing import Optional
class BranchInfo(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}

class SourceInfo(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}

class StatusInfo(BaseModel):
    id:      int
    name:    str
    is_won:  bool
    is_lost: bool
    model_config = {"from_attributes": True}

class CourseInfo(BaseModel):
    id:    int
    name:  str
    price: Decimal
    model_config = {"from_attributes": True}

class EmployeeInfo(BaseModel):
    id:         int
    first_name: str
    last_name:  str
    model_config = {"from_attributes": True}

class StudentInfo(BaseModel):
    id:         int
    first_name: str
    last_name:  str
    phone:      str
    model_config = {"from_attributes": True}

class LeadBase(BaseModel):
    branch_id:   int
    first_name:  str
    last_name:   Optional[str] = None
    phone:       str
    source_id:   Optional[int] = None
    status_id:   Optional[int] = None
    course_id:   Optional[int] = None
    assigned_to: Optional[int] = None
    comment:     Optional[str] = None

class LeadAdd(LeadBase):
    pass
class LeadUpdate(LeadBase):
    pass


class LeadResponse(BaseModel):
    id:          int
    first_name:  str
    last_name:   Optional[str]
    phone:       str
    lost_reason: Optional[str]
    comment:     Optional[str]
    created_at:  datetime
    updated_at:  datetime
    created_by: Optional[int] = None
    branch:   Optional[BranchInfo]   = None
    source:   Optional[SourceInfo]   = None
    status:   Optional[StatusInfo]   = None
    course:   Optional[CourseInfo]   = None
    assignee: Optional[EmployeeInfo] = None
    creator:  Optional[EmployeeInfo] = None
    student:  Optional[StudentInfo]  = None

    model_config = {"from_attributes": True}