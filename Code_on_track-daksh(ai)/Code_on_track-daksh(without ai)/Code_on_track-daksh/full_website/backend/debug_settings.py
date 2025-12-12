import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

print(f"CWD: {os.getcwd()}")
print(f"DB URL: {settings.DATABASE_URL}")
print("Env vars keys:", [k for k in os.environ.keys() if 'POSTGRES' in k])
