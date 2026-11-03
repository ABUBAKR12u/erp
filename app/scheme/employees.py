from datetime import date, datetime
from typing import List, Any

from pydantic import BaseModel, Field, ConfigDict

from app.scheme.employee_roles import EmployeeRolesResponse


class EmployeesBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    branch_id: int
    first_name: str
    last_name: str
    phone: str
    email: str | None = None
    password: str
    birth_date: date
    photo_url: str
    position: str
    hired_at: date
class EmployeesCreate(EmployeesBase):
    pass

class EmployeesUpdate(EmployeesBase):
    password: str | None = None

class EmployeesResponse(BaseModel):
    id: int
    branch_id: int
    first_name: str
    last_name: str
    phone: str
    email: str | None
    birth_date: date
    photo_url: str
    position: str
    hired_at: date
    fired_at: date | None=None
    is_active: bool
    is_superadmin: bool = False
    created_at: datetime
    updated_at: datetime
    employee_role: List[EmployeeRolesResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
