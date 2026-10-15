from pydantic import BaseModel

class EmployeeRolesBase(BaseModel):
    employee_id: int
    role_id: int
    branch_id: int

class EmployeeRolesAdd(EmployeeRolesBase):
    pass

class EmployeeRolesUpdate(BaseModel):
    role_id: int
    branch_id: int
class EmployeeRolesResponse(EmployeeRolesBase):
    pass
