# tests/test_lead_statuses.py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

BASE = "/lead_statuses"


# ── helper ────────────────────────────────────────────────────────
async def create_status(client: AsyncClient, name: str, is_lost=False, is_won=False) -> int:
    resp = await client.post(BASE + "/", json={
        "name": name,
        "is_lost": is_lost,
        "is_won": is_won,
    })
    assert resp.status_code in (200, 201), f"Create failed: {resp.text}"
    # agar response ichida id bo'lmasa GET orqali olamiz
    data = resp.json()
    if "id" in data:
        return data["id"]
    # id yo'q bo'lsa — GET dan oxirgi yozuvni olamiz
    all_resp = await client.get(BASE + "/")
    items = all_resp.json()
    return items[-1]["id"]


# ══════════════════════════════════════════════════════════════════
# POST /lead_statuses/
# ══════════════════════════════════════════════════════════════════
class TestAddLeadStatus:

    async def test_create_success(self, client: AsyncClient):
        resp = await client.post(BASE + "/", json={
            "name": "New",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code in (200, 201)
        assert "message" in resp.json()

    async def test_create_duplicate_name(self, client: AsyncClient):
        """Duplicate nom → 401 (kodda shunday yozilgan)"""
        await create_status(client, "Alpha")
        resp = await client.post(BASE + "/", json={
            "name": "Alpha",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code == 401

    async def test_create_duplicate_case_insensitive(self, client: AsyncClient):
        """alpha va ALPHA bir xil hisoblanishi kerak"""
        await create_status(client, "alpha")
        resp = await client.post(BASE + "/", json={
            "name": "ALPHA",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code == 401

    async def test_create_both_lost_and_won(self, client: AsyncClient):
        """is_lost=True va is_won=True bir vaqtda → 422"""
        resp = await client.post(BASE + "/", json={
            "name": "Conflict",
            "is_lost": True,
            "is_won": True,
        })
        assert resp.status_code == 422

    async def test_position_auto_increments(self, client: AsyncClient):
        """Har yangi status oldingi + 1 position olishi kerak"""
        await create_status(client, "First")
        await create_status(client, "Second")
        await create_status(client, "Third")

        all_resp = await client.get(BASE + "/")
        items = all_resp.json()
        positions = [i["position"] for i in items]
        assert positions == sorted(positions)  # o'sib borishi kerak


# ══════════════════════════════════════════════════════════════════
# GET /lead_statuses/
# ══════════════════════════════════════════════════════════════════
class TestGetLeadStatuses:

    async def test_get_empty(self, client: AsyncClient):
        """Hech narsa yo'q → bo'sh list"""
        resp = await client.get(BASE + "/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_all(self, client: AsyncClient):
        """Barcha statuslar qaytishi kerak"""
        await create_status(client, "Open")
        await create_status(client, "Closed")

        resp = await client.get(BASE + "/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_returns_correct_fields(self, client: AsyncClient):
        """Response sxemadagi fieldlar mavjudligini tekshirish"""
        await create_status(client, "Test Status", is_lost=True)

        resp = await client.get(BASE + "/")
        item = resp.json()[0]
        assert "id" in item
        assert "name" in item
        assert "is_lost" in item
        assert "is_won" in item


# ══════════════════════════════════════════════════════════════════
# PUT /lead_statuses/{id}
# ══════════════════════════════════════════════════════════════════
class TestUpdateLeadStatus:

    async def test_update_success(self, client: AsyncClient):
        sid = await create_status(client, "Old Name")
        resp = await client.put(f"{BASE}/{sid}", json={
            "name": "New Name",
            "is_lost": True,
            "is_won": False,
        })
        assert resp.status_code == 200
        assert resp.json()["message"] == "Lead status updated successfully"

    async def test_update_not_found(self, client: AsyncClient):
        resp = await client.put(f"{BASE}/99999", json={
            "name": "Whatever",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code == 404

    async def test_update_duplicate_name(self, client: AsyncClient):
        """Boshqa statusning nomini olish → 409"""
        await create_status(client, "Alpha")
        bid = await create_status(client, "Beta")

        resp = await client.put(f"{BASE}/{bid}", json={
            "name": "Alpha",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code == 409

    async def test_update_same_name_allowed(self, client: AsyncClient):
        """O'z nomini saqlab faqat is_lost o'zgartirish → 200"""
        sid = await create_status(client, "Keep Name")
        resp = await client.put(f"{BASE}/{sid}", json={
            "name": "Keep Name",
            "is_lost": True,
            "is_won": False,
        })
        assert resp.status_code == 200

    async def test_update_case_insensitive_duplicate(self, client: AsyncClient):
        """ALPHA va alpha bir xil → 409"""
        await create_status(client, "alpha")
        bid = await create_status(client, "Beta")

        resp = await client.put(f"{BASE}/{bid}", json={
            "name": "ALPHA",
            "is_lost": False,
            "is_won": False,
        })
        assert resp.status_code == 409


# ══════════════════════════════════════════════════════════════════
# PATCH /lead_statuses/{id}  — faqat nom o'zgartiradi
# ══════════════════════════════════════════════════════════════════
class TestUpdateLeadStatusName:

    async def test_patch_success(self, client: AsyncClient):
        """Faqat nom o'zgarishi → 200"""
        sid = await create_status(client, "Old")
        resp = await client.patch(
            f"{BASE}/{sid}",
            params={"lead_status_new_name": "New"}   # query param
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Lead status updated successfully"

    async def test_patch_not_found(self, client: AsyncClient):
        resp = await client.patch(
            f"{BASE}/99999",
            params={"lead_status_new_name": "Test"}
        )
        assert resp.status_code == 404

    async def test_patch_duplicate_name(self, client: AsyncClient):
        """Boshqa statusning nomini olish → 409"""
        await create_status(client, "Alpha")
        bid = await create_status(client, "Beta")

        resp = await client.patch(
            f"{BASE}/{bid}",
            params={"lead_status_new_name": "Alpha"}
        )
        assert resp.status_code == 409

    async def test_patch_same_name_allowed(self, client: AsyncClient):
        """O'z nomini yuborsang → 200 (o'zini exclude qiladi)"""
        sid = await create_status(client, "Same Name")
        resp = await client.patch(
            f"{BASE}/{sid}",
            params={"lead_status_new_name": "Same Name"}
        )
        assert resp.status_code == 200

    async def test_patch_case_insensitive_duplicate(self, client: AsyncClient):
        await create_status(client, "gamma")
        bid = await create_status(client, "Delta")

        resp = await client.patch(
            f"{BASE}/{bid}",
            params={"lead_status_new_name": "GAMMA"}
        )
        assert resp.status_code == 409