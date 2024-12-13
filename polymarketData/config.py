import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv('POLYGON_API_KEY')
    DB_URL = os.getenv('SINGLESTORE_DB_URL')
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '8'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '5'))  # requests per second
