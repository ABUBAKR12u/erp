from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database.Base import Base
from app.database.connation import get_db
from app.model.branches import Branch
from app.model.courses import Course
from app.model.employee_roles import EmployeeRole
from app.model.employees import Employees
from app.model.groups import Group
from app.model.roles import Roles
from app.model.rooms import Room
from app.model.teacher_profiles import TeacherProfiles
from app.utils.security import create_access_token

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def group_data():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as db:
        for ident in (1, 2):
            db.add(Branch(id=ident, name=f"Filial {ident}", code=f"BR{ident}", address="Test", phone=f"00{ident}", city="Toshkent", opened_at=date(2026, 1, 1)))
            db.add(Room(id=ident, branch_id=ident, name=f"Xona {ident}", capacity=12))
        db.add(Course(id=1, name="Python", price=Decimal("750000")))
        db.add(Course(id=2, name="English", price=Decimal("500000")))
        for ident, code in ((1, "boss"), (2, "admin"), (3, "teacher")):
            db.add(Roles(id=ident, code=code, name=code))
        for ident in range(1, 7):
            db.add(Employees(id=ident, branch_id=2 if ident == 3 else 1, first_name=f"Xodim {ident}", last_name="Test", phone=f"+99890000000{ident}", password="test-only", birth_date=date(1995, 1, 1), photo_url="", position="Test", hired_at=date(2026, 1, 1), is_active=ident != 6))
        await db.commit()
        db.add_all([
            EmployeeRole(employee_id=1, role_id=1, branch_id=None),
            EmployeeRole(employee_id=4, role_id=2, branch_id=1),
            EmployeeRole(employee_id=2, role_id=3, branch_id=1),
            EmployeeRole(employee_id=6, role_id=2, branch_id=1),
            TeacherProfiles(employee_id=2, max_groups=2),
            TeacherProfiles(employee_id=3, max_groups=2),
        ])
        await db.commit()
    yield sessions
    await engine.dispose()


@pytest_asyncio.fixture
async def group_client(group_data):
    async def test_db():
        async with group_data() as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = test_db
    token = await create_access_token(1)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as client:
        yield client
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def payload(**overrides):
    return dict(branch_id=1, course_id=1, name="PY-26-01", teacher_id=2, room_id=1,
                start_date="2026-11-03", max_students=12) | overrides


async def test_create_and_price_fallback(group_client):
    response = await group_client.post("/groups/", json=payload(name="  PY-26-01  "))
    assert response.status_code == 201, response.text
    group = response.json()
    assert group["name"] == "PY-26-01"
    assert group["status"] == "rejalashtirilgan"
    assert group["current_students"] == 0
    assert group["price"] is None
    assert Decimal(group["effective_price"]) == Decimal("750000")
    assert group["teacher"]["id"] == 2


@pytest.mark.parametrize("changes, expected", [
    ({"max_students": 13}, 400),
    ({"max_students": 0}, 422),
    ({"max_students": 32768}, 422),
    ({"room_id": 2}, 400),
    ({"teacher_id": 3}, 400),
    ({"teacher_id": 5}, 400),
    ({"course_id": 999}, 404),
    ({"end_date": "2026-11-02"}, 422),
    ({"price": "-1"}, 422),
    ({"name": "   "}, 422),
    ({"current_students": 1}, 422),
])
async def test_invalid_group(group_client, changes, expected):
    response = await group_client.post("/groups/", json=payload(**changes))
    assert response.status_code == expected, response.text


async def test_duplicate_and_teacher_limit(group_client):
    assert (await group_client.post("/groups/", json=payload())).status_code == 201
    assert (await group_client.post("/groups/", json=payload(name="py-26-01"))).status_code == 409
    assert (await group_client.post("/groups/", json=payload(name="PY-26-02"))).status_code == 201
    response = await group_client.post("/groups/", json=payload(name="PY-26-03"))
    assert response.status_code == 400
    assert "chegarasi" in response.json()["detail"]


