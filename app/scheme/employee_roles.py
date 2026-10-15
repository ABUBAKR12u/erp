from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.scheme.roles import RoleResponse


class EmployeeRolesBase(BaseModel):
    employee_id: int
    role_id: int
    branch_id: int

class EmployeeRolesAdd(EmployeeRolesBase):
    pass

class EmployeeRolesUpdate(BaseModel):
    role_id: int
    branch_id: int
class EmployeeRolesResponse(BaseModel):
    employee_id: int
    role_id: int
    branch_id: int
    role: Optional[RoleResponse] = None
    model_config = ConfigDict(from_attributes=True)

