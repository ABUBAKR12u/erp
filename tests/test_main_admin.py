from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from test_groups import group_data, group_client
from app.model.employees import Employees
from app.utils.security import create_access_token

pytestmark = pytest.mark.asyncio


async def make_main_admin(sessions, ident):
    async with sessions() as db:
        employee = await db.get(Employees, ident)
        employee.is_superadmin = True
        await db.commit()


async def test_main_admin_has_full_access_without_role_assignment(group_client, group_data):
    await make_main_admin(group_data, 5)
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(5)}"
    options = (await group_client.get("/workspace/options")).json()
    assert options["user"]["is_superadmin"] is True
    assert len(options["branches"]) == 2
    assert (await group_client.get("/employee-roles/")).status_code == 200
    assert (await group_client.get("/role/")).status_code == 200
    assert (await group_client.get("/teacher-profiles/")).status_code == 200
    assert len((await group_client.get("/groups/options")).json()["branches"]) == 2
    response = await group_client.post("/rooms/", json={"branch_id": 2, "name": "Main admin room", "capacity": 10})
    assert response.status_code == 200, response.text


async def test_main_admin_cannot_be_deleted_or_deactivated(group_client, group_data):
    await make_main_admin(group_data, 5)
    assert (await group_client.delete("/employees/5")).status_code == 403
    assert (await group_client.patch("/employees/5?is_active=false")).status_code == 403
    group_client.headers["Authorization"] = f"Bearer {await create_access_token(4)}"
    assert (await group_client.delete("/employees/5")).status_code == 403
    async with group_data() as db:
        employee = await db.get(Employees, 5)
        assert employee.is_active and employee.is_superadmin and employee.fired_at is None


async def test_main_admin_management_role_cannot_be_removed(group_client, group_data):
    await make_main_admin(group_data, 1)
    response = await group_client.delete("/employee-roles/1/1")
    assert response.status_code == 403
    assert "Asosiy administrator" in response.json()["detail"]
    response = await group_client.put("/employee-roles/1/1", json={"role_id": 3, "branch_id": 1})
    assert response.status_code == 403


async def test_main_admin_flag_is_not_editable_through_employee_api(group_client, group_data):
    await make_main_admin(group_data, 5)
    payload = {"branch_id": 1, "first_name": "Main", "last_name": "Admin", "phone": "+998900000005", "email": None, "birth_date": "1995-01-01", "photo_url": "", "position": "Main admin", "hired_at": "2026-01-01", "password": None, "is_superadmin": False}
    response = await group_client.put("/employees/5", json=payload)
    assert response.status_code == 422, response.text
    async with group_data() as db:
        assert (await db.get(Employees, 5)).is_superadmin is True


@pytest.mark.parametrize("field, value", [("is_active", False), ("fired_at", date(2026, 11, 3))])
async def test_database_constraint_keeps_main_admin_active(group_data, field, value):
    await make_main_admin(group_data, 5)
    async with group_data() as db:
        employee = await db.get(Employees, 5)
        setattr(employee, field, value)
        with pytest.raises(IntegrityError):
            await db.commit()
        await db.rollback()
