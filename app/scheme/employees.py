from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from app.scheme.employee_roles import EmployeeRolesResponse


class EmployeesBase(BaseModel):
    branch_id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    password: str
    birth_date: date
    photo_url: str
    position: str
    hired_at: date
    employee_role: List[EmployeeRolesResponse] = []

class EmployeesCreate(EmployeesBase):
    pass

class EmployeesUpdate(EmployeesBase):
    pass

class EmployeesResponse(BaseModel):
    id: int
    branch_id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    birth_date: date
    photo_url: str
    position: str
    hired_at: date
    fired_at: date | None=None
    is_active: bool
    created_at: datetime
    updated_at: datetime