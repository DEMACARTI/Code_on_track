from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from pathlib import Path

# Create a directory for the test database
test_db_dir = "test_db"
os.makedirs(test_db_dir, exist_ok=True)

# Use SQLite for testing
TEST_DB_URL = f"sqlite:///{os.path.join(test_db_dir, 'test.db')}"

# Create test database engine
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the test database with tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get DB session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database when this module is imported
init_db()
