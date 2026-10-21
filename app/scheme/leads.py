from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class LeadBase(BaseModel):
    branch_id:   int
    first_name:  str
    last_name:   Optional[str] = None
    phone:       str
    source_id:   Optional[int] = None
    status_id:   Optional[int] = None
    course_id:   Optional[int] = None
    assigned_to: Optional[int] = None
    lost_reason: Optional[str] = None
    comment:     Optional[str] = None

class LeadAdd(LeadBase):
    pass
class LeadUpdate(LeadBase):
    pass


class LeadResponse(BaseModel):
    id:          int
    branch_id:   int
    first_name:  str
    last_name:   Optional[str]
    phone:       str
    source_id:   Optional[int]
    status_id:   Optional[int]
    course_id:   Optional[int]
    assigned_to: Optional[int]
    lost_reason: Optional[str]
    student_id:  Optional[int]
    comment:     Optional[str]
    created_by:  Optional[int]
    created_at:  datetime
    updated_at:  datetime