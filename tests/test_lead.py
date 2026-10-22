# tests/test_leads.py
import inspect
import pytest
import pytest_asyncio
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.main import app
from app.routers.leads import add_lead, get_leads, update_lead, convert_lead, delete_lead
from app.model.branches import Branch
from app.model.lead_sources import LeadSource
from app.model.courses import Course
from app.model.lead_statuses import LeadStatus
from app.model.students import Student, StudentStatus

pytestmark = pytest.mark.asyncio
BASE = "/leads"


# ── Auth mock ─────────────────────────────────────────────────────
class MockUser:
    def __init__(self):
        self.id = 1

async def _mock_admin():
    return MockUser()

def _collect_auth_deps(*funcs):
    seen = []
    for func in funcs:
        for param in inspect.signature(func).parameters.values():
            dep = getattr(param.default, "dependency", None)
            if dep is not None and dep not in seen:
                seen.append(dep)
    return seen

_AUTH_DEPS = _collect_auth_deps(add_lead, get_leads, update_lead, convert_lead, delete_lead)


@pytest_asyncio.fixture
async def ac(client: AsyncClient):
    for dep in _AUTH_DEPS:
        app.dependency_overrides[dep] = _mock_admin
    yield client


# ── Base data: to'g'ridan DB ga yozish (auth bypass) ─────────────
@pytest_asyncio.fixture
async def base_data(db_engine):
    from datetime import date
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as session:
        branch = Branch(
            name="Test filial",
            code="TST",
            phone="+998901111111",
            address="Test manzil",
            city="Toshkent",
            is_active=True,
            opened_at=date(2024, 1, 1),
        )
        source = LeadSource(
            name="Instagram",
            monthly_budget=Decimal("1000000"),
            is_active=True
        )
        course = Course(
            name="Backend",
            price=Decimal("500000"),
            is_active=True
        )
        status = LeadStatus(
            name="Yangi",
            is_won=False,
            is_lost=False,
            position=1
        )
        session.add_all([branch, source, course, status])
        await session.commit()
        await session.refresh(branch)
        await session.refresh(source)
        await session.refresh(course)
        await session.refresh(status)

        return {
            "branch_id": branch.id,
            "source_id": source.id,
            "course_id": course.id,
            "status_id": status.id,
        }

# ── Helper ────────────────────────────────────────────────────────
async def create_lead(ac: AsyncClient, base_data: dict, phone: str = "+998901234567") -> int:
    resp = await ac.post(BASE + "/", json={
        "first_name": "Ali",
        "last_name": "Valiyev",
        "phone": phone,
        "branch_id": base_data["branch_id"],
        "source_id": base_data["source_id"],
        "course_id": base_data["course_id"],
        "status_id": base_data["status_id"],
    })
    assert resp.status_code in (200, 201), f"Create failed: {resp.text}"
    # MUHIM: router GET /leads/ ni Lead.id.desc() bo'yicha qaytaradi,
    # ya'ni items[0] - eng yangi lead, items[-1] - eng eski lead.
    # Shuning uchun yangi yaratilgan leadni olish uchun items[0] ishlatiladi.
    return (await ac.get(BASE + "/")).json()["items"][0]["id"]