async def test_update_relations_and_free_price(group_client):
    group = (await group_client.post("/groups/", json=payload())).json()
    response = await group_client.put(f"/groups/{group['id']}", json={"course_id": 2, "price": "0"})
    assert response.status_code == 200, response.text
    assert response.json()["course"]["name"] == "English"
    assert Decimal(response.json()["effective_price"]) == 0
    response = await group_client.put(f"/groups/{group['id']}", json={"price": None})
    assert Decimal(response.json()["effective_price"]) == Decimal("500000")


async def test_invalid_partial_update_has_json_error(group_client):
    group = (await group_client.post("/groups/", json=payload(end_date="2026-12-01"))).json()
    response = await group_client.put(f"/groups/{group['id']}", json={"start_date": "2027-01-01"})
    assert response.status_code == 422, response.text
    assert isinstance(response.json()["detail"], list)
    response = await group_client.put(f"/groups/{group['id']}", json={"name": None})
    assert response.status_code == 422


async def test_list_filters_pagination_and_status(group_client):
    group = (await group_client.post("/groups/", json=payload())).json()
    await group_client.post("/groups/", json=payload(branch_id=2, room_id=2, teacher_id=3, name="EN-01"))
    response = await group_client.get("/groups/", params={"size": 1, "page": 2})
    assert response.status_code == 200, response.text
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    response = await group_client.patch(f"/groups/{group['id']}/status", json={"status": "faol"})
    assert response.status_code == 200, response.text
    response = await group_client.get("/groups/", params={"search": "PY-26", "status": "faol", "branch_id": 1, "course_id": 1, "teacher_id": 2})
    assert response.json()["total"] == 1


async def test_cancel_preserves_history(group_client):
    group = (await group_client.post("/groups/", json=payload())).json()
    assert (await group_client.delete(f"/groups/{group['id']}")).status_code == 200
    response = await group_client.get(f"/groups/{group['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "bekor_qilingan"


async def test_course_with_groups_cannot_be_deleted(group_client):
    group = await group_client.post("/groups/", json=payload())
    assert group.status_code == 201
    response = await group_client.delete("/courses/1")
    assert response.status_code == 409, response.text
    assert (await group_client.get("/groups/")).json()["total"] == 1


async def test_enrolled_group_protection(group_client, group_data):
    group = (await group_client.post("/groups/", json=payload())).json()
    async with group_data() as db:
        obj = await db.get(Group, group["id"])
        obj.current_students = 5
        await db.commit()
    assert (await group_client.put(f"/groups/{group['id']}", json={"max_students": 4})).status_code == 400
    assert (await group_client.put(f"/groups/{group['id']}", json={"course_id": 2})).status_code == 409
    assert (await group_client.delete(f"/groups/{group['id']}")).status_code == 409


async def test_branch_permissions_and_options(group_client):
    group = (await group_client.post("/groups/", json=payload(branch_id=2, teacher_id=3, room_id=2))).json()
    token = await create_access_token(4)
    group_client.headers["Authorization"] = f"Bearer {token}"
    response = await group_client.get("/groups/options")
    assert response.status_code == 200, response.text
    assert [item["id"] for item in response.json()["branches"]] == [1]
    assert (await group_client.get("/groups/")).json()["total"] == 0
    assert (await group_client.get(f"/groups/{group['id']}")).status_code == 403
    assert (await group_client.put(f"/groups/{group['id']}", json={"name": "Changed"})).status_code == 403
    assert (await group_client.post("/groups/", json=payload(branch_id=2, teacher_id=3, room_id=2, name="Other"))).status_code == 403


@pytest.mark.parametrize("user_id, expected", [(None, 401), (2, 403), (6, 403)])
async def test_authentication_and_roles(group_client, user_id, expected):
    group_client.headers.pop("Authorization", None)
    if user_id:
        group_client.headers["Authorization"] = f"Bearer {await create_access_token(user_id)}"
    response = await group_client.get("/groups/")
    assert response.status_code == expected
