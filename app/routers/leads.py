from typing import List
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional
from sqlalchemy import or_
from app.database.Base import MyDb
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from app.model.branches import Branch
from app.model.courses import Course
from app.model.employees import Employees
from app.model.lead_sources import LeadSource
from app.model.lead_statuses import LeadStatus
from app.model.leads import Lead
from app.model.students import Student, StudentStatus
from app.scheme.leads import LeadAdd, LeadResponse, LeadUpdate
from app.utils.checker import check_ident
from app.utils.security import require_role

router = APIRouter(tags=["Leads"] , prefix="/leads")


@router.post("/")
async def add_lead(leads: LeadAdd, db: MyDb, current_user=Depends(require_role("admin", "boss"))):
    await check_ident(db, Branch, leads.branch_id)
    await check_ident(db, LeadSource, leads.source_id)
    await check_ident(db, Course, leads.course_id)
    await check_ident(db, LeadStatus, leads.status_id)
    if leads.assigned_to:
        await check_ident(db, Employees, leads.assigned_to)

    find = await db.execute(
        select(Lead).where(
            Lead.phone == leads.phone,
            Lead.branch_id == leads.branch_id
        )
    )
    if find.scalars().first():
        raise HTTPException(409, "Bu raqam bu filialda allaqachon mavjud")

    student_find = await db.execute(
        select(Student).where(Student.phone == leads.phone)
    )
    student = student_find.scalars().first()
    if student:
        if student.status not in (StudentStatus.bitirgan, StudentStatus.ketgan):
            raise HTTPException(
                409,
                f"Bu raqamdagi o'quvchi allaqachon mavjud, status: {student.status.value}"
            )

    obj = Lead(**leads.model_dump(), created_by=current_user.id)
    db.add(obj)
    await db.commit()
    return {"message": "Lead added successfully"}


@router.get("/", response_model=Page[LeadResponse])
async def get_leads(
    db: MyDb,
    search:      Optional[str]      = None,
    assigned_to: Optional[int]      = None,
    created_by:  Optional[int]      = None,
    status_id:   Optional[int]      = None,
    from_date:   Optional[datetime] = None,
    to_date:     Optional[datetime] = None,
):
    query = select(Lead).options(
        selectinload(Lead.branch),
        selectinload(Lead.source),
        selectinload(Lead.status),
        selectinload(Lead.course),
        selectinload(Lead.assignee),
        selectinload(Lead.creator),
        selectinload(Lead.student),
    )

    conditions = []

    if search:
        conditions.append(
            or_(
                Lead.phone.ilike(f"%{search}%"),
                Lead.first_name.ilike(f"%{search}%"),
                Lead.last_name.ilike(f"%{search}%"),
            )
        )
    if assigned_to:
        conditions.append(Lead.assigned_to == assigned_to)
    if created_by:
        conditions.append(Lead.created_by == created_by)
    if status_id:
        conditions.append(Lead.status_id == status_id)
    if from_date:
        conditions.append(Lead.created_at >= from_date)
    if to_date:
        conditions.append(Lead.created_at <= to_date)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Lead.id.desc())
    return await apaginate(db, query)
@router.put("/{lead_id}")
async def update_lead(lead_id: int, leads: LeadUpdate, db: MyDb, current_user=Depends(require_role("admin", "boss"))):
    obj = await db.get(Lead, lead_id)
    if not obj:
        raise HTTPException(404, "Lead not found")
    await check_ident(db, Branch, leads.branch_id)
    await check_ident(db, LeadSource, leads.source_id)
    await check_ident(db, Course, leads.course_id)
    await check_ident(db, LeadStatus, leads.status_id)
    if leads.assigned_to:
        await check_ident(db, Employees, leads.assigned_to)
    if leads.phone != obj.phone:
        find = await db.execute(
            select(Lead).where(
                Lead.phone == leads.phone,
                Lead.branch_id == obj.branch_id,
                Lead.id != lead_id
            )
        )
        if find.scalars().first():
            raise HTTPException(409, "Bu raqam bu filialda allaqachon mavjud")

        student_find = await db.execute(
            select(Student).where(Student.phone == leads.phone)
        )
        student = student_find.scalars().first()
        if student:
            if student.status not in (StudentStatus.bitirgan, StudentStatus.ketgan):
                raise HTTPException(
                    409,
                    f"Bu raqamdagi o'quvchi allaqachon mavjud, status: {student.status.value}"
                )

    for field, value in leads.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    await db.commit()
    return {"message": "Lead updated successfully"}

@router.patch("/{lead_id}")
async def convert_lead(lead_id: int, student_id: int, db: MyDb, current_user=Depends(require_role("admin", "boss"))):
    obj = await db.get(Lead, lead_id)
    if not obj:
        raise HTTPException(404, "Lead not found")

    student = await check_ident(db, Student, student_id)

    obj.student_id = student_id
    student.status = StudentStatus.faol

    await db.commit()
    return {"message": "Lead converted successfully"}

@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, db: MyDb, current_user=Depends(require_role("admin", "boss"))):
    obj = await db.get(Lead, lead_id)
    if not obj:
        raise HTTPException(404, "Lead not found")

    await db.delete(obj)
    await db.commit()
    return {"message": "Lead deleted successfully"}