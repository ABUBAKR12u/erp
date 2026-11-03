from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.courses import Course
from app.model.employees import Employees
from app.model.groups import Group, GroupStatus
from app.model.leads import Lead
from app.model.lead_sources import LeadSource
from app.model.lead_statuses import LeadStatus
from app.model.roles import Roles
from app.model.rooms import Room
from app.model.students import Student, StudentStatus
from app.model.teacher_profiles import TeacherProfiles
from app.utils.security import get_current_user

router = APIRouter(tags=["Workspace"], prefix="/workspace")


def branch_ids(user):
    if user.is_superadmin:
        return None
    roles = [er for er in user.employee_role if er.role.code in ("admin", "boss")]
    if any(er.branch_id is None for er in roles):
        return None
    return {er.branch_id for er in roles} or {user.branch_id}


def scoped(query, column, user, branch_id=None):
    ids = branch_ids(user)
    if branch_id is not None:
        if ids is not None and branch_id not in ids:
            raise HTTPException(403, "Bu filialga ruxsatingiz yo'q")
        return query.where(column == branch_id)
    return query if ids is None else query.where(column.in_(ids))


@router.get("/options")
async def workspace_options(db: MyDb, current_user=Depends(get_current_user)):
    branches = (await db.execute(scoped(select(Branch), Branch.id, current_user).order_by(Branch.name))).scalars().all()
    employees = (await db.execute(scoped(select(Employees), Employees.branch_id, current_user).order_by(Employees.first_name))).scalars().all()
    rooms = (await db.execute(scoped(select(Room), Room.branch_id, current_user).order_by(Room.name))).scalars().all()
    students = (await db.execute(scoped(select(Student.id, Student.first_name, Student.last_name, Student.phone, Student.branch_id), Student.branch_id, current_user))).mappings().all()
    leads = (await db.execute(scoped(select(Lead.id, Lead.first_name, Lead.last_name, Lead.phone, Lead.branch_id), Lead.branch_id, current_user))).mappings().all()
    roles = (await db.execute(select(Roles).order_by(Roles.name))).scalars().all()
    courses = (await db.execute(select(Course).order_by(Course.name))).scalars().all()
    sources = (await db.execute(select(LeadSource).order_by(LeadSource.name))).scalars().all()
    statuses = (await db.execute(select(LeadStatus).order_by(LeadStatus.position))).scalars().all()
    profiles = (await db.execute(select(TeacherProfiles.employee_id))).scalars().all()
    return {
        "user": {
            "id": current_user.id, "first_name": current_user.first_name, "last_name": current_user.last_name,
            "name": f"{current_user.first_name} {current_user.last_name}", "phone": current_user.phone,
            "email": current_user.email, "position": current_user.position, "branch_id": current_user.branch_id,
            "is_superadmin": current_user.is_superadmin,
            "roles": [{"code": er.role.code, "name": er.role.name, "branch_id": er.branch_id} for er in current_user.employee_role],
        },
        "branches": [{"id": b.id, "name": b.name, "code": b.code, "is_active": b.is_active} for b in branches],
        "courses": [{"id": c.id, "name": c.name, "price": c.price, "is_active": c.is_active} for c in courses],
        "employees": [{"id": e.id, "first_name": e.first_name, "last_name": e.last_name, "branch_id": e.branch_id, "phone": e.phone, "is_active": e.is_active, "is_superadmin": e.is_superadmin, "is_teacher": e.id in profiles} for e in employees],
        "rooms": [{"id": r.id, "name": r.name, "branch_id": r.branch_id, "capacity": r.capacity, "is_active": r.is_active} for r in rooms],
        "roles": [{"id": r.id, "code": r.code, "name": r.name, "is_system": r.is_system} for r in roles],
        "sources": [{"id": s.id, "name": s.name, "is_active": s.is_active} for s in sources],
        "statuses": [{"id": s.id, "name": s.name, "position": s.position, "is_won": s.is_won, "is_lost": s.is_lost} for s in statuses],
        "students": [dict(row) for row in students], "leads": [dict(row) for row in leads],
    }


@router.get("/overview")
async def workspace_overview(db: MyDb, branch_id: int | None = None, current_user=Depends(get_current_user)):
    async def count(model, *conditions):
        query = scoped(select(func.count(model.id)), model.branch_id, current_user, branch_id)
        return await db.scalar(query.where(*conditions)) or 0

    students = await count(Student)
    active_students = await count(Student, Student.status == StudentStatus.faol)
    leads = await count(Lead)
    groups = await count(Group)
    active_groups = await count(Group, Group.status == GroupStatus.faol)
    seats = (await db.execute(scoped(
        select(func.coalesce(func.sum(Group.max_students), 0), func.coalesce(func.sum(Group.current_students), 0)).where(Group.status.in_((GroupStatus.faol, GroupStatus.rejalashtirilgan))),
        Group.branch_id, current_user, branch_id,
    ))).one()
    today = datetime.now(timezone(timedelta(hours=5))).date()
    start_index = today.year * 12 + today.month - 6
    months = [((start_index + offset) // 12, (start_index + offset) % 12 + 1) for offset in range(6)]
    since = datetime(months[0][0], months[0][1], 1)
    trend = [{"month": f"{year}-{month:02d}", "students": 0, "leads": 0} for year, month in months]
    for model, key in ((Student, "students"), (Lead, "leads")):
        dates = (await db.execute(scoped(select(model.created_at).where(model.created_at >= since), model.branch_id, current_user, branch_id))).scalars().all()
        for created in dates:
            for item in trend:
                if created.strftime("%Y-%m") == item["month"]:
                    item[key] += 1
                    break
    status_counts = (await db.execute(scoped(select(Lead.status_id, func.count(Lead.id)).group_by(Lead.status_id), Lead.branch_id, current_user, branch_id))).all()
    source_counts = (await db.execute(scoped(select(Lead.source_id, func.count(Lead.id)).group_by(Lead.source_id), Lead.branch_id, current_user, branch_id))).all()
    recent = (await db.execute(scoped(select(Lead).order_by(Lead.created_at.desc()).limit(5), Lead.branch_id, current_user, branch_id))).scalars().all()
    return {
        "students": students, "active_students": active_students, "leads": leads,
        "groups": groups, "active_groups": active_groups,
        "active_courses": await db.scalar(select(func.count(Course.id)).where(Course.is_active == True)),
        "seats": int(seats[0]), "occupied": int(seats[1]), "trend": trend,
        "statuses": [{"id": ident, "count": count} for ident, count in status_counts],
        "sources": [{"id": ident, "count": count} for ident, count in source_counts],
        "recent_leads": [{"id": lead.id, "first_name": lead.first_name, "last_name": lead.last_name, "phone": lead.phone, "status_id": lead.status_id, "course_id": lead.course_id, "created_at": lead.created_at} for lead in recent],
    }
