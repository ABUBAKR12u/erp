from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.enrollments import Enrollment, EnrollmentStatus, OPEN_ENROLLMENTS
from app.model.groups import Group
from app.model.students import Student, StudentStatus
from app.routers.groups import get_group_user, allowed_branches, check_branch
from app.scheme.enrollments import EnrollmentAdd, EnrollmentUpdate, EnrollmentResponse, EnrollmentStatusUpdate
from app.utils.timetable import lock_timetable, ACTIVE_GROUPS, TASHKENT

router = APIRouter(tags=["Enrollments"], prefix="/enrollments")


def today():
    return datetime.now(TASHKENT).date()


async def find_enrollment(db, ident, current_user):
    obj = await db.scalar(select(Enrollment).where(Enrollment.id == ident).with_for_update().execution_options(populate_existing=True))
    if obj is None:
        raise HTTPException(404, "Guruh a'zoligi topilmadi")
    check_branch(current_user, obj.group.branch_id)
    return obj


async def validate_enrollment(db, data, current_user, ident=None):
    group = await db.scalar(select(Group).where(Group.id == data.group_id).with_for_update().execution_options(populate_existing=True))
    if group is None:
        raise HTTPException(404, "Guruh topilmadi")
    check_branch(current_user, group.branch_id)
    student = await db.scalar(select(Student).where(Student.id == data.student_id).with_for_update().execution_options(populate_existing=True))
    if student is None:
        raise HTTPException(404, "O'quvchi topilmadi")
    is_open = data.status in OPEN_ENROLLMENTS
    if (ident is None or is_open) and student.branch_id != group.branch_id:
        raise HTTPException(400, "O'quvchi va guruh bir filialda bo'lishi kerak")
    if data.joined_at > today():
        raise HTTPException(400, "Qo'shilgan sana kelajakda bo'la olmaydi")
    if group.end_date and data.joined_at > group.end_date:
        raise HTTPException(400, "Qo'shilgan sana guruh tugashidan kech bo'la olmaydi")
    if is_open:
        if data.left_at is not None:
            raise HTTPException(400, "Faol yoki muzlatilgan a'zolikda chiqish sanasi bo'lmaydi")
        branch = await db.get(Branch, group.branch_id)
        if group.status not in ACTIVE_GROUPS or not branch.is_active or (group.end_date and group.end_date < today()):
            raise HTTPException(409, "Bu guruhga faol a'zo qo'shib bo'lmaydi")
        if student.status in (StudentStatus.ketgan, StudentStatus.bitirgan):
            raise HTTPException(409, "Avval o'quvchi profilini faol holatga qaytaring")
    else:
        data.left_at = data.left_at or today()
        if data.left_at < data.joined_at or data.left_at > today():
            raise HTTPException(400, "Chiqish sanasi qo'shilgan sana bilan bugun oralig'ida bo'lishi kerak")

    # Tarixiy qayta qabul mumkin, lekin bitta guruhdagi davrlar ustma-ust kelmaydi.
    overlap = select(Enrollment.id).where(
        Enrollment.group_id == group.id, Enrollment.student_id == student.id,
        or_(Enrollment.left_at.is_(None), Enrollment.left_at >= data.joined_at),
    )
    if data.left_at is not None:
        overlap = overlap.where(Enrollment.joined_at <= data.left_at)
    if ident is not None:
        overlap = overlap.where(Enrollment.id != ident)
    if await db.scalar(overlap.with_for_update()) is not None:
        raise HTTPException(409, "O'quvchi shu davrda bu guruhga allaqachon biriktirilgan")

    members = (await db.scalars(select(Enrollment.id).where(
        Enrollment.group_id == group.id, Enrollment.status.in_(OPEN_ENROLLMENTS)
    ).with_for_update())).all()
    count = len([member for member in members if member != ident]) + int(is_open)
    if count > group.max_students:
        raise HTTPException(409, "Guruhda bo'sh joy qolmagan")
    group.current_students = count
    if data.price is None:
        data.price = group.price if group.price is not None else group.course.price
    return data


async def save_enrollment(db, obj):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "A'zolik saqlanmadi. Bog'lanish va sanalarni tekshiring")
    await db.refresh(obj)
    return obj


@router.post("/", response_model=EnrollmentResponse, status_code=201)
async def add_enrollment(body: EnrollmentAdd, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    data = await validate_enrollment(db, body, current_user)
    obj = Enrollment(**data.model_dump())
    db.add(obj)
    return await save_enrollment(db, obj)


@router.get("/", response_model=Page[EnrollmentResponse])
async def get_enrollments(db: MyDb, search: str | None = None, branch_id: int | None = None,
                          student_id: int | None = None, group_id: int | None = None,
                          status: EnrollmentStatus | None = None, current_user=Depends(get_group_user)):
    query = select(Enrollment).join(Group, Enrollment.group_id == Group.id).join(Student, Enrollment.student_id == Student.id)
    ids = allowed_branches(current_user)
    if ids is not None:
        query = query.where(Group.branch_id.in_(ids))
    if branch_id is not None:
        check_branch(current_user, branch_id)
        query = query.where(Group.branch_id == branch_id)
    if group_id is not None:
        query = query.where(Enrollment.group_id == group_id)
    if student_id is not None:
        query = query.where(Enrollment.student_id == student_id)
    if status is not None:
        query = query.where(Enrollment.status == status)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(or_((Student.first_name + " " + Student.last_name).ilike(term),
                                Student.first_name.ilike(term), Student.last_name.ilike(term),
                                Student.phone.ilike(term), Group.name.ilike(term)))
    return await apaginate(db, query.order_by(Enrollment.id.desc()))


@router.get("/{ident}", response_model=EnrollmentResponse)
async def get_enrollment(ident: int, db: MyDb, current_user=Depends(get_group_user)):
    return await find_enrollment(db, ident, current_user)


@router.put("/{ident}", response_model=EnrollmentResponse)
async def update_enrollment(ident: int, body: EnrollmentUpdate, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await find_enrollment(db, ident, current_user)
    changes = body.model_dump(exclude_unset=True)
    values = {field: getattr(obj, field) for field in EnrollmentAdd.model_fields}
    values.update(changes)
    if "status" in changes and "left_at" not in changes and changes["status"] != obj.status:
        values["left_at"] = None if changes["status"] in OPEN_ENROLLMENTS else today()
    data = await validate_enrollment(db, EnrollmentAdd(**values), current_user, obj.id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    return await save_enrollment(db, obj)


@router.patch("/{ident}/status", response_model=EnrollmentResponse)
async def update_enrollment_status(ident: int, body: EnrollmentStatusUpdate, db: MyDb, current_user=Depends(get_group_user)):
    return await update_enrollment(ident, EnrollmentUpdate(status=body.status), db, current_user)


@router.delete("/{ident}", response_model=EnrollmentResponse)
async def leave_group(ident: int, db: MyDb, current_user=Depends(get_group_user)):
    await lock_timetable(db)
    obj = await find_enrollment(db, ident, current_user)
    if obj.status not in OPEN_ENROLLMENTS:
        return obj
    return await update_enrollment(ident, EnrollmentUpdate(status=EnrollmentStatus.ketgan), db, current_user)
