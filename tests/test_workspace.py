import pytest

from test_groups import group_data, group_client
from app.model.employees import Employees
from app.utils.security import create_access_token, create_refresh_token

pytestmark = pytest.mark.asyncio


async def test_options_exclude_password_and_respect_branch(group_client):
    response = await group_client.get("/workspace/options")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user"]["id"] == 1
    assert len(data["branches"]) == 2
    assert "password" not in response.text
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(4)}"
    data = (await group_client.get("/workspace/options")).json()
    assert [branch["id"] for branch in data["branches"]] == [1]
    assert all(employee["branch_id"] == 1 for employee in data["employees"])


async def test_overview_is_real_and_scoped(group_client):
    response = await group_client.get("/workspace/overview")
    assert response.status_code == 200, response.text
    assert response.json()["students"] == 0
    assert response.json()["groups"] == 0
    assert len(response.json()["trend"]) == 6
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(4)}"
    assert (await group_client.get("/workspace/overview?branch_id=2")).status_code == 403


async def test_course_duration_is_available_for_group_end_date_suggestions(group_client, group_data):
    from app.model.courses import Course
    async with group_data() as db:
        course = await db.get(Course, 1)
        course.duration_months = 6
        await db.commit()
    workspace = (await group_client.get("/workspace/options")).json()
    assert next(course for course in workspace["courses"] if course["id"] == 1)["duration_months"] == 6
    options = (await group_client.get("/groups/options")).json()
    assert next(course for course in options["courses"] if course["id"] == 1)["duration_months"] == 6


async def test_refresh_token_flow_and_access_type(group_client):
    refresh = await create_refresh_token(1)
    response = await group_client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"
    group_client.headers["Authorization"] = f"Bearer {refresh}"
    assert (await group_client.get("/workspace/options")).status_code == 401
    assert (await group_client.post("/auth/refresh", json={"refresh_token": await create_access_token(1)})).status_code == 401


async def test_branch_and_room_editor(group_client):
    response = await group_client.put("/branches/1", json={"name": "Chilonzor", "code": "CHL", "address": "Test manzil", "phone": "+998900000000", "city": "Toshkent", "opened_at": "2026-01-01", "is_active": True})
    assert response.status_code == 200, response.text
    response = await group_client.put("/rooms/1", json={"branch_id": 1, "name": "Fokus", "capacity": 14, "is_active": True})
    assert response.status_code == 200, response.text
    response = await group_client.post("/rooms/", json={"branch_id": 2, "name": "Yangi xona", "capacity": 10})
    assert response.status_code == 200, response.text
    response = await group_client.post("/rooms/", json={"branch_id": 1, "name": "Noto'g'ri", "capacity": 0})
    assert response.status_code == 422


async def test_teacher_profile_editor_and_boss_list(group_client):
    response = await group_client.post("/teacher-profiles/", json={"employee_id": 5, "specialization": "Dizayn", "experience_years": 3, "max_groups": 4})
    assert response.status_code == 201, response.text
    assert response.json()["employee_id"] == 5
    assert (await group_client.get("/teacher-profiles/")).status_code == 200
    assert (await group_client.put("/teacher-profiles/5", json={"bio": "Yangilangan profil"})).status_code == 200
    assert (await group_client.delete("/teacher-profiles/5")).status_code == 200


async def test_global_and_composite_employee_role_editor(group_client):
    response = await group_client.post("/employee-roles/", json={"employee_id": 5, "role_id": 3, "branch_id": None})
    assert response.status_code == 200, response.text
    assert (await group_client.get("/employee-roles/")).status_code == 200
    response = await group_client.put("/employee-roles/5/3", json={"role_id": 2, "branch_id": 2})
    assert response.status_code == 200, response.text
    assert (await group_client.delete("/employee-roles/5/2")).status_code == 200


async def test_employee_update_keeps_password_and_deactivation_works(group_client, group_data):
    response = await group_client.put("/employees/5", json={"branch_id": 2, "first_name": "Aziz", "last_name": "Test", "phone": "+998900000005", "email": None, "birth_date": "1995-01-01", "photo_url": "", "position": "Teacher", "hired_at": "2026-01-01", "password": None})
    assert response.status_code == 200, response.text
    async with group_data() as db:
        employee = await db.get(Employees, 5)
        assert employee.password == "test-only"
        assert employee.branch_id == 2
    assert (await group_client.delete("/employees/1")).status_code == 400
    assert (await group_client.delete("/employees/5")).status_code == 200
    assert (await group_client.patch("/employees/5?is_active=true")).status_code == 200


async def test_optional_lead_references_and_conversion(group_client):
    response = await group_client.post("/leads/", json={"branch_id": 1, "first_name": "Lid", "phone": "+998901234567"})
    assert response.status_code == 200, response.text
    lead = (await group_client.get("/leads/")).json()["items"][0]
    response = await group_client.post("/students/", json={"branch_id": 1, "first_name": "Lid", "last_name": "Test", "phone": "+998901234567", "parent_phone": "+998900000000"})
    assert response.status_code == 200, response.text
    student = (await group_client.get("/students/")).json()["items"][0]
    response = await group_client.patch(f"/leads/{lead['id']}?student_id={student['id']}")
    assert response.status_code == 200, response.text
    student = (await group_client.get("/students/")).json()["items"][0]
    assert student["status"] == "faol"
    assert student["lead"]["id"] == lead["id"]
