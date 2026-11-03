from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from pydantic import ValidationError
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.courses import Course
from app.model.employees import Employees
from app.model.groups import Group, GroupStatus
from app.model.rooms import Room
from app.model.teacher_profiles import TeacherProfiles
from app.scheme.groups import GroupAdd, GroupUpdate, GroupResponse, GroupStatusUpdate, GroupOptions
from app.utils.checker import check_ident, normalize_name
from app.utils.security import require_role

router = APIRouter(tags=["Groups"], prefix="/groups")


async def get_group_user(current_user=Depends(require_role("admin", "boss"))):
    if not current_user.is_active or current_user.fired_at is not None:
        raise HTTPException(403, "Xodim faol emas")
    return current_user


def allowed_branches(current_user):
    if current_user.is_superadmin:
        return None
    roles = [er for er in current_user.employee_role if er.role.code in ("admin", "boss")]
    if any(er.branch_id is None for er in roles):
        return None
    return {er.branch_id for er in roles}


def check_branch(current_user, branch_id):
    branches = allowed_branches(current_user)
    if branches is not None and branch_id not in branches:
        raise HTTPException(403, "Bu filialga ruxsatingiz yo'q")


async def validate_group(db, data, current_user, group_id=None, current_students=0):
    check_branch(current_user, data.branch_id)
    branch = await check_ident(db, Branch, data.branch_id)
    course = await check_ident(db, Course, data.course_id)
    room = await check_ident(db, Room, data.room_id)
    teacher = (await db.execute(
        select(Employees).where(Employees.id == data.teacher_id).with_for_update()
    )).scalars().first()
    if not teacher:
        raise HTTPException(404, "O'qituvchi topilmadi")
    profile = await db.get(TeacherProfiles, data.teacher_id)
    if room.branch_id != data.branch_id:
        raise HTTPException(400, "Xona tanlangan filialga tegishli emas")
    if data.max_students > room.capacity:
        raise HTTPException(400, "O'quvchilar chegarasi xona sig'imidan oshmasligi kerak")
    if data.max_students < current_students:
        raise HTTPException(400, "Chegara hozirgi o'quvchilar sonidan kam bo'la olmaydi")
    if data.status == GroupStatus.bekor_qilingan and current_students:
        raise HTTPException(409, "Avval guruhdagi o'quvchilarni boshqa guruhga o'tkazing")

    if data.status in (GroupStatus.rejalashtirilgan, GroupStatus.faol):
        if not profile:
            raise HTTPException(400, "Xodimning o'qituvchi profili yo'q")
        if teacher.branch_id != data.branch_id:
            raise HTTPException(400, "O'qituvchi tanlangan filialga tegishli emas")
        if not branch.is_active or not course.is_active or not room.is_active:
            raise HTTPException(400, "Filial, kurs va xona faol bo'lishi kerak")
        if not teacher.is_active or teacher.fired_at is not None:
            raise HTTPException(400, "O'qituvchi faol emas")
        if profile.max_groups is not None:
            query = select(func.count(Group.id)).where(
                Group.teacher_id == data.teacher_id,
                Group.status.in_((GroupStatus.rejalashtirilgan, GroupStatus.faol)),
            )
            if group_id is not None:
                query = query.where(Group.id != group_id)
            if await db.scalar(query) >= profile.max_groups:
                raise HTTPException(400, "O'qituvchining guruhlar chegarasi to'lgan")

    data.name = normalize_name(data.name)
    if not data.name:
        raise HTTPException(422, "Guruh nomini kiriting")
    query = select(Group.id).where(
        Group.branch_id == data.branch_id,
        func.lower(Group.name) == data.name.lower(),
    )
    if group_id is not None:
        query = query.where(Group.id != group_id)
    if await db.scalar(query) is not None:
        raise HTTPException(409, "Bu filialda shu nomli guruh mavjud")


async def save_group(db, obj):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Guruh ma'lumotlari saqlanmadi, bog'lanish va nomni tekshiring")
    await db.refresh(obj)
    return obj


