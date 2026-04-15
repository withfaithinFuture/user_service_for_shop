import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.app.application import get_app
from src.app.config import settings
from src.db.base_service import Base
from src.db.db import get_session

TEST_DATABASE_URL = settings.TEST_DATABASE_URL
TEST_USER = settings.TEST_USER

engine_test = create_async_engine(
    settings.TEST_DATABASE_URL, echo=False, poolclass=NullPool
)
session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    app = get_app()

    async def override_get_session():
        async with session_maker_test() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://tests"
    ) as asyncl:
        yield asyncl


@pytest.fixture
async def auth_token(client):
    await client.post("/api/v1/auth/register", json=TEST_USER)
    await asyncio.sleep(0.85)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"login": TEST_USER["login"], "password": TEST_USER["password"]},
    )

    return login_resp.json()["token"]
