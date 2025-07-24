import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Settings:
    Database_URL: str = os.getenv("DB_URL")
    Secret_Key: str = os.getenv("SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    HF_Token: str = os.getenv("HF_TOKEN")
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EMBEDDINGS_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "../data/embeddings"))
    

settings = Settings()
