from datetime import date, datetime

import pytest
import pytest_asyncio
from sqlalchemy import select, func

from test_groups import group_data, group_client, payload
from app.model.groups import Group
from app.model.rooms import Room
from app.model.teacher_profiles import TeacherProfiles
from app.model.lesson_sessions import LessonSession
from app.utils.security import create_access_token

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def timetable(group_client, group_data, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 3, 12, tzinfo=tz)
    monkeypatch.setattr("app.utils.timetable.datetime", FixedDateTime)
    async with group_data() as db:
        (await db.get(TeacherProfiles, 2)).max_groups = 10
        db.add(TeacherProfiles(employee_id=5, max_groups=10))
        db.add(Room(id=3, branch_id=1, name="Ikkinchi xona", capacity=20))
        db.add(Room(id=4, branch_id=1, name="Kichik xona", capacity=5))
        await db.commit()
    groups = []
    for name, teacher in (("PY-A", 2), ("PY-B", 5), ("PY-C", 2)):
        response = await group_client.post("/groups/", json=payload(name=name, teacher_id=teacher, start_date="2026-11-01", end_date="2026-12-31"))
        assert response.status_code == 201, response.text
        groups.append(response.json()["id"])
    return groups


def slot(ident, **changes):
    return dict(group_id=ident, weekday=1, start_time="14:00", end_time="16:00", room_id=1) | changes


def lesson(group_id, **changes):
    return dict(group_id=group_id, date="2026-11-02", start_time="14:00", end_time="16:00", room_id=1, teacher_id=2) | changes


async def test_schedule_crud_filters_and_adjacent_slots(group_client, timetable):
    response = await group_client.post("/group-schedules/", json=slot(timetable[0]))
    assert response.status_code == 201, response.text
    ident = response.json()["id"]
    assert response.json()["group"]["teacher"]["id"] == 2
    response = await group_client.put(f"/group-schedules/{ident}", json=slot(timetable[0], weekday=3, room_id=3))
    assert response.status_code == 200, response.text
    assert response.json()["room"]["id"] == 3
    assert (await group_client.get("/group-schedules/?weekday=3&teacher_id=2&room_id=3&search=PY-A")).json()["total"] == 1
    assert (await group_client.get("/group-schedules/?weekday=1")).json()["total"] == 0
    assert (await group_client.post("/group-schedules/", json=slot(timetable[1], weekday=3, room_id=3, start_time="16:00", end_time="18:00"))).status_code == 201
    assert (await group_client.delete(f"/group-schedules/{ident}")).status_code == 200
    assert (await group_client.get(f"/group-schedules/{ident}")).status_code == 404


@pytest.mark.parametrize("changes,expected", [
    ({"weekday": 0}, 422), ({"weekday": 8}, 422), ({"start_time": "16:00"}, 422),
    ({"end_time": "13:00"}, 422), ({"start_time": "14:00:01"}, 422),
    ({"start_time": "14:00:00+05:00"}, 422), ({"room_id": 2}, 400),
    ({"room_id": 4}, 400), ({"group_id": 9999}, 404),
])
async def test_invalid_schedule(group_client, timetable, changes, expected):
    response = await group_client.post("/group-schedules/", json=slot(timetable[0], **changes))
    assert response.status_code == expected, response.text


@pytest.mark.parametrize("other_index,room_id,resource", [(1, 1, "Xona"), (2, 3, "O'qituvchi"), (0, 3, "Guruh")])
async def test_weekly_conflicts(group_client, timetable, other_index, room_id, resource):
    await group_client.post("/group-schedules/", json=slot(timetable[0]))
    response = await group_client.post("/group-schedules/", json=slot(timetable[other_index], room_id=room_id, start_time="15:00", end_time="17:00"))
    assert response.status_code == 409, response.text
    assert resource in response.json()["detail"]


async def test_date_ranges_and_weekday_occurrence(group_client, timetable):
    await group_client.post("/group-schedules/", json=slot(timetable[0]))
    response = await group_client.put(f"/groups/{timetable[1]}", json={"start_date": "2027-01-01", "end_date": "2027-01-31"})
    assert response.status_code == 200, response.text
    assert (await group_client.post("/group-schedules/", json=slot(timetable[1]))).status_code == 201
    response = await group_client.put(f"/groups/{timetable[1]}", json={"start_date": "2026-12-01"})
    assert response.status_code == 409, response.text
    response = await group_client.put(f"/groups/{timetable[2]}", json={"start_date": "2026-11-03", "end_date": "2026-11-03"})
    assert response.status_code == 200
    assert (await group_client.post("/group-schedules/", json=slot(timetable[2]))).status_code == 400


