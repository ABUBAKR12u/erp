from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select, or_

from app.model.branches import Branch
from app.model.employees import Employees
from app.model.group_schedules import GroupSchedule
from app.model.groups import Group, GroupStatus
from app.model.lesson_sessions import LessonSession, SessionStatus
from app.model.rooms import Room
from app.model.teacher_profiles import TeacherProfiles
from app.utils.checker import check_ident

ACTIVE_GROUPS = (GroupStatus.rejalashtirilgan, GroupStatus.faol)
TASHKENT = timezone(timedelta(hours=5))


async def lock_timetable(db):
    # Bitta umumiy qulf parallel so'rovlarda ham ikki marta band qilishni to'xtatadi.
    await db.execute(select(Branch.id).order_by(Branch.id).limit(1).with_for_update())


def occurs_on(weekday, start, end):
    return end is None or (end - start).days >= (weekday - start.isoweekday()) % 7


async def validate_resources(db, group, room_id, teacher_id, active=True, profile_required=True):
    room = await db.scalar(select(Room).where(Room.id == room_id).with_for_update().execution_options(populate_existing=True))
    teacher = await db.scalar(select(Employees).where(Employees.id == teacher_id).with_for_update().execution_options(populate_existing=True))
    if room is None or teacher is None:
        raise HTTPException(404, "Xona yoki o'qituvchi topilmadi")
    if room.branch_id != group.branch_id or teacher.branch_id != group.branch_id:
        raise HTTPException(400, "Xona va o'qituvchi guruhning filialiga tegishli bo'lishi kerak")
    if room.capacity < group.max_students:
        raise HTTPException(400, "Xona sig'imi guruhning o'quvchilar chegarasidan kichik")
    if active:
        branch = await check_ident(db, Branch, group.branch_id)
        if group.status not in ACTIVE_GROUPS:
            raise HTTPException(409, "Tugagan yoki bekor qilingan guruhga dars rejalashtirib bo'lmaydi")
        if not branch.is_active or not room.is_active or not teacher.is_active or teacher.fired_at:
            raise HTTPException(400, "Filial, xona va o'qituvchi faol bo'lishi kerak")
    if (active or profile_required) and not await db.get(TeacherProfiles, teacher_id):
        raise HTTPException(400, "Xodimning o'qituvchi profili yo'q")


def conflict_message(other_group, room_id, teacher_id, group_id, other_room, other_teacher):
    resource = "Guruh" if group_id == other_group.id else "Xona" if room_id == other_room else "O'qituvchi"
    return f"{resource} band: {other_group.name} bilan dars vaqti to'qnashmoqda"


async def check_conflicts(db, group, weekday, start_time, end_time, room_id, teacher_id,
                          on_date=None, schedule_id=None, session_id=None):
    schedules = select(GroupSchedule, Group).join(Group, Group.id == GroupSchedule.group_id).where(
        Group.status.in_(ACTIVE_GROUPS), GroupSchedule.weekday == weekday,
        GroupSchedule.start_time < end_time, GroupSchedule.end_time > start_time,
        or_(GroupSchedule.group_id == group.id, GroupSchedule.room_id == room_id, Group.teacher_id == teacher_id),
    )
    if schedule_id is not None:
        schedules = schedules.where(GroupSchedule.id != schedule_id)
    for slot, other in (await db.execute(schedules.with_for_update())).all():
        if on_date:
            if other.id == group.id or on_date < other.start_date or (other.end_date and on_date > other.end_date):
                continue
            # Aynan shu vaqtdagi aniq dars haftalik rejaning shu sanasini almashtiradi.
            actual = await db.scalar(select(LessonSession.id).where(
                LessonSession.group_id == other.id, LessonSession.date == on_date,
                LessonSession.start_time == slot.start_time, LessonSession.end_time == slot.end_time,
            ).with_for_update())
            if actual is not None:
                continue
        else:
            start = max(group.start_date, other.start_date)
            ends = [d for d in (group.end_date, other.end_date) if d is not None]
            end = min(ends) if ends else None
            if not occurs_on(weekday, start, end):
                continue
        raise HTTPException(409, conflict_message(other, room_id, teacher_id, group.id, slot.room_id, other.teacher_id))

    sessions = select(LessonSession, Group).join(Group, Group.id == LessonSession.group_id).where(
        LessonSession.status != SessionStatus.bekor_qilingan,
        LessonSession.start_time < end_time, LessonSession.end_time > start_time,
        or_(LessonSession.group_id == group.id, LessonSession.room_id == room_id, LessonSession.teacher_id == teacher_id),
    )
    if session_id is not None:
        sessions = sessions.where(LessonSession.id != session_id)
    if on_date:
        sessions = sessions.where(LessonSession.date == on_date)
    else:
        sessions = sessions.where(LessonSession.date >= group.start_date)
        if group.end_date:
            sessions = sessions.where(LessonSession.date <= group.end_date)
    for lesson, other in (await db.execute(sessions.with_for_update())).all():
        if not on_date:
            if lesson.date.isoweekday() != weekday:
                continue
            if lesson.group_id == group.id and lesson.start_time == start_time and lesson.end_time == end_time:
                continue
        raise HTTPException(409, conflict_message(other, room_id, teacher_id, group.id, lesson.room_id, lesson.teacher_id))


