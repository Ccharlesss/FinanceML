from src.Unit_test.configtest import USER_NAME, USER_EMAIL, USER_PASSWORD
import pytest


@pytest.mark.asyncio
async def test_create_user_account(client):
    data = {"username": USER_NAME, "email": USER_EMAIL, "password": USER_PASSWORD}
    response = await client.post("/users/signup", json=data)
    assert response.status_code == 201
    assert "password" not in response.json()


