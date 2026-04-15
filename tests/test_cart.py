from uuid import uuid4

import httpx
import respx
from httpx import Response

from src.app.config import settings

TEST_USER = settings.TEST_USER
TEST_PRODUCT_ID = str(uuid4())
TEST_MARKET_ID = str(uuid4())
SELLER_SERVICE_URL = settings.SELLER_SERVICE_URL
MOCK_SELLER_PRODUCTS: list = [
    {
        "id": TEST_PRODUCT_ID,
        "name": "Игровая приставка",
        "price": 75000.0,
        "available": 50,
        "marketId": TEST_MARKET_ID,
    }
]

MOCK_SELLER_RESPONSE = [
    {
        "id": TEST_PRODUCT_ID,
        "name": "Тестовый iPhone 15",
        "price": 100000.50,
        "available": 10,
        "img": "test.jpg",
        "market": {"marketId": str(uuid4()), "marketName": "Apple Store"},
    }
]


@respx.mock
async def test_seller_service_unavailable(client, auth_token):
    respx.post(f"{SELLER_SERVICE_URL}/products/by-ids").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    response = await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 1},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Сервис товаров временно недоступен"


@respx.mock
async def test_add_to_cart_success(client, auth_token):
    respx.post(f"{SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    response = await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 2},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["cartCount"] == 2


@respx.mock
async def test_update_cart_item_quantity(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").respond(
        200, json=MOCK_SELLER_PRODUCTS
    )

    await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 1},
    )

    response = await client.patch(
        f"/api/v1/cart/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 5},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cartCount"] == 5


@respx.mock
async def test_add_to_cart_first_time(client, auth_token):
    route = respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids")
    route.respond(200, json=MOCK_SELLER_PRODUCTS)

    respx.route(url__startswith=settings.SELLER_SERVICE_URL).pass_through = False

    response = await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 1},
    )
    assert response.status_code == 201


@respx.mock
async def test_add_to_cart_product_not_found(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=[])
    )

    response = await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 1},
    )

    assert response.status_code == 404


@respx.mock
async def test_add_to_cart_not_enough_stock(client, auth_token):
    respx.post(f"{SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    response = await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 15},
    )

    assert response.status_code == 400
    assert response.json() is not None


async def test_add_to_cart_validation_error(client, auth_token):
    response = await client.patch(
        f"/api/v1/cart/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": "[sda[dsa[dsa[d[sad[as]"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_cart_success(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 2},
    )

    response = await client.get(
        "/api/v1/cart/", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totalPrice"] == 100000.50 * 2
    assert len(data["items"]) == 1
    assert data["items"][0]["productId"] == TEST_PRODUCT_ID
    assert data["items"][0]["name"] == "Тестовый iPhone 15"


async def test_get_cart_unauthorized(client):
    response = await client.get("/api/v1/cart/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_cart_empty(client, auth_token):
    response = await client.get(
        "/api/v1/cart/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["totalPrice"] == 0.0


@respx.mock
async def test_update_cart_item(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 2},
    )

    response = await client.patch(
        f"/api/v1/cart/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 5},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cartCount"] == 5
    assert data["totalPrice"] == 100000.50 * 5


@respx.mock
async def test_update_cart_item_not_found(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=[])
    )

    response = await client.patch(
        f"/api/v1/cart/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 5},
    )

    assert response.status_code == 404


@respx.mock
async def test_update_cart_item_not_enough_stock(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    response = await client.patch(
        f"/api/v1/cart/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 5555555555555},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "not_enough_stock"


@respx.mock
async def test_delete_cart_item(client, auth_token):
    respx.post(f"{settings.SELLER_SERVICE_URL}/products/by-ids").mock(
        return_value=Response(200, json=MOCK_SELLER_RESPONSE)
    )

    await client.post(
        "/api/v1/cart/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"productId": TEST_PRODUCT_ID, "quantity": 2},
    )

    response = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cartCount"] == 0
    assert data["totalPrice"] == 0.0


async def test_delete_cart_item_no_cart(client, auth_token):
    response = await client.delete(
        f"/api/v1/cart/item/{TEST_PRODUCT_ID}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["cartCount"] == 0


async def test_delete_cart_item_not_found(client, auth_token):
    fake_uuid = str(uuid4())

    response = await client.delete(
        f"/api/v1/cart/item/{fake_uuid}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code in [200, 404]
