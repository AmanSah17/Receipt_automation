import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "processed_receipts.db")

# Sync URL for sqlite3 / SQLAlchemy engine
SQLITE_URL = f"sqlite:///{DB_PATH}"

# Async URL for FastAPI (databases package)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"




