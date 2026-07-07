from datetime import datetime
from pathlib import Path
from shutil import copyfileobj

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

try:
    from app.database import get_db
    from app.models import AgentDecision, AgentRun, AllowedSource, Capture, OpenQuestion, ProcessingLog, Reminder, SourceFile, Topic
    from app.services.agent_service import run_scan
    from app.services.ai_service import analyze_image_for_capture
    from app.services.topic_router import route_topic
except ModuleNotFoundError:
    from database import get_db
    from models import AgentDecision, AgentRun, AllowedSource, Capture, OpenQuestion, ProcessingLog, Reminder, SourceFile, Topic
    from services.agent_service import run_scan
    from services.ai_service import analyze_image_for_capture
    from services.topic_router import route_topic

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _enabled_source_prefixes(db: Session) -> list[str]:
    rows = db.scalars(select(AllowedSource).where(AllowedSource.enabled.is_(True))).all()
    return [row.path_prefix.strip() for row in rows]


def _is_path_allowed(source_path: str, allowed_prefixes: list[str]) -> bool:
    normalized = source_path.strip()
    return any(normalized.startswith(prefix) for prefix in allowed_prefixes)


@router.get("/")
def dashboard(
    request: Request,
    topic_id: int | None = Query(default=None),
    min_score: int = Query(default=1, ge=1, le=10),
    db: Session = Depends(get_db),
):
    capture_query = select(Capture).where(Capture.knowledge_score >= min_score)
    if topic_id is not None:
        capture_query = capture_query.where(Capture.main_topic_id == topic_id)
    latest_captures = db.scalars(capture_query.order_by(Capture.processed_at.desc()).limit(12)).all()

    topics = db.scalars(select(Topic).order_by(Topic.name)).all()
    open_questions_count = db.scalar(select(func.count(OpenQuestion.id)))
    pending_reminders_count = db.scalar(select(func.count(Reminder.id)).where(Reminder.status == "pending"))
    captures_count = db.scalar(select(func.count(Capture.id)))

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "latest_captures": latest_captures,
            "topics": topics,
            "selected_topic": topic_id,
            "min_score": min_score,
            "stats": {
                "captures": captures_count,
                "questions": open_questions_count,
                "reminders": pending_reminders_count,
            },
        },
    )


@router.get("/captures")
def captures(
    request: Request,
    topic_id: int | None = Query(default=None),
    min_score: int = Query(default=1, ge=1, le=10),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Capture).where(Capture.knowledge_score >= min_score)
    if topic_id is not None:
        query = query.where(Capture.main_topic_id == topic_id)
    if status:
        query = query.where(Capture.status == status)

    captures_data = db.scalars(query.order_by(Capture.processed_at.desc())).all()
    topics = db.scalars(select(Topic).order_by(Topic.name)).all()

    return templates.TemplateResponse(
        "captures.html",
        {
            "request": request,
            "captures": captures_data,
            "topics": topics,
            "selected_topic": topic_id,
            "min_score": min_score,
            "selected_status": status,
        },
    )


@router.get("/topics")
def topics(request: Request, db: Session = Depends(get_db)):
    topics_data = db.scalars(select(Topic).order_by(Topic.name)).all()
    return templates.TemplateResponse("topics.html", {"request": request, "topics": topics_data})


