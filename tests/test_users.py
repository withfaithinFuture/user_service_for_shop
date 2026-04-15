from src.app.config import settings


async def test_get_me_success(client, auth_token):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["userId"] is not None
    assert data["login"] == settings.TEST_USER["login"]


async def test_get_me_unsuccess(client, auth_token):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token_123"}
    )

    assert response.status_code == 401


async def test_get_me_unauthorized(client):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
