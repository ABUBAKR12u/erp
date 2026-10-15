from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.roles import Roles
from app.scheme.roles import RoleAdd, RoleResponse, RoleUpdate
from app.utils.checker import check_ident

router = APIRouter(
    tags=["Role"],
    prefix="/role",
)

@router.post("/")
async def add_role(role:RoleAdd , db:MyDb):
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
async def list_roles(db:MyDb):
    results = await db.execute(select(Roles))
    return results.scalars().all()

@router.put("/{role_id}")
async def update_role(role:RoleUpdate, role_id:int, db:MyDb):
    role_result = await check_ident(db , Roles , role_id)

    find = await db.execute(select(Roles).where(Roles.code==role.code , Roles.id!=role_id))
    if find.scalars().first():
        raise HTTPException(409,"Role already exists")

    role_result.code=role.code
    role_result.name=role.name
    await db.commit()
    return {"message":"Role updated successfully"}

@router.delete("/{role_id}")
async def delete_role(role_id:int, db:MyDb):
    obj = await check_ident(db, Roles , role_id)
    await db.delete(obj)
    await db.commit()
    return {"message":"Role deleted successfully"}
