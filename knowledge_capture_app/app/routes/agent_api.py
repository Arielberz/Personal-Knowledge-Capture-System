from datetime import datetime
from pathlib import Path
from shutil import copyfileobj

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from app.database import get_db
    from app.models import AgentDecision, AgentRun, Capture
    from app.services.ai_service import processIncomingContent
    from app.services.ai_service import analyze_image_for_capture
    from app.services.agent_service import run_scan
    from app.services.topic_router import route_topic
except ModuleNotFoundError:
    from database import get_db
    from models import AgentDecision, AgentRun, Capture
    from services.ai_service import processIncomingContent
    from services.ai_service import analyze_image_for_capture
    from services.agent_service import run_scan
    from services.topic_router import route_topic

router = APIRouter(prefix="/api/agent", tags=["agent"])
knowledge_router = APIRouter(prefix="/api", tags=["knowledge"])


class KnowledgeRequest(BaseModel):
    rawText: str


class KnowledgeResponse(BaseModel):
    title: str
    summary: str
    tags: list[str]
    category: str


class UploadKnowledgeResponse(BaseModel):
    id: int
    title: str
    summary: str
    main_topic_id: int | None
    image_url: str


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


@knowledge_router.post("/knowledge", response_model=KnowledgeResponse)
def process_knowledge(payload: KnowledgeRequest) -> KnowledgeResponse:
    try:
        result = processIncomingContent(payload.rawText)
        return KnowledgeResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI service failed to process incoming content") from exc


@knowledge_router.post("/knowledge/upload", response_model=UploadKnowledgeResponse)
def upload_knowledge_image(
    title: str = Form(...),
    summary: str = Form(default=""),
    topic_id: int | None = Form(default=None),
    knowledge_score: int = Form(default=6),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadKnowledgeResponse:
    suffix = Path(image.filename or "").suffix
    unique_name = f"{int(datetime.utcnow().timestamp() * 1000)}{suffix}"

    uploads_dir = Path(__file__).resolve().parent.parent.parent / "data" / "inbox" / "images"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    destination = uploads_dir / unique_name
    with destination.open("wb") as f:
        copyfileobj(image.file, f)

    generated_analysis = analyze_image_for_capture(destination)

    final_topic_id = topic_id
    if final_topic_id is None:
        topic_blob_parts = [
            title,
            summary,
            image.filename or unique_name,
            str(generated_analysis.get("summary", "")),
            str(generated_analysis.get("category", "")),
        ]
        maybe_tags = generated_analysis.get("tags")
        if isinstance(maybe_tags, list):
            topic_blob_parts.append(" ".join(str(tag) for tag in maybe_tags))
        auto_topic = route_topic(db, "image", " ".join(part for part in topic_blob_parts if part))
        final_topic_id = auto_topic.id if auto_topic else None

    resolved_title = title.strip() or str(generated_analysis.get("title", "")).strip() or unique_name
    normalized_summary = summary.strip() or str(generated_analysis.get("summary", "")).strip() or f"{resolved_title} (image upload)"

    confidence = str(generated_analysis.get("confidence", "")).strip().lower()
    if confidence not in {"low", "medium", "high"}:
        confidence = "medium"

    computed_score = generated_analysis.get("knowledge_score")
    try:
        final_score = int(computed_score)
    except (TypeError, ValueError):
        final_score = knowledge_score

    relative_path = f"data/inbox/images/{unique_name}"
    capture = Capture(
        source_type="image",
        file_path=relative_path,
        original_filename=unique_name,
        title=resolved_title,
        summary=normalized_summary,
        main_topic_id=final_topic_id,
        knowledge_score=max(1, min(10, final_score)),
        confidence=confidence,
        status="pending_review",
    )
    db.add(capture)
    db.commit()
    db.refresh(capture)

    return UploadKnowledgeResponse(
        id=capture.id,
        title=capture.title,
        summary=capture.summary,
        main_topic_id=capture.main_topic_id,
        image_url=f"/inbox-images/{unique_name}",
    )
