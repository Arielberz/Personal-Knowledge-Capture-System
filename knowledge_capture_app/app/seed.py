from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from app.models import AllowedSource, Capture, OpenQuestion, Reminder, Topic
except ModuleNotFoundError:
    from models import AllowedSource, Capture, OpenQuestion, Reminder, Topic


def seed_if_empty(db: Session) -> None:
    existing_topic = db.scalar(select(Topic).limit(1))
    if not existing_topic:
        topics = [
            Topic(name="AI Infrastructure", description="Cloud, data centers, GPUs, capex"),
            Topic(name="Market Valuation", description="Forward P/E, earnings revisions, multiples"),
            Topic(name="ETF and Market Structure", description="Indexing, tracking, rebalancing"),
        ]
        db.add_all(topics)
        db.flush()

        captures = [
            Capture(
                source_type="image",
                file_path="data/inbox/images/image_001.png",
                original_filename="image_001.png",
                title="Cloud AI backlog concentration",
                summary="Backlog concentration in major cloud vendors linked to AI clients.",
                main_topic_id=topics[0].id,
                knowledge_score=9,
                confidence="medium",
                status="approved",
            ),
            Capture(
                source_type="image",
                file_path="data/inbox/images/image_002.png",
                original_filename="image_002.png",
                title="Forward P/E compression",
                summary="Multiples decline despite strong price levels due to rising earnings estimates.",
                main_topic_id=topics[1].id,
                knowledge_score=8,
                confidence="high",
                status="pending_review",
            ),
            Capture(
                source_type="chat_export",
                file_path="data/inbox/images/conversation_001.md",
                original_filename="conversation_001.md",
                title="ETF tracking mechanics",
                summary="Explains drift, rebalancing windows, and creation-redemption arbitrage.",
                main_topic_id=topics[2].id,
                knowledge_score=8,
                confidence="high",
                status="approved",
            ),
        ]
        db.add_all(captures)
        db.flush()

        questions = [
            OpenQuestion(
                capture_id=captures[0].id,
                topic_id=topics[0].id,
                question="How binding are cloud commitments of major AI customers?",
                importance_score=8,
                status="open",
            ),
            OpenQuestion(
                capture_id=captures[1].id,
                topic_id=topics[1].id,
                question="Is forward P/E drop driven more by earnings revisions or multiple compression?",
                importance_score=9,
                status="open",
            ),
        ]

        reminders = [
            Reminder(
                topic_id=topics[0].id,
                capture_id=captures[0].id,
                question="Review AI capex vs electricity demand bottlenecks.",
                due_date=(datetime.utcnow() + timedelta(days=3)).date().isoformat(),
                status="pending",
                reminder_type="follow_up_research",
            ),
            Reminder(
                topic_id=topics[1].id,
                capture_id=captures[1].id,
                question="Re-check forward vs trailing P/E explanation this week.",
                due_date=(datetime.utcnow() + timedelta(days=7)).date().isoformat(),
                status="pending",
                reminder_type="review_question",
            ),
        ]

        db.add_all(questions)
        db.add_all(reminders)

    default_sources = [
        (
            "data/inbox/images",
            "Image inbox for charts and screenshots.",
        ),
        (
            "data/inbox/pdfs",
            "PDF inbox for reports and documents.",
        ),
        (
            "data/inbox/chat_exports",
            "Chat export files and selected conversations.",
        ),
        (
            "data/inbox/notes",
            "Notes inbox for markdown and text notes.",
        ),
        (
            "manual://",
            "Manual notes entered from the dashboard.",
        ),
    ]
    for path_prefix, description in default_sources:
        existing_source = db.scalar(select(AllowedSource).where(AllowedSource.path_prefix == path_prefix))
        if not existing_source:
            db.add(AllowedSource(path_prefix=path_prefix, description=description, enabled=True))

    db.commit()