@router.get("/options", response_model=GroupOptions)
async def get_group_options(db: MyDb, current_user=Depends(get_group_user)):
    branches = select(Branch).where(Branch.is_active == True).order_by(Branch.name)
    rooms = select(Room).where(Room.is_active == True).order_by(Room.name)
    teachers = select(Employees).join(TeacherProfiles).where(
        Employees.is_active == True, Employees.fired_at.is_(None)
    ).order_by(Employees.first_name)
    ids = allowed_branches(current_user)
    if ids is not None:
        branches = branches.where(Branch.id.in_(ids))
        rooms = rooms.where(Room.branch_id.in_(ids))
        teachers = teachers.where(Employees.branch_id.in_(ids))
    return {
        "user": {"id": current_user.id, "name": f"{current_user.first_name} {current_user.last_name}"},
        "branches": (await db.execute(branches)).scalars().all(),
        "courses": (await db.execute(select(Course).where(Course.is_active == True).order_by(Course.name))).scalars().all(),
        "teachers": (await db.execute(teachers)).scalars().all(),
        "rooms": (await db.execute(rooms)).scalars().all(),
    }


@router.post("/", response_model=GroupResponse, status_code=201)
async def add_group(group: GroupAdd, db: MyDb, current_user=Depends(get_group_user)):
    await validate_group(db, group, current_user)
    obj = Group(**group.model_dump())
    db.add(obj)
    return await save_group(db, obj)


@router.get("/", response_model=Page[GroupResponse])
async def get_groups(
    db: MyDb,
    search: str | None = None,
    branch_id: int | None = None,
    course_id: int | None = None,
    teacher_id: int | None = None,
    status: GroupStatus | None = None,
    current_user=Depends(get_group_user),
):
    query = select(Group)
    ids = allowed_branches(current_user)
    if ids is not None:
        query = query.where(Group.branch_id.in_(ids))
    if search:
        query = query.where(Group.name.ilike(f"%{search}%"))
    if branch_id is not None:
        check_branch(current_user, branch_id)
        query = query.where(Group.branch_id == branch_id)
    if course_id is not None:
        query = query.where(Group.course_id == course_id)
    if teacher_id is not None:
        query = query.where(Group.teacher_id == teacher_id)
    if status is not None:
        query = query.where(Group.status == status)
    return await apaginate(db, query.order_by(Group.id.desc()))


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: MyDb, current_user=Depends(get_group_user)):
    obj = await check_ident(db, Group, group_id)
    check_branch(current_user, obj.branch_id)
    return obj


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, group: GroupUpdate, db: MyDb, current_user=Depends(get_group_user)):
    obj = await check_ident(db, Group, group_id)
    check_branch(current_user, obj.branch_id)
    update_data = group.model_dump(exclude_unset=True)
    if obj.current_students and any(
        field in update_data and update_data[field] != getattr(obj, field)
        for field in ("branch_id", "course_id")
    ):
        raise HTTPException(409, "O'quvchilari bor guruhning filiali yoki kursini o'zgartirib bo'lmaydi")
    data = {field: getattr(obj, field) for field in GroupAdd.model_fields}
    data.update(update_data)
    try:
        data = GroupAdd(**data)
    except ValidationError as exc:
        raise HTTPException(422, jsonable_encoder(exc.errors(include_context=False)))
    await validate_group(db, data, current_user, group_id, obj.current_students)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    return await save_group(db, obj)


@router.patch("/{group_id}/status", response_model=GroupResponse)
async def update_group_status(group_id: int, body: GroupStatusUpdate, db: MyDb, current_user=Depends(get_group_user)):
    return await update_group(group_id, GroupUpdate(status=body.status), db, current_user)


@router.delete("/{group_id}")
async def delete_group(group_id: int, db: MyDb, current_user=Depends(get_group_user)):
    await update_group(group_id, GroupUpdate(status=GroupStatus.bekor_qilingan), db, current_user)
    return {"msg": "Guruh bekor qilindi, tarixi saqlandi"}
