from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from tests.test_groups import group_data, group_client, payload
from app.model.students import Student, StudentStatus
from app.model.groups import Group
from app.model.enrollments import Enrollment
from app.utils.security import create_access_token

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    monkeypatch.setattr("app.routers.enrollments.today", lambda: date(2026, 11, 5))


async def setup(group_data, client, **changes):
    async with group_data() as db:
        db.add_all([Student(id=i, branch_id=2 if i == 3 else 1, first_name=f"Ism {i}", last_name="Familiya",
                            phone=f"+99891111111{i}", parent_phone="+998900000000", status=StudentStatus.faol)
                    for i in range(1, 5)])
        await db.commit()
    response = await client.post("/groups/", json=payload(**changes))
    assert response.status_code == 201, response.text
    return response.json()["id"]


def member(target_group, **changes):
    return dict(group_id=target_group, student_id=1, joined_at="2026-11-03") | changes


async def count(client, group_id):
    return (await client.get(f"/groups/{group_id}")).json()["current_students"]


async def test_membership_lifecycle_price_snapshot_and_history(group_data, group_client):
    group = await setup(group_data, group_client)
    response = await group_client.post("/enrollments/", json=member(group))
    assert response.status_code == 201, response.text
    row = response.json()
    assert Decimal(row["price"]) == 750000
    assert row["student"]["first_name"] == "Ism 1"
    assert "password" not in str(row)
    assert await count(group_client, group) == 1
    assert (await group_client.put(f"/groups/{group}", json={"price": "900000"})).status_code == 200
    assert Decimal((await group_client.get(f"/enrollments/{row['id']}")).json()["price"]) == 750000
    assert (await group_client.put(f"/enrollments/{row['id']}", json={"price": "0"})).json()["price"] == "0.00"
    assert (await group_client.patch(f"/enrollments/{row['id']}/status", json={"status": "muzlatilgan"})).status_code == 200
    assert await count(group_client, group) == 1
    result = await group_client.delete(f"/enrollments/{row['id']}")
    assert result.json()["left_at"] == "2026-11-05"
    assert await count(group_client, group) == 0
    assert (await group_client.delete(f"/enrollments/{row['id']}")).json()["id"] == row["id"]
    reopened = await group_client.patch(f"/enrollments/{row['id']}/status", json={"status": "faol"})
    assert reopened.json()["left_at"] is None
    assert await count(group_client, group) == 1
    updated = await group_client.put(f"/enrollments/{row['id']}", json={"price": None})
    assert Decimal(updated.json()["price"]) == 900000
    async with group_data() as db:
        assert len((await db.scalars(select(Enrollment))).all()) == 1


async def test_capacity_duplicate_and_reactivation(group_data, group_client):
    group = await setup(group_data, group_client, max_students=1)
    first = (await group_client.post("/enrollments/", json=member(group))).json()
    assert (await group_client.post("/enrollments/", json=member(group))).status_code == 409
    assert (await group_client.post("/enrollments/", json=member(group, student_id=2))).status_code == 409
    assert await count(group_client, group) == 1
    await group_client.delete(f"/enrollments/{first['id']}")
    second = await group_client.post("/enrollments/", json=member(group, student_id=2))
    assert second.status_code == 201
    assert (await group_client.patch(f"/enrollments/{first['id']}/status", json={"status": "faol"})).status_code == 409
    assert await count(group_client, group) == 1


@pytest.mark.parametrize("changes, expected", [
    ({"student_id": 999}, 404), ({"group_id": 999}, 404), ({"student_id": 3}, 400),
    ({"joined_at": "2026-11-06"}, 400), ({"joined_at": "2026-12-10"}, 400),
    ({"left_at": "2026-11-04"}, 400),
    ({"status": "ketgan", "left_at": "2026-11-02"}, 400),
    ({"status": "bitirgan", "left_at": "2026-11-06"}, 400),
    ({"price": "-1"}, 422), ({"price": "1.001"}, 422), ({"status": "unknown"}, 422),
])
async def test_invalid_memberships(group_data, group_client, changes, expected):
    group = await setup(group_data, group_client, end_date="2026-12-01")
    response = await group_client.post("/enrollments/", json=member(group, **changes))
    assert response.status_code == expected, response.text
    assert await count(group_client, group) == 0


async def test_closed_history_reenrollment_and_immutable_parents(group_data, group_client):
    group = await setup(group_data, group_client)
    old = await group_client.post("/enrollments/", json=member(group, joined_at="2026-11-01", left_at="2026-11-02", status="bitirgan"))
    assert old.status_code == 201, old.text
    assert await count(group_client, group) == 0
    assert (await group_client.delete(f"/enrollments/{old.json()['id']}")).json()["status"] == "bitirgan"
    new = await group_client.post("/enrollments/", json=member(group))
    assert new.status_code == 201, new.text
    assert (await group_client.put(f"/enrollments/{old.json()['id']}", json={"left_at": "2026-11-03"})).status_code == 409
    for change in ({"student_id": 2}, {"group_id": group}, {"joined_at": None}, {"status": None}):
        assert (await group_client.put(f"/enrollments/{new.json()['id']}", json=change)).status_code == 422


