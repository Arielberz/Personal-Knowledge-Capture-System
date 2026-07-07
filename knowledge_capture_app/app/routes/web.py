from datetime import datetime
from pathlib import Path
import random
from shutil import copyfileobj

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import JSONResponse
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


def _shuffle_quiz_answers(payload: dict) -> dict:
    questions = payload.get("questions", [])
    for question in questions:
        options = question.get("answerOptions", [])
        random.shuffle(options)
    return payload


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
def questions(request: Request, topic_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    questions_query = select(OpenQuestion).order_by(OpenQuestion.importance_score.desc())
    if topic_id is not None:
        questions_query = questions_query.where(OpenQuestion.topic_id == topic_id)

    questions_data = db.scalars(questions_query).all()
    topics = db.scalars(select(Topic).order_by(Topic.name.asc())).all()
    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "questions": questions_data,
            "topics": topics,
            "selected_topic": topic_id,
        },
    )


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


@router.get("/quiz")
def quiz_page(request: Request):
    return RedirectResponse(url="/questions", status_code=307)


@router.get("/api/quiz/sample")
def quiz_sample_data(topic_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    selected_topic_name = None
    if topic_id is not None:
        topic = db.get(Topic, topic_id)
        selected_topic_name = topic.name if topic else None

    if selected_topic_name and any(
        key in selected_topic_name.lower() for key in ["etf", "market", "finance", "פיננס", "השק", "שוק"]
    ):
        payload = {
            "questions": [
                {
                    "questionNumber": 1,
                    "question": "איזה משפט מתאר נכון ETF?",
                    "answerOptions": [
                        {
                            "text": "ETF הוא קרן סל הנסחרת כמו מניה",
                            "rationale": "נכון. ETF נסחר בזמן אמת לאורך יום המסחר.",
                            "isCorrect": True,
                        },
                        {
                            "text": "ETF ניתן לקנות רק פעם ביום בסגירה",
                            "rationale": "לא נכון. זה נכון יותר לקרנות נאמנות מסורתיות.",
                            "isCorrect": False,
                        },
                        {
                            "text": "ETF לא מאפשר פיזור כלל",
                            "rationale": "לא נכון. רבים מה-ETF-ים בנויים בדיוק לפיזור רחב.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "חשוב על אופן המסחר של ETF בבורסה.",
                },
                {
                    "questionNumber": 2,
                    "question": "מה יתרון מרכזי בפיזור השקעות?",
                    "answerOptions": [
                        {
                            "text": "מקטין תלות בנכס אחד",
                            "rationale": "נכון. פיזור מוריד סיכון ספציפי לנכס יחיד.",
                            "isCorrect": True,
                        },
                        {
                            "text": "מבטיח רווח בכל מצב",
                            "rationale": "לא נכון. פיזור מפחית סיכון אך לא מבטיח תשואה.",
                            "isCorrect": False,
                        },
                        {
                            "text": "מונע תנודתיות לחלוטין",
                            "rationale": "לא נכון. תנודתיות יכולה להישאר גם בתיק מגוון.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "המפתח הוא ניהול סיכון, לא ביטול סיכון.",
                },
                {
                    "questionNumber": 3,
                    "question": "מה ההבדל המרכזי בין מניה לאג\"ח?",
                    "answerOptions": [
                        {
                            "text": "מניה משקפת בעלות, אג\"ח משקפת חוב",
                            "rationale": "נכון. מניה היא חלק בבעלות החברה, אג\"ח היא התחייבות להחזר חוב.",
                            "isCorrect": True,
                        },
                        {
                            "text": "אין הבדל מהותי ביניהן",
                            "rationale": "לא נכון. מדובר בשני סוגי נכסים שונים מהיסוד.",
                            "isCorrect": False,
                        },
                        {
                            "text": "אג\"ח תמיד מסוכנת יותר ממניה",
                            "rationale": "לא נכון. רמת הסיכון תלויה בסוג הנכס ובמנפיק.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "שאל את עצמך: בעלות או הלוואה?",
                },
                {
                    "questionNumber": 4,
                    "question": "מה המשמעות של יחס הוצאות (Expense Ratio) בקרן סל?",
                    "answerOptions": [
                        {
                            "text": "עמלה שנתית הנגבית מנכסי הקרן",
                            "rationale": "נכון. זהו שיעור העלות השנתית לניהול הקרן.",
                            "isCorrect": True,
                        },
                        {
                            "text": "מס שהמדינה גובה על כל פעולה",
                            "rationale": "לא נכון. זהו לא מס ממשלתי אלא עלות ניהול הקרן.",
                            "isCorrect": False,
                        },
                        {
                            "text": "ריבית שהמשקיע מקבל בסוף שנה",
                            "rationale": "לא נכון. מדובר בעלות, לא ברווח.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "זה קשור לעלות ניהול, לא לתשואה מובטחת.",
                },
                {
                    "questionNumber": 5,
                    "question": "למה איזון תיק תקופתי (Rebalancing) יכול להיות חשוב?",
                    "answerOptions": [
                        {
                            "text": "כדי להחזיר את התיק להקצאת הסיכון המתוכננת",
                            "rationale": "נכון. האיזון שומר על פרופיל הסיכון המקורי.",
                            "isCorrect": True,
                        },
                        {
                            "text": "כדי להבטיח תשואה חיובית בכל רבעון",
                            "rationale": "לא נכון. איזון לא מבטיח תשואה.",
                            "isCorrect": False,
                        },
                        {
                            "text": "כדי לבטל לחלוטין עמלות מסחר",
                            "rationale": "לא נכון. איזון עצמו עשוי אף ליצור פעולות מסחר.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "תחשוב על שמירה על רמת סיכון קבועה.",
                },
                {
                    "questionNumber": 6,
                    "question": "מה בדרך כלל קורה לקשר בין סיכון לתשואה צפויה?",
                    "answerOptions": [
                        {
                            "text": "סיכון גבוה יותר עשוי לאפשר תשואה צפויה גבוהה יותר",
                            "rationale": "נכון. זו הנחת יסוד מרכזית בשוק ההון.",
                            "isCorrect": True,
                        },
                        {
                            "text": "אין שום קשר בין סיכון לתשואה",
                            "rationale": "לא נכון. לרוב קיים קשר בין השניים.",
                            "isCorrect": False,
                        },
                        {
                            "text": "סיכון גבוה תמיד מבטיח תשואה גבוהה",
                            "rationale": "לא נכון. פוטנציאל גבוה לא מבטיח תוצאה בפועל.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "המילה החשובה: 'צפויה', לא 'מובטחת'.",
                },
                {
                    "questionNumber": 7,
                    "question": "מה היתרון של השקעה עקבית לאורך זמן (DCA)?",
                    "answerOptions": [
                        {
                            "text": "מפחיתה תלות בתזמון כניסה חד-פעמי",
                            "rationale": "נכון. פריסה בזמן יכולה להפחית סיכון תזמון.",
                            "isCorrect": True,
                        },
                        {
                            "text": "מבטיחה תשואה גבוהה מכל אסטרטגיה אחרת",
                            "rationale": "לא נכון. אין הבטחת תשואה.",
                            "isCorrect": False,
                        },
                        {
                            "text": "מבטלת תנודתיות בשוק",
                            "rationale": "לא נכון. התנודתיות בשוק עדיין קיימת.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "הדגש הוא הפחתת תלות ברגע אחד בשוק.",
                },
                {
                    "questionNumber": 8,
                    "question": "מה נחשב לרוב לסיכון ספציפי לחברה?",
                    "answerOptions": [
                        {
                            "text": "כשל ניהולי בחברה מסוימת",
                            "rationale": "נכון. זהו סיכון נקודתי שניתן לרוב להפחית בפיזור.",
                            "isCorrect": True,
                        },
                        {
                            "text": "שינוי ריבית במשק כולו",
                            "rationale": "לא נכון. זה יותר סיכון מערכתי/שוקי.",
                            "isCorrect": False,
                        },
                        {
                            "text": "אינפלציה כללית במשק",
                            "rationale": "לא נכון. זהו סיכון מאקרו רחב, לא ספציפי לחברה אחת.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "שאל מה קשור לחברה אחת מול כל השוק.",
                },
            ]
        }
        return JSONResponse(content=_shuffle_quiz_answers(payload))

    payload = {
        "questions": [
            {
                "questionNumber": 1,
                "question": "איזה יחס בין סיכון לתשואה נחשב לרוב כאיזון סביר למשקיע מתחיל?",
                "answerOptions": [
                    {
                        "text": "100% מניות צמיחה",
                        "rationale": "חשיפה מלאה למניות מגדילה תנודתיות ועלולה להיות אגרסיבית מדי להתחלה.",
                        "isCorrect": False,
                    },
                    {
                        "text": "שילוב מניות ואג\"ח לפי רמת סיכון אישית",
                        "rationale": "פיזור בין אפיקים נוטה לייצב את התיק ולשפר ניהול סיכון.",
                        "isCorrect": True,
                    },
                    {
                        "text": "להחזיק הכול במזומן לאורך שנים",
                        "rationale": "מזומן שומר על יציבות, אך בדרך כלל נשחק מול אינפלציה בטווח ארוך.",
                        "isCorrect": False,
                    },
                ],
                "hint": "חפש תשובה שמדגישה פיזור וניהול סיכון.",
            },
            {
                "questionNumber": 2,
                "question": "מה המשמעות של 'פיזור' בתיק השקעות?",
                "answerOptions": [
                    {
                        "text": "לקנות רק את המניה המובילה במדד",
                        "rationale": "התמקדות בנכס יחיד מגדילה סיכון ספציפי.",
                        "isCorrect": False,
                    },
                    {
                        "text": "להשקיע בכמה סוגי נכסים וסקטורים",
                        "rationale": "פיזור מפחית תלות בנכס יחיד ומשפר עמידות לשינויים.",
                        "isCorrect": True,
                    },
                    {
                        "text": "להחליף נכסים כל יום",
                        "rationale": "תדירות גבוהה לא מחליפה אסטרטגיית פיזור אמיתית.",
                        "isCorrect": False,
                    },
                ],
                "hint": "חשוב על חלוקת סיכון בין מקורות שונים.",
            },
                {
                    "questionNumber": 3,
                    "question": "מהי דרך טובה לבדוק אם הבנת נושא לעומק?",
                    "answerOptions": [
                        {
                            "text": "להסביר את הנושא במילים פשוטות",
                            "rationale": "נכון. הסבר פשוט חושף פערי הבנה במהירות.",
                            "isCorrect": True,
                        },
                        {
                            "text": "לשנן משפט אחד בלי הקשר",
                            "rationale": "לא נכון. שינון בלי הבנה לא בודק עומק אמיתי.",
                            "isCorrect": False,
                        },
                        {
                            "text": "לדלג על דוגמאות",
                            "rationale": "לא נכון. דוגמאות מחזקות הבנה יישומית.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "יכולת להסביר לאחרים היא מבחן טוב להבנה.",
                },
                {
                    "questionNumber": 4,
                    "question": "מה כדאי לעשות כשנשארת שאלה פתוחה אחרי למידה?",
                    "answerOptions": [
                        {
                            "text": "לתעד אותה ולעקוב עד לקבלת תשובה",
                            "rationale": "נכון. מעקב שיטתי הופך פער ידע למשימת למידה.",
                            "isCorrect": True,
                        },
                        {
                            "text": "להתעלם ממנה",
                            "rationale": "לא נכון. התעלמות משאירה חור בהבנה.",
                            "isCorrect": False,
                        },
                        {
                            "text": "לנחש תשובה סופית ולסגור",
                            "rationale": "לא נכון. ניחוש לא מחליף בדיקה אמינה.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "שאלה פתוחה טובה היא משימה, לא רעש.",
                },
                {
                    "questionNumber": 5,
                    "question": "מה המטרה המרכזית של רמז בשאלה?",
                    "answerOptions": [
                        {
                            "text": "לכוון לחשיבה הנכונה בלי לתת את התשובה",
                            "rationale": "נכון. רמז טוב מכוון מסלול חשיבה.",
                            "isCorrect": True,
                        },
                        {
                            "text": "להחליף את כל תהליך הפתרון",
                            "rationale": "לא נכון. הרמז עוזר, לא פותר במקומך.",
                            "isCorrect": False,
                        },
                        {
                            "text": "לבלבל בין האפשרויות",
                            "rationale": "לא נכון. מטרת רמז היא בהירות, לא בלבול.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "רמז טוב מרמז על כיוון, לא על נוסח סופי.",
                },
                {
                    "questionNumber": 6,
                    "question": "מה התועלת בהסברים קצרים לכל תשובה אחרי Submit?",
                    "answerOptions": [
                        {
                            "text": "למידה מהירה גם מטעויות וגם מתשובות נכונות",
                            "rationale": "נכון. כך מתקבלת למידה ממוקדת בכל שאלה.",
                            "isCorrect": True,
                        },
                        {
                            "text": "רק הארכת זמן המבחן",
                            "rationale": "לא נכון. הסברים טובים משפרים הבנה איכותית.",
                            "isCorrect": False,
                        },
                        {
                            "text": "ביטול הצורך בחזרה על חומר",
                            "rationale": "לא נכון. הסברים עוזרים, אך לא מחליפים תרגול חוזר.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "תחשוב על פידבק מיידי כתהליך למידה.",
                },
                {
                    "questionNumber": 7,
                    "question": "איזה שימוש בציון מבחן הוא הכי נכון?",
                    "answerOptions": [
                        {
                            "text": "לזהות נושאים לחיזוק ולבנות תכנית שיפור",
                            "rationale": "נכון. ציון הוא אינדיקציה לשיפור, לא תווית קבועה.",
                            "isCorrect": True,
                        },
                        {
                            "text": "להחליט שאין צורך ללמוד יותר",
                            "rationale": "לא נכון. גם ציון גבוה לא מבטל תחזוקה של ידע.",
                            "isCorrect": False,
                        },
                        {
                            "text": "להשוות רק לאחרים בלי ניתוח אישי",
                            "rationale": "לא נכון. הערך הגדול הוא שיפור עצמי ממוקד.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "מדד טוב מוביל לפעולה הבאה.",
                },
                {
                    "questionNumber": 8,
                    "question": "מה סימן לכך שהבנת טעות שעשית בשאלה?",
                    "answerOptions": [
                        {
                            "text": "אתה יודע להסביר למה התשובה שלך הייתה שגויה",
                            "rationale": "נכון. הבנת הטעות עצמה היא לב השיפור.",
                            "isCorrect": True,
                        },
                        {
                            "text": "אתה רק זוכר את האות הנכונה",
                            "rationale": "לא נכון. זכירת אות בלי היגיון לא מבטיחה למידה.",
                            "isCorrect": False,
                        },
                        {
                            "text": "אתה מדלג לשאלה הבאה בלי לקרוא הסבר",
                            "rationale": "לא נכון. דילוג על הסבר מפספס את הערך הלימודי.",
                            "isCorrect": False,
                        },
                    ],
                    "hint": "האם אתה מבין את הסיבה, לא רק את התוצאה?",
                },
        ]
    }
    return JSONResponse(content=_shuffle_quiz_answers(payload))


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
