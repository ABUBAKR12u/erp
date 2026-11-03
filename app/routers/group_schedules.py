from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.Base import MyDb
from app.model.group_schedules import GroupSchedule
from app.model.groups import Group
from app.routers.groups import get_group_user, allowed_branches, check_branch
from app.scheme.group_schedules import ScheduleAdd, ScheduleUpdate, ScheduleResponse
from app.utils.checker import check_ident
from app.utils.timetable import lock_timetable, occurs_on, validate_resources, check_conflicts

router = APIRouter(tags=["Group schedules"], prefix="/group-schedules")


async def timetable_group(db, group_id, current_user):
    group = await db.scalar(select(Group).where(Group.id == group_id).with_for_update().execution_options(populate_existing=True))
    if group is None:
        raise HTTPException(404, "Guruh topilmadi")
    check_branch(current_user, group.branch_id)
    return group


async def validate_schedule(db, data, current_user, schedule_id=None):
    group = await timetable_group(db, data.group_id, current_user)
    await validate_resources(db, group, data.room_id, group.teacher_id)
    if not occurs_on(data.weekday, group.start_date, group.end_date):
        raise HTTPException(400, "Guruh muddati tanlangan hafta kunini qamrab olmaydi")
    await check_conflicts(db, group, data.weekday, data.start_time, data.end_time,
                          data.room_id, group.teacher_id, schedule_id=schedule_id)


async def save_schedule(db, obj):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Jadval saqlanmadi, bu guruhning shu vaqtdagi jadvali mavjud")
    await db.refresh(obj)
    return obj


@router.get("/", response_model=Page[ScheduleResponse])
async def list_schedules(db: MyDb, search: str | None = None, branch_id: int | None = None,
                         group_id: int | None = None, teacher_id: int | None = None,
                         room_id: int | None = None, weekday: int | None = Query(default=None, ge=1, le=7),
                         current_user=Depends(get_group_user)):
    query = select(GroupSchedule).join(Group)
    ids = allowed_branches(current_user)
    if ids is not None:
        query = query.where(Group.branch_id.in_(ids))
    if branch_id is not None:
        check_branch(current_user, branch_id)
        query = query.where(Group.branch_id == branch_id)
    if search:
        query = query.where(Group.name.ilike(f"%{search}%"))
    for column, value in ((GroupSchedule.group_id, group_id), (Group.teacher_id, teacher_id),
                           (GroupSchedule.room_id, room_id), (GroupSchedule.weekday, weekday)):
        if value is not None:
            query = query.where(column == value)
    return await apaginate(db, query.order_by(GroupSchedule.weekday, GroupSchedule.start_time, GroupSchedule.id))


@router.post("/", response_model=ScheduleResponse, status_code=201)
async def add_schedule(data: ScheduleAdd, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    await validate_schedule(db, data, current_user)
    obj = GroupSchedule(**data.model_dump())
    db.add(obj)
    return await save_schedule(db, obj)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: MyDb, current_user=Depends(get_group_user)):
    obj = await check_ident(db, GroupSchedule, schedule_id)
    check_branch(current_user, obj.group.branch_id)
    return obj


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: int, data: ScheduleUpdate, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await db.scalar(select(GroupSchedule).where(GroupSchedule.id == schedule_id).with_for_update())
    if obj is None:
        raise HTTPException(404, "Jadval topilmadi")
    check_branch(current_user, obj.group.branch_id)
    await validate_schedule(db, data, current_user, schedule_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    return await save_schedule(db, obj)


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await db.scalar(select(GroupSchedule).where(GroupSchedule.id == schedule_id).with_for_update())
    if obj is None:
        raise HTTPException(404, "Jadval topilmadi")
    check_branch(current_user, obj.group.branch_id)
    await db.delete(obj)
    await db.commit()
    return {"msg": "Haftalik jadval o'chirildi, yaratilgan darslar tarixda saqlandi"}
