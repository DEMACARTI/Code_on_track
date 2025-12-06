import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.auth.security import get_password_hash
import uuid

@pytest.fixture
async def admin_token_import(client: AsyncClient, db_session: AsyncSession):
    email = f"import_admin_{uuid.uuid4()}@example.com"
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
async def test_import_items(client: AsyncClient, admin_token_import: str):
    headers = {"Authorization": f"Bearer {admin_token_import}"}
    
    csv_content = "uid,component_type,lot_no\nIMP-001,Capacitor,LOT-999\nIMP-002,Resistor,LOT-888"
    files = {"file": ("items.csv", csv_content, "text/csv")}
    
    # Preview (commit=false)
    response = await client.post(
        "/api/import/items",
        files=files,
        data={"commit": "false"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 2
    assert data["valid_rows"] == 2
    
    # Commit (commit=true)
    # Re-create files because stream is consumed
    files = {"file": ("items.csv", csv_content, "text/csv")}
    response = await client.post(
        "/api/import/items",
        files=files,
        data={"commit": "true"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["created_items"]) == 2
    
    # Verify DB
    response = await client.get("/items/IMP-001", headers=headers)
    assert response.status_code == 200
