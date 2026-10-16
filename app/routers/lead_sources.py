from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.lead_sources import LeadSource
from app.scheme.lead_sources import LeadSourceUpdate, LeadSourceAdd, LeadSourceResponse
from app.utils.security import require_role

router = APIRouter(tags=["Lead Source"] , prefix="/lead_source")

@router.post("/")
async def add_lead_source(lead_source: LeadSourceAdd , db:MyDb , current_user=Depends(require_role("admin" ,"boss", "manager"))):
    find = await db.execute(select(LeadSource).where(LeadSource.name == lead_source.name))
    result = find.scalars().first()
    if result:
        raise HTTPException(status_code=400, detail="Lead Source already exists")
    obj= LeadSource(
        **lead_source.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"msg": "Lead Source added successfully"}

@router.get("/", response_model=List[LeadSourceResponse])
async def get_lead_source(db:MyDb , current_user=Depends(require_role("admin" ,"boss", "manager"))):
    find= await db.execute(select(LeadSource))
    return find.scalars().all()


@router.put("/{lead_source_id}")
async def  update_lead_source(lead_source_id:int , lead_source: LeadSourceUpdate,db:MyDb , current_user=Depends(require_role("admin" ,"boss", "manager"))):
    find = await db.execute(select(LeadSource).where(LeadSource.id == lead_source_id))
    result = find.scalars().first()
    if not result:
        raise HTTPException(status_code=404, detail="Lead Source not found")
    if not result.is_active:
        raise HTTPException(status_code=401, detail="Lead Source isn't active")

    result.name=lead_source.name
    result.monthly_budget= lead_source.monthly_budget

    await db.commit()
    return {"msg": "Lead Source updated successfully"}


@router.patch("/{lead_source_id}")
async def change_lead_source(lead_source_id:int , db:MyDb, lead_source:bool=True , current_user=Depends(require_role("admin" ,"boss", "manager"))):
    find= await db.execute(select(LeadSource).where(LeadSource.id == lead_source_id))
    result = find.scalars().first()
    if not result:
        raise HTTPException(status_code=404, detail="Lead Source not found")
    result.is_active=lead_source
    await db.commit()
    return {"msg": "Lead Source updated successfully"}

@router.delete("/{lead_source_id}")
async def delete_lead_source(lead_source_id:int ,db: MyDb , current_user=Depends(require_role("admin" ,"boss", "manager"))):
    result = await db.execute(select(LeadSource).where(LeadSource.id == lead_source_id))
    find = result.scalars().first()
    if not find:
        raise HTTPException(status_code=404, detail="Lead Source not found")
    await db.delete(find)
    await db.commit()
    return {"msg": "Lead Source deleted successfully"}