@router.get("/topics/{topic_id}")
def topic_detail(topic_id: int, request: Request, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    captures_data = db.scalars(
        select(Capture).where(Capture.main_topic_id == topic_id).order_by(Capture.processed_at.desc())
    ).all()
    questions_data = db.scalars(select(OpenQuestion).where(OpenQuestion.topic_id == topic_id)).all()
    reminders_data = db.scalars(
        select(Reminder).where(Reminder.topic_id == topic_id).order_by(Reminder.due_date.asc())
    ).all()

    return templates.TemplateResponse(
        "topic_detail.html",
        {
            "request": request,
            "topic": topic,
            "captures": captures_data,
            "questions": questions_data,
            "reminders": reminders_data,
        },
    )


@router.get("/questions")
def questions(request: Request, db: Session = Depends(get_db)):
    questions_data = db.scalars(select(OpenQuestion).order_by(OpenQuestion.importance_score.desc())).all()
    return templates.TemplateResponse("questions.html", {"request": request, "questions": questions_data})


@router.get("/reminders")
def reminders(request: Request, db: Session = Depends(get_db)):
    reminders_data = db.scalars(select(Reminder).order_by(Reminder.due_date.asc())).all()
    return templates.TemplateResponse("reminders.html", {"request": request, "reminders": reminders_data})


@router.get("/add-data")
def add_data_page(request: Request, db: Session = Depends(get_db)):
    topics = db.scalars(select(Topic).order_by(Topic.name)).all()
    allowed_sources = db.scalars(select(AllowedSource).order_by(AllowedSource.path_prefix.asc())).all()
    return templates.TemplateResponse(
        "add_data.html",
        {
            "request": request,
            "topics": topics,
            "allowed_sources": allowed_sources,
            "message": None,
            "error": None,
        },
    )


@router.post("/add-data")
def add_data_submit(
    request: Request,
    title: str = Form(...),
    summary: str = Form(default=""),
    source_path: str = Form(default=""),
    image_file: UploadFile | None = File(default=None),
    topic_id: str | None = Form(default=None),
    knowledge_score: int = Form(default=6),
    db: Session = Depends(get_db),
):
    topics = db.scalars(select(Topic).order_by(Topic.name)).all()
    allowed_sources = db.scalars(select(AllowedSource).order_by(AllowedSource.path_prefix.asc())).all()
    enabled_prefixes = _enabled_source_prefixes(db)

    parsed_topic_id: int | None = None
    if topic_id is not None and topic_id.strip() != "":
        try:
            parsed_topic_id = int(topic_id)
        except ValueError:
            return templates.TemplateResponse(
                "add_data.html",
                {
                    "request": request,
                    "topics": topics,
                    "allowed_sources": allowed_sources,
                    "message": None,
                    "error": "ערך topic_id לא תקין. יש לבחור נושא מהרשימה או להשאיר ריק.",
                },
            )

    effective_source_path = source_path.strip()
    source_type = "manual_note"
    generated_analysis: dict[str, str | int] | None = None

    if image_file and image_file.filename:
        uploads_dir = Path(__file__).resolve().parent.parent.parent / "data" / "inbox" / "images"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(image_file.filename).suffix
        unique_name = f"{int(datetime.utcnow().timestamp() * 1000)}{suffix}"
        destination = uploads_dir / unique_name

        with destination.open("wb") as f:
            copyfileobj(image_file.file, f)

        generated_analysis = analyze_image_for_capture(destination)
        effective_source_path = f"data/inbox/images/{unique_name}"
        source_type = "image"

    if not effective_source_path:
        return templates.TemplateResponse(
            "add_data.html",
            {
                "request": request,
                "topics": topics,
                "allowed_sources": allowed_sources,
                "message": None,
                "error": "יש להזין נתיב מקור או להעלות קובץ תמונה.",
            },
        )

    if not _is_path_allowed(effective_source_path, enabled_prefixes):
        return templates.TemplateResponse(
            "add_data.html",
            {
                "request": request,
                "topics": topics,
                "allowed_sources": allowed_sources,
                "message": None,
                "error": "נתיב המקור לא מורשה במדיניות הנוכחית. יש להוסיף או להפעיל אותו קודם במסך הרשאות גישה.",
            },
        )

    if parsed_topic_id is None:
        topic_blob_parts = [title, summary, effective_source_path]
        if generated_analysis:
            topic_blob_parts.append(str(generated_analysis.get("summary", "")))
            topic_blob_parts.append(str(generated_analysis.get("category", "")))
            maybe_tags = generated_analysis.get("tags")
            if isinstance(maybe_tags, list):
                topic_blob_parts.append(" ".join(str(tag) for tag in maybe_tags))
        auto_topic = route_topic(db, source_type, " ".join(part for part in topic_blob_parts if part))
        parsed_topic_id = auto_topic.id if auto_topic else None

    file_name = Path(effective_source_path).name if effective_source_path else f"manual_{datetime.utcnow().timestamp()}"
    resolved_title = title.strip()
    if not resolved_title and generated_analysis:
        resolved_title = str(generated_analysis.get("title", "")).strip()
    if not resolved_title:
        resolved_title = file_name

    normalized_summary = summary.strip()
    if not normalized_summary and generated_analysis:
        normalized_summary = str(generated_analysis.get("summary", "")).strip()
    if not normalized_summary:
        normalized_summary = f"{resolved_title} ({source_type})"

    confidence = "manual"
    if generated_analysis:
        generated_confidence = str(generated_analysis.get("confidence", "")).strip().lower()
        if generated_confidence in {"low", "medium", "high"}:
            confidence = generated_confidence

    capture = Capture(
        source_type=source_type,
        file_path=effective_source_path,
        original_filename=file_name,
        title=resolved_title,
        summary=normalized_summary,
        main_topic_id=parsed_topic_id,
        knowledge_score=max(1, min(10, knowledge_score)),
        confidence=confidence,
        status="pending_review",
    )
    db.add(capture)
    db.commit()

    return templates.TemplateResponse(
        "add_data.html",
        {
            "request": request,
            "topics": topics,
            "allowed_sources": allowed_sources,
            "message": "הפריט נשמר בהצלחה.",
            "error": None,
        },
    )


@router.get("/access-policy")
def access_policy_page(request: Request, db: Session = Depends(get_db)):
    policies = db.scalars(select(AllowedSource).order_by(AllowedSource.path_prefix.asc())).all()
    return templates.TemplateResponse(
        "access_policy.html",
        {
            "request": request,
            "policies": policies,
        },
    )


@router.post("/access-policy/add")
def access_policy_add(
    path_prefix: str = Form(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
):
    normalized = path_prefix.strip()
    existing = db.scalar(select(AllowedSource).where(AllowedSource.path_prefix == normalized))
    if not existing and normalized:
        db.add(
            AllowedSource(
                path_prefix=normalized,
                description=description.strip() or None,
                enabled=True,
            )
        )
        db.commit()
    return RedirectResponse(url="/access-policy", status_code=303)


@router.post("/access-policy/toggle/{policy_id}")
def access_policy_toggle(policy_id: int, db: Session = Depends(get_db)):
    policy = db.get(AllowedSource, policy_id)
    if policy:
        policy.enabled = not policy.enabled
        db.commit()
    return RedirectResponse(url="/access-policy", status_code=303)


@router.get("/agent")
def agent_page(request: Request, db: Session = Depends(get_db)):
    policies = db.scalars(select(AllowedSource).order_by(AllowedSource.path_prefix.asc())).all()
    topics = db.scalars(select(Topic).order_by(Topic.name.asc())).all()
    last_run = db.scalar(select(AgentRun).order_by(AgentRun.started_at.desc()))
    review_queue = db.scalars(
        select(AgentDecision).where(AgentDecision.approved_by_user.is_(False)).order_by(AgentDecision.created_at.desc()).limit(50)
    ).all()
    recent_files = db.scalars(select(SourceFile).order_by(SourceFile.created_at.desc()).limit(50)).all()
    logs = db.scalars(select(ProcessingLog).order_by(ProcessingLog.created_at.desc()).limit(80)).all()
    return templates.TemplateResponse(
        "agent.html",
        {
            "request": request,
            "policies": policies,
            "topics": topics,
            "last_run": last_run,
            "review_queue": review_queue,
            "recent_files": recent_files,
            "logs": logs,
            "scan_message": None,
        },
    )


@router.post("/agent/scan")
def agent_scan(request: Request, db: Session = Depends(get_db)):
    summary = run_scan(db)
    policies = db.scalars(select(AllowedSource).order_by(AllowedSource.path_prefix.asc())).all()
    topics = db.scalars(select(Topic).order_by(Topic.name.asc())).all()
    last_run = db.scalar(select(AgentRun).where(AgentRun.id == summary.run_id))
    review_queue = db.scalars(
        select(AgentDecision).where(AgentDecision.approved_by_user.is_(False)).order_by(AgentDecision.created_at.desc()).limit(50)
    ).all()
    recent_files = db.scalars(select(SourceFile).order_by(SourceFile.created_at.desc()).limit(50)).all()
    logs = db.scalars(select(ProcessingLog).order_by(ProcessingLog.created_at.desc()).limit(80)).all()

    return templates.TemplateResponse(
        "agent.html",
        {
            "request": request,
            "policies": policies,
            "topics": topics,
            "last_run": last_run,
            "review_queue": review_queue,
            "recent_files": recent_files,
            "logs": logs,
            "scan_message": f"הסריקה הושלמה: נמצאו {summary.files_found}, עובדו {summary.files_processed}, נכשלו {summary.files_failed}.",
        },
    )


@router.post("/agent/decision/{decision_id}/approve")
def approve_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = db.get(AgentDecision, decision_id)
    if decision:
        decision.approved_by_user = True
        decision.suggested_status = "approved"
        if decision.capture_id:
            capture = db.get(Capture, decision.capture_id)
            if capture:
                capture.status = "approved"
        db.commit()
    return RedirectResponse(url="/agent", status_code=303)


@router.post("/agent/decision/{decision_id}/archive")
def archive_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = db.get(AgentDecision, decision_id)
    if decision:
        decision.suggested_status = "archived"
        if decision.capture_id:
            capture = db.get(Capture, decision.capture_id)
            if capture:
                capture.status = "archived"
        db.commit()
    return RedirectResponse(url="/agent", status_code=303)


@router.post("/agent/decision/{decision_id}/requires-check")
def requires_check_decision(decision_id: int, user_correction: str = Form(default=""), db: Session = Depends(get_db)):
    decision = db.get(AgentDecision, decision_id)
    if decision:
        decision.suggested_status = "requires_check"
        decision.user_correction = user_correction.strip() or "Marked for manual check by user"
        if decision.capture_id:
            capture = db.get(Capture, decision.capture_id)
            if capture:
                capture.status = "pending_review"
        db.commit()
    return RedirectResponse(url="/agent", status_code=303)


@router.post("/agent/decision/{decision_id}/change-topic")
def change_topic_decision(
    decision_id: int,
    topic_id: int = Form(...),
    user_correction: str = Form(default=""),
    db: Session = Depends(get_db),
):
    decision = db.get(AgentDecision, decision_id)
    topic = db.get(Topic, topic_id)
    if decision and topic:
        decision.suggested_topic = topic.name
        decision.suggested_status = "pending_review"
        decision.user_correction = user_correction.strip() or f"הנושא שונה ל-{topic.name}"
        if decision.capture_id:
            capture = db.get(Capture, decision.capture_id)
            if capture:
                capture.main_topic_id = topic.id
                capture.status = "pending_review"
        db.commit()
    return RedirectResponse(url="/agent", status_code=303)
