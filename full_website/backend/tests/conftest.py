import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import JSON
import sqlalchemy.dialects.postgresql

# Patch JSONB to be JSON for SQLite tests
sqlalchemy.dialects.postgresql.JSONB = JSON

from app.main import app
from app.db.session import get_db
from app.db.base_class import Base
from app.core.config import settings
# Import models to register them with Base.metadata
from app.models.user import User
from app.models.item import Item
from app.models.vendor import Vendor
from app.models.item_event import ItemEvent
from app.models.engraving import Engraving

from app.models.engraving import Engraving

import os
from sqlalchemy.pool import StaticPool

# Use Postgres for tests by default, but allow override (e.g. for CI with sqlite)
env_db_url = os.getenv("DATABASE_URL", "")
if "sqlite" in env_db_url or "test" in env_db_url:
    TEST_DATABASE_URL = env_db_url
else:
    TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/test_db"

if TEST_DATABASE_URL.startswith("postgresql://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
if "@localhost" in TEST_DATABASE_URL:
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("@localhost", "@db")

print(f"DEBUG: TEST_DATABASE_URL={TEST_DATABASE_URL}")

@pytest_asyncio.fixture
async def test_engine():
    # Handle SQLite specific configuration for in-memory tests
    if "sqlite" in TEST_DATABASE_URL:
        engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
    else:
        engine = create_async_engine(
            TEST_DATABASE_URL, 
            echo=False,
        )
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        def check_tables(conn):
            from sqlalchemy import inspect
            inspector = inspect(conn)
            print(f"Tables in DB after create: {inspector.get_table_names()}")
        await conn.run_sync(check_tables)
    
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
