from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database.Base import MyDb
from app.model.employees import Employees
from app.model.teacher_profiles import TeacherProfiles
from app.scheme.teacher_profiles import (
    TeacherProfilesAdd,
    TeacherProfilesUpdate,
    TeacherProfilesResponse,
)
from app.utils.checker import check_ident
from app.utils.security import require_role, get_current_user  # get_current_user qo'shildi
# from app.utils.common import check_ident
# from app.database import MyDb

router = APIRouter(prefix="/teacher-profiles", tags=["Teacher profiles"])


async def _load_profile(db, employee_id: int):
    stmt = (
        select(TeacherProfiles)
        .where(TeacherProfiles.employee_id == employee_id)
        .options(selectinload(TeacherProfiles.employee))
    )
    profile = (await db.execute(stmt)).scalars().first()
    if not profile:
        raise HTTPException(404, "Teacher profile topilmadi")
    return profile


@router.get("/", response_model=List[TeacherProfilesResponse])
async def list_teacher_profiles(
    db: MyDb,
    current_user=Depends(require_role("admin")),
    specialization: str | None = None,
):
    stmt = select(TeacherProfiles).options(selectinload(TeacherProfiles.employee))
    if specialization:
        stmt = stmt.where(TeacherProfiles.specialization.ilike(f"%{specialization}%"))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/me", response_model=TeacherProfilesResponse)
async def my_teacher_profile(
    db: MyDb,
    current_user=Depends(get_current_user),
):
    return await _load_profile(db, current_user.id)


@router.get("/{employee_id}", response_model=TeacherProfilesResponse)
async def get_teacher_profile(
    employee_id: int,
    db: MyDb,
    current_user=Depends(require_role("admin")),
):
    return await _load_profile(db, employee_id)


@router.post("/", response_model=TeacherProfilesResponse, status_code=201)
async def add_teacher_profile(
    data: TeacherProfilesAdd,
    db: MyDb,
    current_user=Depends(require_role("admin","boss")),
):
    await check_ident(db, Employees, data.employee_id)

    if await db.get(TeacherProfiles, data.employee_id):
        raise HTTPException(409, "Bu xodimda profil allaqachon bor")

    db.add(TeacherProfiles(**data.model_dump()))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Bu xodimda profil allaqachon bor")

    return await _load_profile(db, data.employee_id)


@router.put("/{employee_id}", response_model=TeacherProfilesResponse)
async def update_teacher_profile(
    employee_id: int,
    data: TeacherProfilesUpdate,
    db: MyDb,
    current_user=Depends(require_role("admin", "boss")),
):
    profile = await db.get(TeacherProfiles, employee_id)
    if not profile:
        raise HTTPException(404, "Teacher profile topilmadi")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    await db.commit()
    return await _load_profile(db, employee_id)


@router.delete("/{employee_id}")
async def delete_teacher_profile(
    employee_id: int,
    db: MyDb,
    current_user=Depends(require_role("admin","boss")),
):
    profile = await db.get(TeacherProfiles, employee_id)
    if not profile:
        raise HTTPException(404, "Teacher profile topilmadi")

    await db.delete(profile)
    await db.commit()
    return {"msg": "teacher profile deleted"}