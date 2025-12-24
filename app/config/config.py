import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "crm")


    ollama_url: str = os.getenv("OLLAMA_URL", "")
    model: str = os.getenv("MODEL", "")
    model_dir = os.getenv("MODEL_DIR", "data/models")

settings = Settings()
