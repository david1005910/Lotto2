import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'lotto_data.db'}")
DB_PATH = BASE_DIR / "data" / "lotto_data.db"

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# External API
DHLOTTERY_API_URL = os.getenv(
    "DHLOTTERY_API_URL",
    "https://www.dhlottery.co.kr/common.do"
)
CURRENT_DRAW_NO = int(os.getenv("CURRENT_DRAW_NO", "1202"))

# CORS
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

# ML Models
MODEL_PATH = BASE_DIR / os.getenv("MODEL_PATH", "ml_models")
