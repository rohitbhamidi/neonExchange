import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class that loads environment variables and settings.
    """
    SINGLESTORE_DB_URL = os.environ.get("SINGLESTORE_DB_URL", "")
