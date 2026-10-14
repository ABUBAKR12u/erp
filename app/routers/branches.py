from typing import List

from fastapi import APIRouter, status, HTTPException
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.scheme.branches import BranchAdd, BranchResponse

router = APIRouter(tags=['Branches'] , prefix="/branches")

@router.post("/" , status_code=status.HTTP_201_CREATED)
async def add_branch(branch : BranchAdd , db:MyDb):
    find = await db.execute(select(Branch).where(Branch.code == branch.code))
    result = find.scalars().first()
    if result:
        raise HTTPException(409 , "Code already exists")

    obj = Branch(
    **branch.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"msg":"branch added successfully"}

@router.get("/" , response_model=List[BranchResponse])
async def list_branches(db:MyDb , name:str=None):
    result = await db.execute(select(Branch))
    if name:
        result = await db.execute(select(Branch).where(Branch.name.ilike(f"%{name}%")))

    return result.scalars().all()