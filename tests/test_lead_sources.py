import inspect
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.routers.lead_sources import (
    add_lead_source,
    get_lead_source,
    update_lead_source,
    change_lead_source,
    delete_lead_source,
)

pytestmark = pytest.mark.asyncio
BASE = "/lead_source"


# ── require_role mock ──────────────────────────────────────────────
async def _mock_admin():
    return {"id": 1, "role": "admin"}


def _collect_auth_deps(*funcs):
    """Route function signature dan Depends() larni olib override qilish uchun"""
    seen = []
    for func in funcs:
        for param in inspect.signature(func).parameters.values():
            dep = getattr(param.default, "dependency", None)
            if dep is not None and dep not in seen:
                seen.append(dep)
    return seen


_AUTH_DEPS = _collect_auth_deps(
    add_lead_source, get_lead_source,
    update_lead_source, change_lead_source, delete_lead_source,
)


@pytest_asyncio.fixture
async def ac(client: AsyncClient):
    """DB + auth mock bo'lgan client"""
    for dep in _AUTH_DEPS:
        app.dependency_overrides[dep] = _mock_admin
    yield client
    # conftest dagi client fixture o'zi dependency_overrides.clear() qiladi


# ── Helper ─────────────────────────────────────────────────────────
async def create_source(ac: AsyncClient, name: str, monthly_budget: float = 1000.0) -> int:
    resp = await ac.post(BASE + "/", json={"name": name, "monthly_budget": monthly_budget})
    assert resp.status_code in (200, 201), f"Create failed: {resp.text}"
    items = (await ac.get(BASE + "/")).json()
    for item in reversed(items):
        if item["name"] == name:
            return item["id"]
    raise AssertionError(f"'{name}' not found after create")


# ══════════════════════════════════════════════════════════════════
# POST /lead_source/
# ══════════════════════════════════════════════════════════════════
class TestAddLeadSource:

    async def test_create_success(self, ac: AsyncClient):
        resp = await ac.post(BASE + "/", json={"name": "Google Ads", "monthly_budget": 500.0})
        assert resp.status_code in (200, 201)
        assert "msg" in resp.json()

    async def test_create_duplicate(self, ac: AsyncClient):
        """Duplicate nom → 400"""
        await create_source(ac, "Facebook")
        resp = await ac.post(BASE + "/", json={"name": "Facebook", "monthly_budget": 500.0})
        assert resp.status_code == 400

    async def test_no_auth(self, client: AsyncClient):
        """Auth yo'q → 401/403"""
        resp = await client.post(BASE + "/", json={"name": "Test", "monthly_budget": 100.0})
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════
# GET /lead_source/
# ══════════════════════════════════════════════════════════════════
class TestGetLeadSource:

    async def test_get_empty(self, ac: AsyncClient):
        resp = await ac.get(BASE + "/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_all(self, ac: AsyncClient):
        await create_source(ac, "Instagram")
        await create_source(ac, "Twitter")
        resp = await ac.get(BASE + "/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_returns_correct_fields(self, ac: AsyncClient):
        await create_source(ac, "TikTok")
        item = (await ac.get(BASE + "/")).json()[0]
        assert "id" in item
        assert "name" in item
        assert "is_active" in item

    async def test_no_auth(self, client: AsyncClient):
        resp = await client.get(BASE + "/")
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════
# PUT /lead_source/{id}
# ══════════════════════════════════════════════════════════════════
class TestUpdateLeadSource:

    async def test_update_success(self, ac: AsyncClient):
        sid = await create_source(ac, "Old Source")
        resp = await ac.put(f"{BASE}/{sid}", json={"name": "New Source", "monthly_budget": 2000.0})
        assert resp.status_code == 200
        assert resp.json()["msg"] == "Lead Source updated successfully"

    async def test_update_not_found(self, ac: AsyncClient):
        resp = await ac.put(f"{BASE}/99999", json={"name": "X", "monthly_budget": 0.0})
        assert resp.status_code == 404

    async def test_update_inactive_source(self, ac: AsyncClient):
        """is_active=False bo'lsa → 401"""
        sid = await create_source(ac, "Inactive Source")
        await ac.patch(f"{BASE}/{sid}", params={"lead_source": False})  # deactivate
        resp = await ac.put(f"{BASE}/{sid}", json={"name": "Try Update", "monthly_budget": 0.0})
        assert resp.status_code == 401

    async def test_no_auth(self, client: AsyncClient):
        resp = await client.put(f"{BASE}/1", json={"name": "X", "monthly_budget": 0.0})
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════
# PATCH /lead_source/{id}  — is_active toggle
# ══════════════════════════════════════════════════════════════════
class TestChangeLeadSource:

    async def test_deactivate(self, ac: AsyncClient):
        sid = await create_source(ac, "Active Source")
        resp = await ac.patch(f"{BASE}/{sid}", params={"lead_source": False})
        assert resp.status_code == 200

    async def test_activate(self, ac: AsyncClient):
        sid = await create_source(ac, "Another Source")
        await ac.patch(f"{BASE}/{sid}", params={"lead_source": False})
        resp = await ac.patch(f"{BASE}/{sid}", params={"lead_source": True})
        assert resp.status_code == 200

    async def test_patch_not_found(self, ac: AsyncClient):
        resp = await ac.patch(f"{BASE}/99999", params={"lead_source": False})
        assert resp.status_code == 404

    async def test_no_auth(self, client: AsyncClient):
        resp = await client.patch(f"{BASE}/1", params={"lead_source": False})
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════
# DELETE /lead_source/{id}
# ══════════════════════════════════════════════════════════════════
class TestDeleteLeadSource:

    async def test_delete_success(self, ac: AsyncClient):
        sid = await create_source(ac, "To Delete")
        resp = await ac.delete(f"{BASE}/{sid}")
        assert resp.status_code == 200
        assert resp.json()["msg"] == "Lead Source deleted successfully"