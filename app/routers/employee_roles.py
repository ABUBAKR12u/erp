from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.employee_roles import EmployeeRole
from app.model.employees import Employees
from app.model.roles import Roles
from app.scheme.employee_roles import EmployeeRolesAdd, EmployeeRolesResponse, EmployeeRolesUpdate
from app.utils.checker import check_ident
from app.utils.security import require_role

router = APIRouter(tags=["Employee roles"] , prefix="/employee-roles")


async def protect_main_admin_role(db, employee_id, role_id):
    employee = await check_ident(db, Employees, employee_id)
    role = await check_ident(db, Roles, role_id)
    if employee.is_superadmin and role.code in ("boss", "admin"):
        raise HTTPException(403, "Asosiy administratorning boshqaruv rolini olib tashlab yoki o'zgartirib bo'lmaydi")


@router.post("/")
async def add_employee_roles(employee_roles:EmployeeRolesAdd , db:MyDb, current_user=Depends(require_role("boss"))):
    await check_ident(db , Employees , employee_roles.employee_id)
    await check_ident(db , Roles, employee_roles.role_id)
    if employee_roles.branch_id is not None:
        await check_ident(db , Branch , employee_roles.branch_id)

    result = await db.execute(select(EmployeeRole).where(EmployeeRole.employee_id == employee_roles.employee_id , EmployeeRole.role_id == employee_roles.role_id))
    if result.scalars().first():
        return {"msg":"employee roles already added"}
    obj = EmployeeRole(
        **employee_roles.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"msg":"employee roles added"}

@router.get("/" , response_model=List[EmployeeRolesResponse])
async def list_employee_roles(db:MyDb , current_user=Depends(require_role("boss"))):
    result = await db.execute(select(EmployeeRole).options(selectinload(EmployeeRole.role)))
    return result.scalars().all()




@router.put("/{employee_id}/{role_id}")
async def update_employee_role(employee_id:int, role_id:int, employee_role:EmployeeRolesUpdate , db:MyDb , current_user=Depends(require_role("boss"))):
    await protect_main_admin_role(db, employee_id, role_id)

    await check_ident(db , Roles , employee_role.role_id)
    if employee_role.branch_id is not None:
        await check_ident(db , Branch , employee_role.branch_id)

    result = await db.execute(select(EmployeeRole).where(EmployeeRole.employee_id==employee_id, EmployeeRole.role_id==role_id))
    found= result.scalars().first()
    if not found:
        raise HTTPException(404,"Employee role not found")

    found.role_id = employee_role.role_id
    found.branch_id = employee_role.branch_id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Bu rol xodimga allaqachon biriktirilgan")
    return {"msg":"employee role updated"}

@router.delete("/{employee_id}/{role_id}")
async def delete_employee_role(
    employee_id: int,
    role_id: int,
    db: MyDb,
    branch_id: int | None = None,
    current_user=Depends(require_role("boss")),
):
    await protect_main_admin_role(db, employee_id, role_id)
    stmt = select(EmployeeRole).where(
        EmployeeRole.employee_id == employee_id,
        EmployeeRole.role_id == role_id,
    )
    if branch_id is not None:
        stmt = stmt.where(EmployeeRole.branch_id == branch_id)

    rows = (await db.execute(stmt)).scalars().all()
    if not rows:
        raise HTTPException(404, "Employee role not found")

    if len(rows) > 1:
        raise HTTPException(
            409, "Bu rol bir nechta filialda bor, branch_id ni ko'rsating"
        )

    await db.delete(rows[0])
    await db.commit()
    return {"msg": "employee role deleted"}





