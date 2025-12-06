import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.auth.security import get_password_hash

import uuid

@pytest.mark.asyncio
async def test_login(client: AsyncClient, db_session: AsyncSession):
    # Seed user
    email = f"test_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        username=email,
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # Test login
    response = await client.post(
        "/auth/login",
        json={"username": email, "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
