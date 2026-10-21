from fastapi import APIRouter, HTTPException
from fastapi_pagination import Page
from sqlalchemy import select, or_, and_
from fastapi_pagination.ext.sqlalchemy import apaginate
from app.database.Base import MyDb
from datetime import date
from app.model.branches import Branch
from app.model.students import Student, StudentStatus
from app.scheme.students import StudentAdd, StudentResponse, StudentUpdate, StudentStatusUpdate
from app.utils.checker import check_ident

router = APIRouter(tags=["Students"] , prefix="/students")


@router.post("/")
async def add_student(student: StudentAdd, db: MyDb):
    await check_ident(db, Branch, student.branch_id)
    find = await db.execute(select(Student).where(Student.phone == student.phone))
    result = find.scalars().first()
    if result:
        raise HTTPException(400, "Student already exists")

    obj = Student(**student.model_dump())

    db.add(obj)
    await db.commit()

    return {"msg": "Student created successfully"}

@router.get("/", response_model=Page[StudentResponse])
async def get_students(
    db: MyDb,
    search: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    branch_id: int | None = None,
    status: StudentStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_balance: float | None = None,
    max_balance: float | None = None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date end_date dan katta bo'la olmaydi")

    if min_balance is not None and max_balance is not None and min_balance > max_balance:
        raise HTTPException(400, "min_balance max_balance dan katta bo'la olmaydi")

    query = select(Student)
    conditions = []

    if search:
        conditions.append(
            or_(
                Student.first_name.ilike(f"%{search}%"),
                Student.last_name.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%"),
            )
        )
    else:
        if first_name:
            conditions.append(Student.first_name.ilike(f"%{first_name}%"))
        if last_name:
            conditions.append(Student.last_name.ilike(f"%{last_name}%"))
        if phone:
            conditions.append(Student.phone.ilike(f"%{phone}%"))

    if branch_id is not None:
        conditions.append(Student.branch_id == branch_id)
    if status:
        conditions.append(Student.status == status)
    if start_date:
        conditions.append(Student.created_at >= start_date)
    if end_date:
        conditions.append(Student.created_at <= end_date)
    if min_balance is not None:
        conditions.append(Student.balance >= min_balance)
    if max_balance is not None:
        conditions.append(Student.balance <= max_balance)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Student.id.desc())
    return await apaginate(db, query)


@router.put("/{student_id}")
async def update_student(student_id: int, student: StudentUpdate, db: MyDb):
    obj = await db.get(Student, student_id)
    if not obj:
        raise HTTPException(404, "Student not found")
    update_data = student.model_dump(exclude_unset=True)
    if "branch_id" in update_data:
        await check_ident(db, Branch, update_data["branch_id"])

    if "phone" in update_data and update_data["phone"] != obj.phone:
        find = await db.execute(
            select(Student).where(
                Student.phone == update_data["phone"],
                Student.id != student_id,
            )
        )
        if find.scalars().first():
            raise HTTPException(400, "Student already exists")
    for field, value in update_data.items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return {"msg": "Student updated successfully"}

@router.patch("/{student_id}/status")
async def update_student_status(student_id: int, payload: StudentStatusUpdate, db: MyDb):
    obj = await db.get(Student, student_id)
    if not obj:
        raise HTTPException(404, "Student not found")

    obj.status = payload.status
    await db.commit()

    return {"msg": "Student status updated successfully"}

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: MyDb):
    obj = await db.get(Student, student_id)
    if not obj:
        raise HTTPException(404, "Student not found")

    obj.status = StudentStatus.ketgan
    await db.commit()
    return {"msg": "Student marked as left"}