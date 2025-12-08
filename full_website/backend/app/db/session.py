# backend/app/db/session.py
# Purpose: Database session and engine configuration
# Author: Antigravity

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Create engine with database-specific connection arguments
# For SQLite: no cache options
# For PostgreSQL: disable prepared statements for Supabase connection pooler (PgBouncer)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support statement_cache_size
    connect_args = {}
else:
    # PostgreSQL with connection pooler
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
