from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Knowledge Capture Dashboard")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./database/knowledge.db")


settings = Settings()
