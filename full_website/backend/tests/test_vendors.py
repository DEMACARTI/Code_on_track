import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_create_vendor_as_admin(async_client: AsyncClient, admin_token_headers):
    response = await async_client.post(
        "/vendors/",
        json={"name": "Test Vendor", "contact_info": {"email": "test@example.com"}},
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Vendor"
    assert data["contact_info"]["email"] == "test@example.com"
    assert data["items_count"] == 0
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_list_vendors(async_client: AsyncClient, admin_token_headers):
    # Create a vendor first
    await async_client.post(
        "/vendors/",
        json={"name": "Vendor 1"},
        headers=admin_token_headers,
    )
    
    response = await async_client.get("/vendors/", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "items_count" in data[0]

@pytest.mark.asyncio
async def test_create_vendor_as_viewer_fails(async_client: AsyncClient, viewer_token_headers):
    response = await async_client.post(
        "/vendors/",
        json={"name": "Viewer Vendor"},
        headers=viewer_token_headers,
    )
    assert response.status_code == 403
