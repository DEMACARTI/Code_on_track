import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import Item, EngravingQueue, EngravingHistory

def init_database():
    """Initialize the database by creating all tables."""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        print("\nCreated tables:")
        print("- items")
        print("- engraving_queue")
        print("- engraving_history")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_database()
