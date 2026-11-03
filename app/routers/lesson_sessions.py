from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from app.database.Base import MyDb
from app.model.group_schedules import GroupSchedule
from app.model.groups import Group
from app.model.lesson_sessions import LessonSession, SessionStatus
from app.routers.groups import get_group_user, allowed_branches, check_branch
from app.routers.group_schedules import timetable_group
from app.scheme.lesson_sessions import SessionAdd, SessionUpdate, SessionResponse, SessionStatusUpdate, GenerateSessions
from app.utils.checker import check_ident
from app.utils.timetable import lock_timetable, validate_session

router = APIRouter(tags=["Lesson sessions"], prefix="/lesson-sessions")


async def save_session(db, obj):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Bu guruhning shu sana va vaqtdagi darsi mavjud")
    await db.refresh(obj)
    return obj


@router.get("/", response_model=Page[SessionResponse])
async def list_sessions(db: MyDb, search: str | None = None, branch_id: int | None = None,
                        group_id: int | None = None, teacher_id: int | None = None, room_id: int | None = None,
                        date_from: date | None = None, date_to: date | None = None,
                        status: SessionStatus | None = None, current_user=Depends(get_group_user)):
    if date_from and date_to and date_to < date_from:
        raise HTTPException(422, "Davrning tugashi boshlanishidan oldin bo'la olmaydi")
    query = select(LessonSession).join(Group)
    ids = allowed_branches(current_user)
    if ids is not None:
        query = query.where(Group.branch_id.in_(ids))
    if branch_id is not None:
        check_branch(current_user, branch_id)
        query = query.where(Group.branch_id == branch_id)
    if search:
        query = query.where(or_(Group.name.ilike(f"%{search}%"), LessonSession.topic.ilike(f"%{search}%")))
    for column, value in ((LessonSession.group_id, group_id), (LessonSession.teacher_id, teacher_id),
                           (LessonSession.room_id, room_id), (LessonSession.status, status)):
        if value is not None:
            query = query.where(column == value)
    if date_from:
        query = query.where(LessonSession.date >= date_from)
    if date_to:
        query = query.where(LessonSession.date <= date_to)
    return await apaginate(db, query.order_by(LessonSession.date, LessonSession.start_time, LessonSession.id))


@router.post("/generate")
async def generate_sessions(data: GenerateSessions, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    group = await timetable_group(db, data.group_id, current_user)
    if data.date_from < group.start_date or (group.end_date and data.date_to > group.end_date):
        raise HTTPException(400, "Tanlangan davr guruhning o'qish muddati ichida bo'lishi kerak")
    slots = (await db.execute(select(GroupSchedule).where(GroupSchedule.group_id == group.id).order_by(
        GroupSchedule.weekday, GroupSchedule.start_time).with_for_update())).scalars().all()
    if not slots:
        raise HTTPException(409, "Avval guruhning haftalik jadvalini yarating")
    created, skipped = 0, 0
    day = data.date_from
    while day <= data.date_to:
        for slot in slots:
            if slot.weekday != day.isoweekday():
                continue
            exists = await db.scalar(select(LessonSession.id).where(
                LessonSession.group_id == group.id, LessonSession.date == day, LessonSession.start_time == slot.start_time,
            ).with_for_update())
            if exists is not None:
                skipped += 1
                continue
            lesson = SessionAdd(group_id=group.id, teacher_id=group.teacher_id, room_id=slot.room_id,
                                date=day, start_time=slot.start_time, end_time=slot.end_time)
            await validate_session(db, lesson, group)
            db.add(LessonSession(**lesson.model_dump()))
            await db.flush()
            created += 1
        if day == data.date_to:
            break
        day += timedelta(days=1)
    await db.commit()
    return {"created": created, "skipped": skipped, "msg": f"{created} ta dars yaratildi, {skipped} ta mavjud dars saqlandi"}


@router.post("/", response_model=SessionResponse, status_code=201)
async def add_session(data: SessionAdd, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    group = await timetable_group(db, data.group_id, current_user)
    await validate_session(db, data, group)
    obj = LessonSession(**data.model_dump())
    db.add(obj)
    return await save_session(db, obj)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: MyDb, current_user=Depends(get_group_user)):
    obj = await check_ident(db, LessonSession, session_id)
    check_branch(current_user, obj.group.branch_id)
    return obj


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: int, data: SessionUpdate, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await db.scalar(select(LessonSession).where(LessonSession.id == session_id).with_for_update())
    if obj is None:
        raise HTTPException(404, "Dars topilmadi")
    check_branch(current_user, obj.group.branch_id)
    group = await timetable_group(db, data.group_id, current_user)
    await validate_session(db, data, group, session_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    return await save_session(db, obj)


@router.patch("/{session_id}/status", response_model=SessionResponse)
async def update_session_status(session_id: int, data: SessionStatusUpdate, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await db.scalar(select(LessonSession).where(LessonSession.id == session_id).with_for_update())
    if obj is None:
        raise HTTPException(404, "Dars topilmadi")
    body = SessionUpdate(**{field: getattr(obj, field) for field in SessionAdd.model_fields if field != "status"}, status=data.status)
    return await update_session(session_id, body, db, current_user)


@router.delete("/{session_id}", response_model=SessionResponse)
async def cancel_session(session_id: int, db: MyDb, current_user=Depends(get_group_user)):
    return await update_session_status(session_id, SessionStatusUpdate(status=SessionStatus.bekor_qilingan), db, current_user)
