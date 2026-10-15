from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.employee_roles import EmployeeRole
from app.model.employees import Employees
from app.model.roles import Roles
from app.scheme.employee_roles import EmployeeRolesAdd, EmployeeRolesResponse, EmployeeRolesUpdate
from app.utils.checker import check_ident
from app.utils.security import require_role

router = APIRouter(tags=["Employee roles"] , prefix="/employee-roles")


@router.post("/")
async def add_employee_roles(employee_roles:EmployeeRolesAdd , db:MyDb, current_user=Depends(require_role("boss"))):
    await check_ident(db , Employees , employee_roles.employee_id)
    await check_ident(db , Roles, employee_roles.role_id)
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
    result = await db.execute(select(EmployeeRole))
    return result.scalars().all()




@router.put("/{employee_role_id")
async def update_employee_role(employee_role_id:int, employee_role:EmployeeRolesUpdate , db:MyDb , current_user=Depends(require_role("boss"))):

    await check_ident(db , Roles , employee_role.role_id)
    await check_ident(db , Branch , employee_role.branch_id)

    result = await db.execute(select(EmployeeRole).where(EmployeeRole.employee_id==employee_role_id))
    found= result.scalars().first()
    if not found:
        raise HTTPException(404,"Employee role not found")

    found.role_id = employee_role.role_id
    found.branch_id = employee_role.branch_id
    await db.commit()
    return {"msg":"employee role updated"}

@router.delete("/{employee_id}/{role_id}")
async def delete_employee_role(
    employee_id: int,
    role_id: int,
    db: MyDb,
    branch_id: int | None = None,
    current_user=Depends(require_role("boss")),
):
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





