import enum
import itertools
from datetime import date, datetime

import pytest
import pytest_asyncio
from sqlalchemy import select, update
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, Integer, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.model.branches import Branch
from app.model.students import Student, StudentStatus
from app.scheme.students import StudentAdd

pytestmark = pytest.mark.asyncio

URL = "/students/"


# ----------------------------------------------------------------------
# Yordamchi fixture va funksiyalar
# ----------------------------------------------------------------------
@pytest_asyncio.fixture
async def session_maker(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


_branch_counter = itertools.count(1)


def _fake_value(col, n: int):
    """Majburiy (NOT NULL) ustun uchun turiga qarab avtomatik qiymat tanlaydi."""
    t = col.type
    if isinstance(t, SAEnum):
        return t.enums[0] if t.enums else None
    if isinstance(t, Boolean):
        return True
    if isinstance(t, Integer):
        return n
    if isinstance(t, (Numeric, Float)):
        return 1
    if isinstance(t, DateTime):
        return datetime.now()
    if isinstance(t, Date):
        return date.today()
    if isinstance(t, JSON):
        return {}
    # String / Text / boshqa matnli turlar
    value = f"{col.name}-{n}"
    length = getattr(t, "length", None)
    return value[:length] if length else value


async def create_branch(session_maker, **overrides) -> Branch:
    """Branch modelidagi barcha majburiy ustunlarni o'zi to'ldirib filial yaratadi.
    Kerak bo'lsa overrides orqali qiymatni o'zingiz bera olasiz."""
    n = next(_branch_counter)
    data = {}
    for col in Branch.__table__.columns:
        if col.primary_key or col.nullable:
            continue
        if col.default is not None or col.server_default is not None:
            continue
        if col.foreign_keys:
            raise RuntimeError(
                f"Branch.{col.name} boshqa jadvalga bog'langan — create_branch ni moslang"
            )
        data[col.name] = _fake_value(col, n)
    data.update(overrides)

    async with session_maker() as s:
        obj = Branch(**data)
        s.add(obj)
        await s.commit()
        return obj


@pytest_asyncio.fixture
async def branch(session_maker):
    return await create_branch(session_maker)


@pytest_asyncio.fixture
async def branch2(session_maker):
    return await create_branch(session_maker)


def make_payload(branch_id: int, **overrides) -> dict:
    data = {
        "first_name": "Ali",
        "last_name": "Valiyev",
        "phone": "+998901234567",
        "parent_phone": "+998909999999",
        "branch_id": branch_id,
    }
    data.update(overrides)

    # StudentAdd dagi yana boshqa majburiy maydonlar bo'lsa, ularni turiga qarab o'zi to'ldiradi
    for name, field in StudentAdd.model_fields.items():
        if field.is_required() and name not in data:
            ann = field.annotation
            if ann is int:
                data[name] = 1
            elif ann is float:
                data[name] = 1.0
            elif ann is bool:
                data[name] = True
            elif ann is date:
                data[name] = date.today().isoformat()
            elif isinstance(ann, type) and issubclass(ann, enum.Enum):
                data[name] = list(ann)[0].value
            else:
                data[name] = f"{name}-test"
    return data


async def create_student(client, branch_id: int, **overrides) -> int:
    resp = await client.post(URL, json=make_payload(branch_id, **overrides))
    assert resp.status_code == 200, resp.text
    listing = await client.get(URL, params={"phone": make_payload(branch_id, **overrides)["phone"]})
    return listing.json()["items"][0]["id"]


async def set_balance(session_maker, student_id: int, balance: float):
    async with session_maker() as s:
        await s.execute(update(Student).where(Student.id == student_id).values(balance=balance))
        await s.commit()


# ----------------------------------------------------------------------
# POST /students/
# ----------------------------------------------------------------------
async def test_add_student_success(client, branch, session_maker):
    resp = await client.post(URL, json=make_payload(branch.id))
    assert resp.status_code == 200
    assert resp.json() == {"msg": "Student created successfully"}

    async with session_maker() as s:
        res = await s.execute(select(Student).where(Student.phone == "+998901234567"))
        assert res.scalars().first() is not None


async def test_add_student_duplicate_phone(client, branch):
    await client.post(URL, json=make_payload(branch.id))
    resp = await client.post(URL, json=make_payload(branch.id, first_name="Vali"))
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already exists"


async def test_add_student_invalid_branch(client):
    resp = await client.post(URL, json=make_payload(branch_id=9999))
    # check_ident qaysi kodni qaytarishiga qarab (404, 400 yoki 422)
    assert resp.status_code in (400, 404, 422)


async def test_add_student_validation_error(client, branch):
    resp = await client.post(URL, json={"first_name": "Ali"})
    assert resp.status_code == 422


# ----------------------------------------------------------------------
# GET /students/
# ----------------------------------------------------------------------
async def test_get_students_empty(client):
    resp = await client.get(URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


async def test_get_students_list_and_order(client, branch):
    id1 = await create_student(client, branch.id, phone="+998900000001")
    id2 = await create_student(client, branch.id, phone="+998900000002")

    resp = await client.get(URL)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert [i["id"] for i in items] == [id2, id1]  # id bo'yicha kamayish tartibida


async def test_get_students_pagination(client, branch):
    for i in range(3):
        await create_student(client, branch.id, phone=f"+99890000010{i}")

    resp = await client.get(URL, params={"page": 1, "size": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total"] == 3


async def test_search_by_first_name_last_name_phone(client, branch):
    await create_student(client, branch.id, first_name="Jasur", last_name="Karimov", phone="+998911111111")
    await create_student(client, branch.id, first_name="Dilnoza", last_name="Aliyeva", phone="+998922222222")

    for q, expected in [("jasur", "+998911111111"), ("aliyeva", "+998922222222"), ("2222", "+998922222222")]:
        resp = await client.get(URL, params={"search": q})
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["phone"] == expected


async def test_search_ignores_separate_filters(client, branch):
    await create_student(client, branch.id, first_name="Jasur", phone="+998911111111")
    await create_student(client, branch.id, first_name="Dilnoza", phone="+998922222222")

    # search berilsa first_name e'tiborga olinmaydi
    resp = await client.get(URL, params={"search": "jasur", "first_name": "Dilnoza"})
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["first_name"] == "Jasur"


async def test_filter_first_last_phone(client, branch):
    await create_student(client, branch.id, first_name="Jasur", last_name="Karimov", phone="+998911111111")
    await create_student(client, branch.id, first_name="Dilnoza", last_name="Aliyeva", phone="+998922222222")

    assert len((await client.get(URL, params={"first_name": "dil"})).json()["items"]) == 1
    assert len((await client.get(URL, params={"last_name": "karim"})).json()["items"]) == 1
    assert len((await client.get(URL, params={"phone": "9222"})).json()["items"]) == 1
    assert len((await client.get(URL, params={"first_name": "Jasur", "last_name": "Aliyeva"})).json()["items"]) == 0


async def test_filter_by_branch(client, branch, branch2):
    await create_student(client, branch.id, phone="+998900000001")
    await create_student(client, branch2.id, phone="+998900000002")

    resp = await client.get(URL, params={"branch_id": branch2.id})
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["phone"] == "+998900000002"


async def test_filter_by_status(client, branch):
    sid = await create_student(client, branch.id, phone="+998900000001")
    await create_student(client, branch.id, phone="+998900000002")
    await client.delete(f"/students/{sid}")

    resp = await client.get(URL, params={"status": StudentStatus.ketgan.value})
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == sid


async def test_filter_by_dates(client, branch):
    await create_student(client, branch.id)

    # bugungi sana oralig'ida topiladi
    from datetime import date, timedelta
    today = date.today()
    resp = await client.get(
        URL,
        params={
            "start_date": (today - timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=1)).isoformat(),
        },
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1

    # kelajakdagi start_date -> hech narsa topilmaydi
    resp = await client.get(URL, params={"start_date": (today + timedelta(days=5)).isoformat()})
    assert resp.json()["items"] == []


async def test_start_date_greater_than_end_date(client):
    resp = await client.get(URL, params={"start_date": "2026-10-20", "end_date": "2026-10-01"})
    assert resp.status_code == 400


async def test_filter_by_balance(client, branch, session_maker):
    id1 = await create_student(client, branch.id, phone="+998900000001")
    id2 = await create_student(client, branch.id, phone="+998900000002")
    id3 = await create_student(client, branch.id, phone="+998900000003")
    await set_balance(session_maker, id1, 100)
    await set_balance(session_maker, id2, 500)
    await set_balance(session_maker, id3, 1000)

    resp = await client.get(URL, params={"min_balance": 200, "max_balance": 800})
    assert [i["id"] for i in resp.json()["items"]] == [id2]

    resp = await client.get(URL, params={"min_balance": 500})
    assert {i["id"] for i in resp.json()["items"]} == {id2, id3}

    resp = await client.get(URL, params={"max_balance": 100})
    assert [i["id"] for i in resp.json()["items"]] == [id1]


async def test_min_balance_greater_than_max_balance(client):
    resp = await client.get(URL, params={"min_balance": 500, "max_balance": 100})
    assert resp.status_code == 400


async def test_invalid_status_value(client):
    resp = await client.get(URL, params={"status": "no_such_status"})
    assert resp.status_code == 422


# ----------------------------------------------------------------------
# PUT /students/{id}
# ----------------------------------------------------------------------
async def test_update_student_success(client, branch):
    sid = await create_student(client, branch.id)

    resp = await client.put(f"/students/{sid}", json={"first_name": "Yangi"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": "Student updated successfully"}

    items = (await client.get(URL)).json()["items"]
    assert items[0]["first_name"] == "Yangi"
    assert items[0]["last_name"] == "Valiyev"  # o'zgarmagan (exclude_unset)


async def test_update_student_not_found(client):
    resp = await client.put("/students/9999", json={"first_name": "X"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Student not found"


async def test_update_student_duplicate_phone(client, branch):
    await create_student(client, branch.id, phone="+998900000001")
    sid2 = await create_student(client, branch.id, phone="+998900000002")

    resp = await client.put(f"/students/{sid2}", json={"phone": "+998900000001"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already exists"


async def test_update_student_same_phone_allowed(client, branch):
    sid = await create_student(client, branch.id, phone="+998900000001")
    resp = await client.put(f"/students/{sid}", json={"phone": "+998900000001", "first_name": "Boshqa"})
    assert resp.status_code == 200


async def test_update_student_invalid_branch(client, branch):
    sid = await create_student(client, branch.id)
    resp = await client.put(f"/students/{sid}", json={"branch_id": 9999})
    assert resp.status_code in (400, 404, 422)


async def test_update_student_change_branch(client, branch, branch2):
    sid = await create_student(client, branch.id)
    resp = await client.put(f"/students/{sid}", json={"branch_id": branch2.id})
    assert resp.status_code == 200

    items = (await client.get(URL, params={"branch_id": branch2.id})).json()["items"]
    assert [i["id"] for i in items] == [sid]


# ----------------------------------------------------------------------
# PATCH /students/{id}/status
# ----------------------------------------------------------------------
async def test_update_student_status_success(client, branch, session_maker):
    sid = await create_student(client, branch.id)
    new_status = StudentStatus.ketgan

    resp = await client.patch(f"/students/{sid}/status", json={"status": new_status.value})
    assert resp.status_code == 200
    assert resp.json() == {"msg": "Student status updated successfully"}

    async with session_maker() as s:
        obj = await s.get(Student, sid)
        assert obj.status == new_status


async def test_update_student_status_not_found(client):
    resp = await client.patch("/students/9999/status", json={"status": list(StudentStatus)[0].value})
    assert resp.status_code == 404


async def test_update_student_status_invalid_value(client, branch):
    sid = await create_student(client, branch.id)
    resp = await client.patch(f"/students/{sid}/status", json={"status": "noto'g'ri"})
    assert resp.status_code == 422


# ----------------------------------------------------------------------
# DELETE /students/{id}
# ----------------------------------------------------------------------
async def test_delete_student_marks_as_left(client, branch, session_maker):
    sid = await create_student(client, branch.id)

    resp = await client.delete(f"/students/{sid}")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "Student marked as left"}

    async with session_maker() as s:
        obj = await s.get(Student, sid)
        assert obj is not None  # soft delete: qator o'chmaydi
        assert obj.status == StudentStatus.ketgan


async def test_delete_student_not_found(client):
    resp = await client.delete("/students/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Student not found"