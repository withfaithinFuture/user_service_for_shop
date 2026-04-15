import asyncio

from src.app.config import settings

TEST_USER = settings.TEST_USER


async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json=TEST_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["login"] == TEST_USER["login"]
    assert "token" in data


async def test_register_duplicate(client):
    await client.post("/api/v1/auth/register", json=TEST_USER)
    response = await client.post("/api/v1/auth/register", json=TEST_USER)
    assert response.status_code == 400
    assert response.json()["detail"] == "Пользователь с таким логином уже существует"


async def test_login_success(client):
    await client.post("/api/v1/auth/register", json=TEST_USER)
    await asyncio.sleep(1)
    response = await client.post(
        "/api/v1/auth/login",
        json={"login": TEST_USER["login"], "password": TEST_USER["password"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data


async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json=TEST_USER)
    response = await client.post(
        "/api/v1/auth/login",
        json={"login": TEST_USER["login"], "password": "lohsfdew122222222222"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"


async def test_get_me_success(client):
    reg_response = await client.post("/api/v1/auth/register", json=TEST_USER)
    token = reg_response.json()["token"]
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["login"] == TEST_USER["login"]
    assert data["firstName"] == TEST_USER["firstName"]
    assert data["isSeller"] is False


async def test_get_me_unauthorized(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
