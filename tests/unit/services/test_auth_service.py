from dataclasses import dataclass
from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Role
from app.security import get_password_hash
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)
from tests.factories.user import UserFactory


@dataclass(frozen=True)
class UserData:
    username: str
    email: str
    is_active: bool
    role: Role


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user",
    [
        UserData(
            username="mopuk",
            email="123@example.com",
            is_active=True,
            role=Role.customer,
        )
    ],
)
async def test_get_user_by_id(user: UserData, db_session: AsyncSession):

    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    db_session.add(new_user)
    await db_session.flush()

    found_user = await get_user_by_id(user_id=new_user.id, db=db_session)

    assert found_user is not None
    assert found_user.id == new_user.id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user",
    [
        UserData(
            username="mopuk",
            email="123@example.com",
            is_active=True,
            role=Role.customer,
        )
    ],
)
async def test_get_user_by_email(user: UserData, db_session: AsyncSession):
    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    db_session.add(new_user)
    await db_session.flush()

    found_user = await get_user_by_email(email=new_user.email, db=db_session)

    assert found_user is not None
    assert found_user.email == new_user.email
    assert found_user.id == new_user.id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user",
    [
        UserData(
            username="mopuk",
            email="123@example.com",
            is_active=True,
            role=Role.customer,
        )
    ],
)
async def test_get_user_by_username(user: UserData, db_session: AsyncSession):
    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    db_session.add(new_user)
    await db_session.flush()

    found_user = await get_user_by_username(username=new_user.username, db=db_session)

    assert found_user is not None
    assert found_user.username == new_user.username
    assert found_user.id == new_user.id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user,field",
    [
        (
            UserData(
                username="mopuk",
                email="123@example.com",
                is_active=True,
                role=Role.customer,
            ),
            ("email", "123@example.com"),
        )
    ],
)
async def test_get_user(
    user: UserData, field: tuple[str, str | int], db_session: AsyncSession
):
    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    db_session.add(new_user)
    await db_session.flush()

    found_user = await get_user(field=field[1], db=db_session)

    assert found_user is not None
    assert found_user.id == new_user.id

    match field[0]:
        case "username":
            assert found_user.username == new_user.username
        case "email":
            assert found_user.email == new_user.email


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user",
    [
        (
            UserData(
                username="mopuk",
                email="123@example.com",
                is_active=True,
                role=Role.customer,
            )
        )
    ],
)
async def test_get_current_user(user: UserData, db_session: AsyncSession):
    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    db_session.add(new_user)
    await db_session.flush()

    access_token = create_access_token(
        {"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=60),
    )

    found_user = await get_current_user(token=access_token, db=db_session)

    assert found_user is not None
    assert found_user.id == new_user.id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user,password",
    [
        (
            UserData(
                username="mopuk",
                email="123@example.com",
                is_active=True,
                role=Role.customer,
            ),
            "1234567889",
        )
    ],
)
async def test_authenticate_user(
    user: UserData, password: str, db_session: AsyncSession
):
    new_hashed_password = get_password_hash(password)
    new_user = UserFactory.build(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
        hashed_password=new_hashed_password,
    )
    db_session.add(new_user)
    await db_session.flush()

    found_user = await authenticate_user(new_user.username, password, db=db_session)

    assert found_user is not None
    assert found_user is not False
    assert found_user.id == new_user.id


@pytest.mark.anyio
async def test_user_lookup_returns_none_for_unknown_values(db_session: AsyncSession):
    assert await get_user_by_id(999, db_session) is None
    assert await get_user_by_email("missing@example.com", db_session) is None
    assert await get_user_by_username("missing-user", db_session) is None
    assert await get_user("missing@example.com", db_session) is None
    assert await get_user("missing-user", db_session) is None
    assert await get_user(999, db_session) is None


@pytest.mark.anyio
async def test_authenticate_user_rejects_wrong_and_unknown_credentials(
    db_session: AsyncSession,
):
    password = "correct1!"
    user = UserFactory.build(
        username="credential-user",
        email="credential@example.com",
        hashed_password=get_password_hash(password),
    )
    db_session.add(user)
    await db_session.flush()

    assert await authenticate_user(user.username, "incorrect1!", db_session) is False
    assert await authenticate_user("unknown-user", password, db_session) is False


@pytest.mark.anyio
async def test_get_current_user_rejects_expired_and_malformed_subject_tokens(
    db_session: AsyncSession,
):
    expired_token = create_access_token(
        {"sub": "1"}, expires_delta=timedelta(seconds=-1)
    )
    missing_subject_token = create_access_token({"aud": "shop"})
    malformed_subject_token = create_access_token({"sub": "not-an-id"})

    for token in (expired_token, missing_subject_token, malformed_subject_token):
        with pytest.raises(HTTPException) as error:
            await get_current_user(token=token, db=db_session)
        assert error.value.status_code == 401


@pytest.mark.anyio
async def test_get_current_user_reports_missing_user(db_session: AsyncSession):
    token = create_access_token({"sub": "987654"})

    with pytest.raises(HTTPException) as error:
        await get_current_user(token=token, db=db_session)

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_get_current_active_user_rejects_inactive_user(db_session: AsyncSession):
    user = UserFactory.build(
        username="inactive-service-user",
        email="inactive-service@example.com",
        is_active=False,
        role=Role.customer,
    )

    with pytest.raises(HTTPException) as error:
        await get_current_active_user(current_user=user)

    assert error.value.status_code == 403
