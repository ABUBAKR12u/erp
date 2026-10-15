from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.database.Base import MyDb
from app.model.employee_roles import EmployeeRole
from app.model.roles import Roles
from app.scheme.roles import RoleAdd, RoleResponse, RoleUpdate
from app.utils.checker import check_ident
from app.utils.security import get_current_user, require_role

router = APIRouter(
    tags=["Role"],
    prefix="/role",
)

@router.post("/")
async def add_role(role:RoleAdd , db:MyDb , current_user=Depends(require_role("boss"))):
    find = await db.execute(select(Roles).where(Roles.code==role.code))
    result= find.scalars().first()
    if result:
        raise HTTPException(409,"Role already exists")
    obj = Roles(
        **role.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"message":"Role created successfully"}

@router.get("/" , response_model=List[RoleResponse])
async def list_roles(db:MyDb ,current_user=Depends(require_role("boss", "admin"))):
    results = await db.execute(select(Roles))
    return results.scalars().all()

@router.put("/{role_id}")
async def update_role(role:RoleUpdate, role_id:int, db:MyDb , current_user=Depends(require_role("boss"))):
    role_result = await check_ident(db , Roles , role_id)

    find = await db.execute(select(Roles).where(Roles.code==role.code , Roles.id!=role_id))
    if find.scalars().first():
        raise HTTPException(409,"Role already exists")

    role_result.code=role.code
    role_result.name=role.name
    await db.commit()
    return {"message":"Role updated successfully"}

@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: MyDb,
current_user=Depends(require_role("boss"))
):
    obj = await check_ident(db, Roles, role_id)

    in_use = await db.scalar(
        select(EmployeeRole.employee_id)
        .where(EmployeeRole.role_id == role_id)
        .limit(1)
    )
    if in_use is not None:
        raise HTTPException(409, "Bu rol xodimlarga biriktirilgan, avval ularni olib tashlang")

    await db.delete(obj)
    await db.commit()
    return {"message": "Role deleted successfully"}