async def validate_session(db, data, group, session_id=None):
    if data.date < group.start_date or (group.end_date and data.date > group.end_date):
        raise HTTPException(400, "Dars sanasi guruhning o'qish muddati ichida bo'lishi kerak")
    if data.status == SessionStatus.otilgan and datetime.combine(data.date, data.end_time, TASHKENT) > datetime.now(TASHKENT):
        raise HTTPException(400, "Kelajakdagi yoki tugamagan darsni o'tilgan deb belgilab bo'lmaydi")
    old_teacher = None if session_id is None else await db.scalar(select(LessonSession.teacher_id).where(LessonSession.id == session_id).with_for_update())
    await validate_resources(db, group, data.room_id, data.teacher_id,
                             data.status == SessionStatus.rejalashtirilgan, old_teacher != data.teacher_id)
    duplicate = select(LessonSession.id).where(
        LessonSession.group_id == group.id, LessonSession.date == data.date, LessonSession.start_time == data.start_time,
    )
    if session_id is not None:
        duplicate = duplicate.where(LessonSession.id != session_id)
    if await db.scalar(duplicate.with_for_update()) is not None:
        raise HTTPException(409, "Bu guruhning shu sana va vaqtdagi darsi allaqachon mavjud")
    if data.status != SessionStatus.bekor_qilingan:
        await check_conflicts(db, group, data.date.isoweekday(), data.start_time, data.end_time,
                              data.room_id, data.teacher_id, on_date=data.date, session_id=session_id)


async def validate_group_timetable(db, obj, data):
    schedules = (await db.execute(select(GroupSchedule).where(GroupSchedule.group_id == obj.id).with_for_update())).scalars().all()
    lessons = (await db.execute(select(LessonSession).where(LessonSession.group_id == obj.id).with_for_update())).scalars().all()
    if (schedules or lessons) and obj.branch_id != data.branch_id:
        raise HTTPException(409, "Jadvali yoki darslari bor guruhning filialini almashtirib bo'lmaydi")
    live = [lesson for lesson in lessons if lesson.status != SessionStatus.bekor_qilingan]
    if any(lesson.date < data.start_date or (data.end_date and lesson.date > data.end_date) for lesson in live):
        raise HTTPException(409, "Guruh muddati mavjud darslar sanalarini qamrab olishi kerak")
    if data.status not in ACTIVE_GROUPS and any(lesson.status == SessionStatus.rejalashtirilgan for lesson in live):
        raise HTTPException(409, "Avval rejalashtirilgan darslarni o'tilgan yoki bekor qilingan deb belgilang")
    candidate = type("TimetableGroup", (), {**data.model_dump(), "id": obj.id})()
    if data.status in ACTIVE_GROUPS:
        for slot in schedules:
            await validate_resources(db, candidate, slot.room_id, data.teacher_id)
            if not occurs_on(slot.weekday, data.start_date, data.end_date):
                raise HTTPException(409, "Guruh muddati haftalik jadvaldagi kunni qamrab olmaydi")
            # Shu guruhning boshqa slotlari ham tekshiriladi; ular oldindan o'zaro mos.
            await check_conflicts(db, candidate, slot.weekday, slot.start_time, slot.end_time,
                                  slot.room_id, data.teacher_id, schedule_id=slot.id)
    for lesson in live:
        room = await check_ident(db, Room, lesson.room_id)
        if room.capacity < data.max_students:
            raise HTTPException(409, "Guruh chegarasi mavjud dars xonasi sig'imidan oshadi")


async def validate_room_timetable(db, room_id, branch_id, capacity, active):
    scheduled = (await db.execute(select(Group).join(GroupSchedule).where(GroupSchedule.room_id == room_id).with_for_update())).scalars().all()
    lessons = (await db.execute(select(LessonSession, Group).join(Group).where(LessonSession.room_id == room_id).with_for_update())).all()
    groups = scheduled + [group for _, group in lessons]
    if any(group.branch_id != branch_id for group in groups):
        raise HTTPException(409, "Jadvali yoki darslari bor xonaning filialini almashtirib bo'lmaydi")
    if any(group.max_students > capacity for group in groups):
        raise HTTPException(409, "Xona sig'imi jadvaldagi guruhlar chegarasidan kichik")
    if not active and (any(group.status in ACTIVE_GROUPS for group in scheduled) or any(lesson.status == SessionStatus.rejalashtirilgan for lesson, _ in lessons)):
        raise HTTPException(409, "Avval xonaning haftalik jadvali va rejalashtirilgan darslarini boshqa xonaga o'tkazing")


async def protect_teacher_timetable(db, teacher_id, branch_id=None):
    weekly = (await db.execute(select(Group).join(GroupSchedule).where(Group.teacher_id == teacher_id).with_for_update())).scalars().all()
    lessons = (await db.execute(select(LessonSession, Group).join(Group).where(LessonSession.teacher_id == teacher_id).with_for_update())).all()
    if branch_id is not None:
        if any(group.branch_id != branch_id for group in weekly) or any(group.branch_id != branch_id for _, group in lessons):
            raise HTTPException(409, "Jadvali yoki darslari bor o'qituvchining filialini almashtirib bo'lmaydi")
    elif any(group.status in ACTIVE_GROUPS for group in weekly) or any(lesson.status == SessionStatus.rejalashtirilgan for lesson, _ in lessons):
        raise HTTPException(409, "Avval o'qituvchining haftalik jadvali va rejalashtirilgan darslarini boshqa ustozga o'tkazing")
