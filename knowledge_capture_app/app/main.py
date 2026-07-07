from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

try:
    from app.config import settings
    from app.database import Base, SessionLocal, engine
    from app.routes.agent_api import knowledge_router, router as agent_api_router
    from app.routes.web import router as web_router
    from app.seed import seed_if_empty
except ModuleNotFoundError:
    from config import settings
    from database import Base, SessionLocal, engine
    from routes.agent_api import knowledge_router, router as agent_api_router
    from routes.web import router as web_router
    from seed import seed_if_empty


app = FastAPI(title=settings.app_name)
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/inbox-images", StaticFiles(directory=str(PROJECT_ROOT / "data" / "inbox" / "images")), name="inbox-images")
app.include_router(web_router)
app.include_router(agent_api_router)
app.include_router(knowledge_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
