import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.auth.security import get_password_hash
import uuid

@pytest.fixture
async def admin_token(client: AsyncClient, db_session: AsyncSession):
    email = f"admin_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        username=email,
        password_hash=get_password_hash("password"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    response = await client.post(
        "/auth/login",
        json={"username": email, "password": "password"}
    )
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_and_get_item(client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create Item
    item_data = {
        "uid": "ITEM-001",
        "component_type": "Resistor",
        "lot_no": "LOT-123",
        "status": "In Stock"
    }
    response = await client.post("/items/", json=item_data, headers=headers)
    assert response.status_code == 200
    created_item = response.json()
    assert created_item["uid"] == "ITEM-001"
    
    # Get Item
    response = await client.get("/items/ITEM-001", headers=headers)
    assert response.status_code == 200
    assert response.json()["uid"] == "ITEM-001"
