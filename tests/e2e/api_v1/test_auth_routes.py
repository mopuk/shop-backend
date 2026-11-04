
from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserModel
from app.security import get_password_hash
from app.services.auth import create_access_token


@pytest.mark.anyio
async def test_register_login_and_get_current_user(async_client: AsyncClient):
    registration = {
        "username": "route-customer",
        "email": "route-customer@example.com",
        "password": "secure1!",
    }

    response = await async_client.post("/api/v1/auth/register", json=registration)

    assert response.status_code == 200
    token = response.json()
    assert token["token_type"] == "bearer"
    assert token["access_token"]

    me_response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == registration["username"]
    assert me_response.json()["email"] == registration["email"]
    assert "hashed_password" not in me_response.json()

    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": registration["username"],
            "password": registration["password"],
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("registration", "expected_status", "expected_detail"),
    [
        (
            {
                "username": "weak-password",
                "email": "weak@example.com",
                "password": "short",
            },
            403,
            "Password does not meet the requirements",
        ),
        (
            {
                "username": "no-symbol",
                "email": "no-symbol@example.com",
                "password": "secure123",
            },
            403,
            "Password does not meet the requirements",
        ),
        (
            {
                "username": "no-digit",
                "email": "no-digit@example.com",
                "password": "secure!!",
            },
            403,
            "Password does not meet the requirements",
        ),
    ],
)
async def test_register_rejects_weak_passwords(
    async_client: AsyncClient,
    registration: dict[str, str],
    expected_status: int,
    expected_detail: str,
):
    response = await async_client.post("/api/v1/auth/register", json=registration)

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


@pytest.mark.anyio
async def test_register_rejects_duplicate_username_and_email(
    async_client: AsyncClient,
):
    registration = {
        "username": "duplicate-user",
        "email": "duplicate@example.com",
        "password": "secure1!",
    }
    response = await async_client.post("/api/v1/auth/register", json=registration)
    assert response.status_code == 200

    duplicate_username = await async_client.post(
        "/api/v1/auth/register",
        json={**registration, "email": "another@example.com"},
    )
    duplicate_email = await async_client.post(
        "/api/v1/auth/register",
        json={**registration, "username": "another-user"},
    )

    assert duplicate_username.status_code == 409
    assert duplicate_username.json()["detail"] == "Username already registered"
    assert duplicate_email.status_code == 409
    assert duplicate_email.json()["detail"] == "Email already registered"


@pytest.mark.anyio
async def test_login_rejects_invalid_credentials(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "missing-user", "password": "incorrect"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.anyio
async def test_me_requires_a_valid_active_user(async_client: AsyncClient):
    missing_token = await async_client.get("/api/v1/auth/me")
    invalid_token = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}
    )

    assert missing_token.status_code == 401
    assert invalid_token.status_code == 401


@pytest.mark.anyio
async def test_me_rejects_inactive_user(
    async_client: AsyncClient, db_session: AsyncSession
):
    user = UserModel(
        username="inactive-user",
        email="inactive@example.com",
        hashed_password=get_password_hash("secure1!"),
        is_active=False,
        role="customer",
    )
    db_session.add(user)
    await db_session.flush()
    token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=10)
    )

    response = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user"