import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Settings:
    Database_URL: str = os.getenv("DB_URL")
    Secret_Key: str = os.getenv("SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    HF_Token: str = os.getenv("HF_TOKEN")
    Google_key = os.getenv("GOOGLE_API_KEY")
    Groq_key = os.getenv("GROQ_API_KEY")
    Eleven_key = os.getenv("ELEVEN_LABS")

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JSON_EMBEDDINGS_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "../data/embeddings"))
    CSV_EMBEDDINGS_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "../data/csv_embeddings"))

    BASE_URL = "http://localhost:8000" 
    

settings = Settings()
