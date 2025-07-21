import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Settings:
    Database_URL: str = os.getenv("DB_URL")

settings = Settings()
