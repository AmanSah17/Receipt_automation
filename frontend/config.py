import os
import json
from streamlit_lottie import st_lottie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "processed_receipts.db")

# Sync URL for sqlite3 / SQLAlchemy engine
SQLITE_URL = f"sqlite:///{DB_PATH}"

# Async URL for FastAPI (databases package)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"




def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
   
''' 
lottie_animation = "frontend\static\Accounting.json"
st_lottie(
    lottie_animation,
    speed=1,
    reverse=False,
    loop=True,
    quality="high",
    height=320,
    width=400,
    key="lottie_animation",
) 

'''