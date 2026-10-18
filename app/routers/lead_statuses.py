from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.database.Base import MyDb
from app.model.lead_statuses import LeadStatus
from app.scheme.lead_statuses import LeadStatusAdd, LeadStatusResponse, LeadStatusUpdate
from app.utils.checker import normalize_name

router = APIRouter(
    tags=["Lead Statuses"],
    prefix="/lead_statuses",
)

@router.post("/")
async def add_lead_status(lead_status: LeadStatusAdd , db:MyDb):
    name = normalize_name(lead_status.name)

    find = await db.execute(select(LeadStatus).where(func.lower(LeadStatus.name) == name.lower()))
    result = find.scalars().first()
    if result:
        raise HTTPException(401 , "Lead status already exists")
    if lead_status.is_lost == True and lead_status.is_won== True:
        raise HTTPException(422 , "Unprocessable Content")


    last = await db.scalar(select(func.max(LeadStatus.position)))
    obj = LeadStatus(
        name=name,
        is_lost=lead_status.is_lost,
        is_won=lead_status.is_won,
        position=(last or 0) + 1
    )
    db.add(obj)
    await db.commit()
    return {"message": "Lead status added successfully"}

@router.get("/", response_model=List[LeadStatusResponse])
async def get_lead_statuses(db:MyDb):
    find= await db.execute(select(LeadStatus))
    return find.scalars().all()

@router.put("/{lead_status_id}")
async def update_lead_status(lead_status_id: int, lead_status: LeadStatusUpdate, db: MyDb):
    name = normalize_name(lead_status.name)
    obj = await db.get(LeadStatus, lead_status_id)

    if not obj:
        raise HTTPException(404, "Lead status not found")

    find = await db.execute(
        select(LeadStatus).where(
            func.lower(LeadStatus.name) == name.lower(),
            LeadStatus.id != lead_status_id
        )
    )
    result = find.scalars().first()

    if result:
        raise HTTPException(409, "Lead status already exists")

    obj.name = name
    obj.is_lost = lead_status.is_lost
    obj.is_won = lead_status.is_won
    await db.commit()
    return {"message": "Lead status updated successfully"}

@router.patch("/{lead_status_id}")
async def update_lead_status_name(lead_status_id:int, lead_status_new_name:str , db:MyDb):
    name = normalize_name(lead_status_new_name)
    obj = await db.get(LeadStatus, lead_status_id)
    if not obj:
        raise HTTPException(404 , "Lead status not found")
    find = await db.execute(select(LeadStatus).where(func.lower(LeadStatus.name)==name.lower(),LeadStatus.id != lead_status_id))
    result = find.scalars().first()
    if result:
        raise HTTPException(409 , "Lead status already exists")
    obj.name=name
    await db.commit()
    return {"message": "Lead status updated successfully"}

