from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from app.database import get_db
    from app.models import AgentDecision, AgentRun
    from app.services.agent_service import run_scan
except ModuleNotFoundError:
    from database import get_db
    from models import AgentDecision, AgentRun
    from services.agent_service import run_scan

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/scan")
def scan_agent(db: Session = Depends(get_db)) -> dict:
    summary = run_scan(db)
    return {
        "run_id": summary.run_id,
        "files_found": summary.files_found,
        "files_processed": summary.files_processed,
        "files_failed": summary.files_failed,
    }


@router.get("/runs")
def get_runs(db: Session = Depends(get_db)) -> list[dict]:
    runs = db.scalars(select(AgentRun).order_by(AgentRun.started_at.desc()).limit(20)).all()
    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "status": run.status,
            "files_found": run.files_found,
            "files_processed": run.files_processed,
            "files_failed": run.files_failed,
        }
        for run in runs
    ]


@router.get("/decisions")
def get_decisions(db: Session = Depends(get_db)) -> list[dict]:
    decisions = db.scalars(select(AgentDecision).order_by(AgentDecision.created_at.desc()).limit(100)).all()
    return [
        {
            "id": d.id,
            "capture_id": d.capture_id,
            "suggested_topic": d.suggested_topic,
            "suggested_status": d.suggested_status,
            "knowledge_score": d.knowledge_score,
            "confidence": d.confidence,
            "reason_for_topic": d.reason_for_topic,
            "reason_for_score": d.reason_for_score,
            "approved_by_user": d.approved_by_user,
            "user_correction": d.user_correction,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in decisions
    ]
