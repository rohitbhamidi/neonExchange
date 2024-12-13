import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class that loads environment variables and settings.
    """
    # Load the SingleStoreDB URL from the environment variables
    SINGLESTORE_DB_URL = os.environ.get("SINGLESTORE_DB_URL", "")
    # Additional configuration variables can be added here as needed.
