import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class for environment variables and settings.
    """
    SINGLESTORE_DB_URL = os.environ.get("SINGLESTORE_DB_URL", "")
    UPDATE_INTERVAL_MS = 2000  # 2 seconds for real-time updates
