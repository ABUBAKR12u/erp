from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.database.Base import MyDb
from app.model.courses import Course
from app.scheme.courses import CourseAdd, CourseResponse, CourseUpdate
from app.utils.checker import check_ident, normalize_name

router = APIRouter(tags=["courses"] , prefix="/courses")


@router.post("/")
async def add_course(course: CourseAdd , db:MyDb):
    name = normalize_name(course.name)
    find = await db.execute(select(Course).where(
        func.lower(Course.name) == name.lower()
    ))
    result = find.scalars().first()
    if result:
        raise HTTPException(status_code=400, detail="Course already exists")


    obj = Course(
        **course.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"message": "Course Added"}



@router.get("/", response_model=List[CourseResponse])
async def get_courses(db: MyDb, course_name: str = None, is_active: bool = None):
    query = select(Course)
    if course_name:
        query = query.where(Course.name.ilike(f"%{course_name}%"))
    if is_active is not None:
        query = query.where(Course.is_active == is_active)
    find = await db.execute(query)
    return find.scalars().all()

@router.put("/{course_id}")
async def put_course(course_id: int, courses: CourseUpdate, db: MyDb):
    find = await db.execute(select(Course).where(Course.id == course_id))
    result = find.scalars().first()
    if not result:
        raise HTTPException(404, "Course not found")

    for field, value in courses.model_dump(exclude_unset=True).items():
        setattr(result, field, value)

    await db.commit()
    return {"message": "Course Updated"}


@router.patch("/{course_id}")
async def patch_course_status(course_id: int, body:bool, db: MyDb):
    db_course = await db.get(Course, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    db_course.is_active = body

    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return {"msg": "Course Updated"}


@router.delete("/{course_id}")
async def delete_course(course_id: int, db: MyDb):
    db_course =await check_ident(db , Course , course_id)

    await db.delete(db_course)
    await db.commit()

    return {"message": "Course deleted successfully"}