from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException , Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.employee_roles import EmployeeRole
from app.model.employees import Employees
from app.scheme.employees import EmployeesCreate, EmployeesResponse, EmployeesUpdate
from app.utils.checker import check_ident
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, require_role, \
    get_current_user

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)

@router.post("/")
async def add_employees(employee: EmployeesCreate , db:MyDb , current_user=Depends(require_role("admin" ,"boss"))):
    result= await db.execute(select(Employees).where(Employees.phone==employee.phone))
    user= result.scalars().first()
    if user:
        raise HTTPException(409 , "Employee already exists")
    await check_ident(db, Branch , employee.branch_id)
    obj = Employees(
        **employee.model_dump(exclude={"password"}),
        password= await hash_password(employee.password)
    )
    db.add(obj)
    await db.commit()
    return {"msg":"Employee created successfully"}


from sqlalchemy.orm import selectinload
from sqlalchemy import select


@router.get("/", response_model=List[EmployeesResponse])
async def list_employees(db: MyDb,name: str = None,is_active: bool = True):
    query = select(Employees).options(
        selectinload(Employees.employee_role).selectinload(EmployeeRole.role)
  )
    if name:
        query = query.where(Employees.first_name.ilike(f"%{name}%"))
    if is_active is not None:
        query = query.where(Employees.is_active == is_active)
    find = await db.execute(query)
    return find.scalars().all()


@router.get("/me" , response_model=EmployeesResponse)
async def get_me(db:MyDb, current_user=Depends(get_current_user)):
    find= await db.execute(select(Employees).where(Employees.phone==current_user.phone))
    result= find.scalars().first()
    if not result:
        raise HTTPException(404, "Employee not found")
    return result





@router.put("/{employee_id}")
async def update_employee(employee_id: int, employee:EmployeesUpdate,db:MyDb , current_user=Depends(require_role("boss", "admin"))):
    employee_result = await check_ident(db , Employees , employee_id)
    if not employee_result.is_active:
        raise HTTPException(400, "Epmloyee is not active")

    await check_ident(db, Branch , employee_result.branch_id)
    result = await db.execute(select(Employees).where(Employees.phone==employee.phone , Employees.id != employee_id))
    user= result.scalars().first()
    if user:
        raise HTTPException(409 , "Employee already exists")
    update_user= employee.model_dump()
    update_user["password"] = await hash_password(update_user["password"])

    for field, value in update_user.items():
        setattr(employee_result, field, value)

    await db.commit()
    return {"msg":"Employee updated successfully"}


@router.patch("/{employee_id}")
async def patch_employee(employee_id: int,db:MyDb, is_active:bool=True , current_user=Depends(require_role("admin","boss"))):
    employee_result = await check_ident(db , Employees , employee_id)
    if employee_result.is_active:
        raise HTTPException(400, "Epmloyee is active")
    employee_result.is_active = is_active
    employee_result.fired_at=None
    await db.commit()
    return {"msg":"Employee is active successfully"}


@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, db:MyDb , current_user=Depends(require_role("boss" ,"admin"))):
    employee = await check_ident(db , Employees , employee_id)
    if current_user.is_active is not False:
        raise HTTPException(403, "Permission denied")
    employee.is_active = False
    employee.fired_at=datetime.now(timezone.utc)

    await db.commit()
    return {"msg":"Employee deleted successfully"}


