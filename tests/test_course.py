import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database.Base import Base
from app.database.connation import get_db


TEST_DB_URL = "mysql+aiomysql://root:1234@localhost/tstdb"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_engine):
    TestSession = async_sessionmaker(
        db_engine,
        expire_on_commit=False
    )

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# =========================
# POST /courses/
# =========================

@pytest.mark.asyncio
async def test_add_course(client):
    response = await client.post(
        "/courses/",
        json={
            "name": "Python"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Course Added"}


@pytest.mark.asyncio
async def test_add_duplicate_course(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    response = await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Course already exists"


@pytest.mark.asyncio
async def test_add_course_with_different_case(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    response = await client.post(
        "/courses/",
        json={"name": "python"}
    )

    assert response.status_code == 400


# =========================
# GET /courses/
# =========================

@pytest.mark.asyncio
async def test_get_courses(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    response = await client.get("/courses/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Python"


@pytest.mark.asyncio
async def test_get_courses_by_name(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )
    await client.post(
        "/courses/",
        json={"name": "Java"}
    )

    response = await client.get(
        "/courses/",
        params={"course_name": "Pyt"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Python"


@pytest.mark.asyncio
async def test_get_courses_by_active_status(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    response = await client.get(
        "/courses/",
        params={"is_active": True}
    )

    assert response.status_code == 200
    assert all(course["is_active"] is True for course in response.json())


# =========================
# PUT /courses/{course_id}
# =========================

@pytest.mark.asyncio
async def test_update_course(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    courses_response = await client.get("/courses/")
    course_id = courses_response.json()[0]["id"]

    response = await client.put(
        f"/courses/{course_id}",
        json={"name": "Advanced Python"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Course Updated"}

    updated_response = await client.get("/courses/")
    assert updated_response.json()[0]["name"] == "Advanced Python"


@pytest.mark.asyncio
async def test_update_nonexistent_course(client):
    response = await client.put(
        "/courses/99999",
        json={"name": "Advanced Python"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# =========================
# PATCH /courses/{course_id}
# =========================

@pytest.mark.asyncio
async def test_patch_course_status(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    courses_response = await client.get("/courses/")
    course_id = courses_response.json()[0]["id"]

    response = await client.patch(
        f"/courses/{course_id}?body=false"
    )

    assert response.status_code == 200
    assert response.json() == {"msg": "Course Updated"}

    updated_response = await client.get("/courses/")

    assert updated_response.json()[0]["is_active"] is False


@pytest.mark.asyncio
async def test_patch_nonexistent_course(client):
    response = await client.patch(
        "/courses/99999?body=false"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# =========================
# DELETE /courses/{course_id}
# =========================

@pytest.mark.asyncio
async def test_delete_course(client):
    await client.post(
        "/courses/",
        json={"name": "Python"}
    )

    courses_response = await client.get("/courses/")
    course_id = courses_response.json()[0]["id"]

    response = await client.delete(
        f"/courses/{course_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Course deleted successfully"
    }

    remaining_courses = await client.get("/courses/")
    assert len(remaining_courses.json()) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_course(client):
    response = await client.delete("/courses/99999")

    assert response.status_code == 404