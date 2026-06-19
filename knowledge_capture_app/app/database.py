from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pathlib import Path

try:
    from app.config import settings
except ModuleNotFoundError:
    from config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.database_url
if database_url.startswith("sqlite:///./"):
    project_root = Path(__file__).resolve().parent.parent
    relative_db = database_url.replace("sqlite:///./", "", 1)
    db_path = (project_root / relative_db).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{db_path}"

engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
