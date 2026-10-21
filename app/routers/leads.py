from fastapi import APIRouter

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.lead_sources import LeadSource
from app.model.lead_statuses import LeadStatus
from app.scheme.leads import LeadAdd
from app.utils.checker import check_ident

router = APIRouter(tags=["Leads"] , prefix="/leads")


@router.post("/")
async def add_lead(lead:LeadAdd , db:MyDb):
    await check_ident(db , Branch , lead.branch_id)
    await check_ident(db , LeadSource , lead.course_id)
    await check_ident(db , LeadStatus , lead.status_id)