async def create_student(db_engine, branch_id: int, phone: str = "+998907654321") -> int:
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as session:
        student = Student(
            first_name="Test", last_name="Student",
            phone=phone, parent_phone="+998900000000",
            branch_id=branch_id,
            status=StudentStatus.sinovda,
            balance=Decimal("0"),
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student.id


# ══════════════════════════════════════════════════════════════════
# POST /leads/
# ══════════════════════════════════════════════════════════════════
class TestAddLead:

    async def test_create_success(self, ac: AsyncClient, base_data: dict):
        resp = await ac.post(BASE + "/", json={
            "first_name": "Ali",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code in (200, 201)

    async def test_create_duplicate_phone_same_branch(self, ac: AsyncClient, base_data: dict):
        """Bir filialda bir xil telefon → 409"""
        await create_lead(ac, base_data, "+998901234567")
        resp = await ac.post(BASE + "/", json={
            "first_name": "Vali",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 409

    async def test_create_invalid_branch(self, ac: AsyncClient, base_data: dict):
        """Mavjud bo'lmagan branch → 404"""
        resp = await ac.post(BASE + "/", json={
            "first_name": "Ali",
            "phone": "+998909999999",
            "branch_id": 99999,
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 404

    async def test_create_invalid_source(self, ac: AsyncClient, base_data: dict):
        resp = await ac.post(BASE + "/", json={
            "first_name": "Ali",
            "phone": "+998909999999",
            "branch_id": base_data["branch_id"],
            "source_id": 99999,
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 404

    async def test_created_by_auto_set(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901234568")
        item = (await ac.get(BASE + "/")).json()["items"][0]
        assert item.get("created_by") == 1

    async def test_student_active_blocked(self, ac: AsyncClient, base_data: dict, db_engine):
        """Faol studentning raqami bilan lead yaratib bo'lmaydi"""
        await create_student(db_engine, base_data["branch_id"], "+998901234567")
        resp = await ac.post(BASE + "/", json={
            "first_name": "Ali",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 409


# ══════════════════════════════════════════════════════════════════
# GET /leads/
# ══════════════════════════════════════════════════════════════════
class TestGetLeads:

    async def test_get_empty(self, ac: AsyncClient):
        resp = await ac.get(BASE + "/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_get_all(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901111111")
        await create_lead(ac, base_data, "+998902222222")
        assert len((await ac.get(BASE + "/")).json()["items"]) == 2

    async def test_search_by_name(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901111111")
        resp = await ac.get(BASE + "/", params={"search": "Ali"})
        assert len(resp.json()["items"]) >= 1

    async def test_search_by_phone(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901111111")
        resp = await ac.get(BASE + "/", params={"search": "901111111"})
        assert len(resp.json()["items"]) == 1

    async def test_filter_by_status(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901111111")
        resp = await ac.get(BASE + "/", params={"status_id": base_data["status_id"]})
        assert len(resp.json()["items"]) >= 1

    async def test_filter_by_assigned_to(self, ac: AsyncClient, base_data: dict):
        await create_lead(ac, base_data, "+998901111111")
        resp = await ac.get(BASE + "/", params={"created_by": 1})
        assert len(resp.json()["items"]) >= 1

    async def test_pagination(self, ac: AsyncClient, base_data: dict):
        for i in range(5):
            await create_lead(ac, base_data, f"+99890111111{i}")
        data = (await ac.get(BASE + "/", params={"page": 1, "size": 2})).json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


# ══════════════════════════════════════════════════════════════════
# PUT /leads/{id}
# ══════════════════════════════════════════════════════════════════
class TestUpdateLead:

    async def test_update_success(self, ac: AsyncClient, base_data: dict):
        lid = await create_lead(ac, base_data, "+998901234567")
        resp = await ac.put(f"{BASE}/{lid}", json={
            "first_name": "Yangi Ism",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 200

    async def test_update_not_found(self, ac: AsyncClient, base_data: dict):
        resp = await ac.put(f"{BASE}/99999", json={
            "first_name": "Ali",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 404

    async def test_update_duplicate_phone(self, ac: AsyncClient, base_data: dict):
        """Boshqa leadning raqamini olish → 409"""
        await create_lead(ac, base_data, "+998901111111")          # Lead A
        lid = await create_lead(ac, base_data, "+998902222222")    # Lead B (eng yangi, items[0])
        resp = await ac.put(f"{BASE}/{lid}", json={
            "first_name": "Ali",
            "phone": "+998901111111",   # Lead A ning raqami
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 409

    async def test_update_same_phone_allowed(self, ac: AsyncClient, base_data: dict):
        """O'z raqamini o'zgartirmasdan update → 200"""
        lid = await create_lead(ac, base_data, "+998901234567")
        resp = await ac.put(f"{BASE}/{lid}", json={
            "first_name": "Yangi Ism",
            "phone": "+998901234567",
            "branch_id": base_data["branch_id"],
            "source_id": base_data["source_id"],
            "course_id": base_data["course_id"],
            "status_id": base_data["status_id"],
        })
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════════
# PATCH /leads/{id} — lead → student ga aylantirish
# ══════════════════════════════════════════════════════════════════
class TestConvertLead:

    async def test_convert_success(self, ac: AsyncClient, base_data: dict, db_engine):
        lid = await create_lead(ac, base_data, "+998901234567")
        sid = await create_student(db_engine, base_data["branch_id"], "+998907654321")
        resp = await ac.patch(f"{BASE}/{lid}", params={"student_id": sid})
        assert resp.status_code == 200

    async def test_convert_lead_not_found(self, ac: AsyncClient):
        resp = await ac.patch(f"{BASE}/99999", params={"student_id": 1})
        assert resp.status_code == 404

    async def test_convert_student_not_found(self, ac: AsyncClient, base_data: dict):
        lid = await create_lead(ac, base_data, "+998901234567")
        resp = await ac.patch(f"{BASE}/{lid}", params={"student_id": 99999})
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════
# DELETE /leads/{id}
# ══════════════════════════════════════════════════════════════════
class TestDeleteLead:

    async def test_delete_success(self, ac: AsyncClient, base_data: dict):
        lid = await create_lead(ac, base_data, "+998901234567")
        resp = await ac.delete(f"{BASE}/{lid}")
        assert resp.status_code == 200

    async def test_delete_not_found(self, ac: AsyncClient):
        resp = await ac.delete(f"{BASE}/99999")
        assert resp.status_code == 404

    async def test_deleted_not_in_list(self, ac: AsyncClient, base_data: dict):
        lid = await create_lead(ac, base_data, "+998901234567")
        await ac.delete(f"{BASE}/{lid}")
        ids = [i["id"] for i in (await ac.get(BASE + "/")).json()["items"]]
        assert lid not in ids