async def test_group_and_student_guards(group_data, group_client):
    group = await setup(group_data, group_client)
    row = (await group_client.post("/enrollments/", json=member(group))).json()
    for status in ("tugagan", "bekor_qilingan"):
        assert (await group_client.patch(f"/groups/{group}/status", json={"status": status})).status_code == 409
    for body in ({"branch_id": 2}, {"status": "ketgan"}, {"status": "bitirgan"}):
        assert (await group_client.put("/students/1", json=body)).status_code == 409
    assert (await group_client.delete("/students/1")).status_code == 409
    assert (await group_client.patch("/students/1/status", json={"status": "bitirgan"})).status_code == 409
    await group_client.delete(f"/enrollments/{row['id']}")
    assert (await group_client.put(f"/groups/{group}", json={"course_id": 2})).status_code == 409
    assert (await group_client.put(f"/groups/{group}", json={"branch_id": 2, "teacher_id": 3, "room_id": 2})).status_code == 409
    assert (await group_client.put("/students/1", json={"branch_id": 2})).status_code == 200
    assert (await group_client.patch(f"/groups/{group}/status", json={"status": "tugagan"})).status_code == 200
    assert (await group_client.patch(f"/enrollments/{row['id']}/status", json={"status": "faol"})).status_code == 400


async def test_filters_and_branch_permissions(group_data, group_client):
    group = await setup(group_data, group_client)
    row = (await group_client.post("/enrollments/", json=member(group))).json()
    for search in ("Ism 1 Familiya", "1111111", "PY-26"):
        result = await group_client.get("/enrollments/", params={"search": search})
        assert result.status_code == 200, result.text
        assert result.json()["total"] == 1
    assert (await group_client.get("/enrollments/", params={"status": "ketgan"})).json()["total"] == 0
    assert (await group_client.get("/enrollments/", params={"student_id": 2})).json()["total"] == 0
    assert (await group_client.get("/enrollments/", params={"group_id": group})).json()["total"] == 1
    token = await create_access_token(4)
    headers = {"Authorization": f"Bearer {token}"}
    assert (await group_client.get("/enrollments/?branch_id=2", headers=headers)).status_code == 403
    other_group = (await group_client.post("/groups/", json=payload(branch_id=2, teacher_id=3, room_id=2))).json()["id"]
    other = (await group_client.post("/enrollments/", json=member(other_group, student_id=3))).json()
    assert (await group_client.get("/enrollments/", headers=headers)).json()["total"] == 1
    for method, path, kwargs in (
        ("get", f"/enrollments/{other['id']}", {}),
        ("put", f"/enrollments/{other['id']}", {"json": {"price": "0"}}),
        ("delete", f"/enrollments/{other['id']}", {}),
        ("post", "/enrollments/", {"json": member(other_group, student_id=3)}),
    ):
        assert (await getattr(group_client, method)(path, headers=headers, **kwargs)).status_code == 403
    teacher = await create_access_token(2)
    assert (await group_client.get(f"/enrollments/{row['id']}", headers={"Authorization": f"Bearer {teacher}"})).status_code == 403
    assert (await group_client.get("/enrollments/999")).status_code == 404


async def test_multiple_groups_and_dates_preserve_membership_history(group_data, group_client):
    group = await setup(group_data, group_client)
    other = (await group_client.post("/groups/", json=payload(name="Second group", price="0"))).json()["id"]
    assert (await group_client.post("/enrollments/", json=member(group, joined_at="2026-11-05"))).status_code == 201
    free = await group_client.post("/enrollments/", json=member(other))
    assert free.status_code == 201 and Decimal(free.json()["price"]) == 0
    assert (await group_client.put(f"/groups/{group}", json={"end_date": "2026-11-04"})).status_code == 409
    assert await count(group_client, group) == 1
    assert await count(group_client, other) == 1


async def test_closed_group_and_departed_student(group_data, group_client):
    group = await setup(group_data, group_client, status="tugagan")
    assert (await group_client.post("/enrollments/", json=member(group))).status_code == 409
    historical = await group_client.post("/enrollments/", json=member(group, status="bitirgan"))
    assert historical.status_code == 201
    async with group_data() as db:
        (await db.get(Group, group)).status = "faol"
        (await db.get(Student, 2)).status = StudentStatus.ketgan
        await db.commit()
    assert (await group_client.post("/enrollments/", json=member(group, student_id=2))).status_code == 409