async def test_sessions_crud_status_and_history(group_client, timetable):
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[0], topic="Python kirish", note="Birinchi dars"))
    assert response.status_code == 201, response.text
    ident = response.json()["id"]
    response = await group_client.put(f"/lesson-sessions/{ident}", json=lesson(timetable[0], teacher_id=5, room_id=3, topic="O'zgaruvchilar"))
    assert response.status_code == 200, response.text
    assert response.json()["teacher"]["id"] == 5
    response = await group_client.patch(f"/lesson-sessions/{ident}/status", json={"status": "otilgan"})
    assert response.status_code == 200, response.text
    response = await group_client.get("/lesson-sessions/?date_from=2026-11-02&date_to=2026-11-02&status=otilgan&teacher_id=5&search=O%27zgaruvchilar")
    assert response.json()["total"] == 1
    response = await group_client.delete(f"/lesson-sessions/{ident}")
    assert response.status_code == 200, response.text
    assert (await group_client.get(f"/lesson-sessions/{ident}")).json()["status"] == "bekor_qilingan"


@pytest.mark.parametrize("changes,expected", [
    ({"date": "2026-10-31"}, 400), ({"date": "2027-01-01"}, 400),
    ({"teacher_id": 3}, 400), ({"teacher_id": 4}, 400), ({"room_id": 4}, 400),
    ({"end_time": "14:00"}, 422), ({"status": "otilgan", "date": "2026-12-31"}, 400),
    ({"topic": "x" * 201}, 422), ({"weekday": 1}, 422),
    ({"teacher_id": 4, "status": "otilgan"}, 400),
])
async def test_invalid_session(group_client, timetable, changes, expected):
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[0], **changes))
    assert response.status_code == expected, response.text


async def test_actual_and_recurring_conflicts(group_client, timetable):
    await group_client.post("/group-schedules/", json=slot(timetable[0]))
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[1], teacher_id=5, start_time="15:00", end_time="17:00"))
    assert response.status_code == 409, response.text
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[0], teacher_id=5, room_id=3))
    assert response.status_code == 201, response.text
    # O'rinbosar boshqa xonada o'tadi: o'sha sanadagi asl xona va ustoz bo'shaydi.
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[2]))
    assert response.status_code == 201, response.text
    response = await group_client.post("/lesson-sessions/", json=lesson(timetable[1], teacher_id=5, room_id=1, start_time="15:00", end_time="17:00"))
    assert response.status_code == 409
    response = await group_client.post("/group-schedules/", json=slot(timetable[1], room_id=3, start_time="15:00", end_time="17:00"))
    assert response.status_code == 409


async def test_generation_idempotency_and_snapshot(group_client, timetable):
    for weekday in (1, 3, 5):
        assert (await group_client.post("/group-schedules/", json=slot(timetable[0], weekday=weekday))).status_code == 201
    data = {"group_id": timetable[0], "date_from": "2026-11-02", "date_to": "2026-11-08"}
    response = await group_client.post("/lesson-sessions/generate", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 3
    assert (await group_client.post("/lesson-sessions/generate", json=data)).json()["skipped"] == 3
    lessons = (await group_client.get(f"/lesson-sessions/?group_id={timetable[0]}")).json()["items"]
    await group_client.delete(f"/lesson-sessions/{lessons[0]['id']}")
    assert (await group_client.post("/lesson-sessions/generate", json=data)).json()["created"] == 0
    response = await group_client.put(f"/groups/{timetable[0]}", json={"teacher_id": 5})
    assert response.status_code == 200, response.text
    assert (await group_client.get(f"/lesson-sessions/{lessons[1]['id']}")).json()["teacher"]["id"] == 2
    schedules = (await group_client.get(f"/group-schedules/?group_id={timetable[0]}")).json()["items"]
    await group_client.delete(f"/group-schedules/{schedules[0]['id']}")
    assert (await group_client.get(f"/lesson-sessions/?group_id={timetable[0]}")).json()["total"] == 3


async def test_generation_rolls_back_all_on_conflict(group_client, timetable, group_data):
    await group_client.post("/group-schedules/", json=slot(timetable[0]))
    # Qarama-qarshi tarixiy darsni to'g'ridan-to'g'ri bazada tayyorlaymiz.
    async with group_data() as db:
        from datetime import time
        db.add(LessonSession(group_id=timetable[1], teacher_id=5, room_id=1, date=date(2026, 11, 9), start_time=time(14), end_time=time(16)))
        await db.commit()
    response = await group_client.post("/lesson-sessions/generate", json={"group_id": timetable[0], "date_from": "2026-11-02", "date_to": "2026-11-09"})
    assert response.status_code == 409, response.text
    async with group_data() as db:
        assert await db.scalar(select(func.count(LessonSession.id)).where(LessonSession.group_id == timetable[0])) == 0


async def test_group_changes_cannot_break_timetable(group_client, timetable):
    await group_client.post("/group-schedules/", json=slot(timetable[0], room_id=3))
    await group_client.post("/group-schedules/", json=slot(timetable[1], room_id=1))
    assert (await group_client.put(f"/groups/{timetable[1]}", json={"teacher_id": 2})).status_code == 409
    await group_client.post("/lesson-sessions/", json=lesson(timetable[0], room_id=3))
    assert (await group_client.delete(f"/groups/{timetable[0]}")).status_code == 409
    assert (await group_client.put(f"/groups/{timetable[0]}", json={"start_date": "2026-11-03"})).status_code == 409


async def test_branch_and_role_access(group_client, timetable):
    created = (await group_client.post("/group-schedules/", json=slot(timetable[0]))).json()
    response = await group_client.post("/groups/", json=payload(branch_id=2, teacher_id=3, room_id=2, name="Other"))
    group = response.json()["id"]
    response = await group_client.post("/group-schedules/", json=slot(group, room_id=2))
    assert response.status_code == 201, response.text
    other_slot = response.json()["id"]
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(4)}"
    assert (await group_client.get("/group-schedules/")).json()["total"] == 1
    assert (await group_client.get(f"/group-schedules/{other_slot}")).status_code == 403
    assert (await group_client.put(f"/group-schedules/{created['id']}", json=slot(group, room_id=2))).status_code == 403
    assert (await group_client.post("/lesson-sessions/generate", json={"group_id": group, "date_from": "2026-11-09", "date_to": "2026-11-10"})).status_code == 403
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(2)}"
    assert (await group_client.get("/lesson-sessions/")).status_code == 403
    group_client.headers.clear()
    assert (await group_client.get("/group-schedules/")).status_code == 401


async def test_generate_limits_and_missing_schedule(group_client, timetable):
    assert (await group_client.post("/lesson-sessions/generate", json={"group_id": timetable[0], "date_from": "2026-11-02", "date_to": "2026-11-08"})).status_code == 409
    for dates in (("2026-11-08", "2026-11-02"), ("2026-11-01", "2027-03-01")):
        assert (await group_client.post("/lesson-sessions/generate", json={"group_id": timetable[0], "date_from": dates[0], "date_to": dates[1]})).status_code == 422


async def test_room_and_teacher_changes_keep_existing_schedule_valid(group_client, timetable):
    await group_client.post("/group-schedules/", json=slot(timetable[0], room_id=3))
    assert (await group_client.delete("/rooms/3")).status_code == 409
    assert (await group_client.put("/rooms/3", json={"branch_id": 1, "name": "Small", "capacity": 5})).status_code == 409
    assert (await group_client.put("/rooms/3", json={"branch_id": 2, "name": "Moved", "capacity": 20})).status_code == 409
    assert (await group_client.delete("/employees/2")).status_code == 409
    assert (await group_client.delete("/teacher-profiles/2")).status_code == 409


async def test_overlapping_ranges_without_shared_weekday_are_allowed(group_client, timetable):
    for ident, start, end in ((timetable[0], "2026-11-02", "2026-11-03"), (timetable[1], "2026-11-03", "2026-11-09")):
        assert (await group_client.put(f"/groups/{ident}", json={"start_date": start, "end_date": end})).status_code == 200
        response = await group_client.post("/group-schedules/", json=slot(ident))
        assert response.status_code == 201, response.text


async def test_cancelled_lesson_can_only_be_restored_if_free(group_client, timetable):
    first = await group_client.post("/lesson-sessions/", json=lesson(timetable[0]))
    ident = first.json()["id"]
    assert (await group_client.delete(f"/lesson-sessions/{ident}")).status_code == 200
    assert (await group_client.post("/lesson-sessions/", json=lesson(timetable[1], teacher_id=5))).status_code == 201
    assert (await group_client.patch(f"/lesson-sessions/{ident}/status", json={"status": "rejalashtirilgan"})).status_code == 409
    assert (await group_client.get(f"/lesson-sessions/{ident}")).json()["status"] == "bekor_qilingan"


async def test_cross_branch_lesson_read_update_cancel(group_client, timetable):
    group = (await group_client.post("/groups/", json=payload(branch_id=2, teacher_id=3, room_id=2, name="Branch two"))).json()
    response = await group_client.post("/lesson-sessions/", json=lesson(group["id"], teacher_id=3, room_id=2, date="2026-11-04"))
    assert response.status_code == 201, response.text
    ident = response.json()["id"]
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(4)}"
    assert (await group_client.get("/lesson-sessions/")).json()["total"] == 0
    assert (await group_client.get(f"/lesson-sessions/{ident}")).status_code == 403
    assert (await group_client.delete(f"/lesson-sessions/{ident}")).status_code == 403
    assert (await group_client.put(f"/lesson-sessions/{ident}", json=lesson(timetable[0]))).status_code == 403
