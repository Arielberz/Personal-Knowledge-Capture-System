from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from app.processors.chat_processor import process_chat
    from app.processors.image_processor import process_image
    from app.processors.note_processor import process_note
    from app.processors.pdf_processor import process_pdf
    from app.services.file_router import detect_file_type
    from app.services.file_scanner import resolve_source_prefix, scan_allowed_sources
    from app.services.topic_router import route_topic
    from app.models import (
        AgentDecision,
        AgentRun,
        AllowedSource,
        Capture,
        ProcessingLog,
        SourceFile,
        Topic,
    )
except ModuleNotFoundError:
    from processors.chat_processor import process_chat
    from processors.image_processor import process_image
    from processors.note_processor import process_note
    from processors.pdf_processor import process_pdf
    from services.file_router import detect_file_type
    from services.file_scanner import resolve_source_prefix, scan_allowed_sources
    from services.topic_router import route_topic
    from models import AgentDecision, AgentRun, AllowedSource, Capture, ProcessingLog, SourceFile, Topic


@dataclass
class ScanSummary:
    run_id: int
    files_found: int
    files_processed: int
    files_failed: int


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _file_hash(file_path: Path) -> str:
    digest = sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _process_by_type(file_path: Path, file_type: str) -> dict[str, str | int]:
    if file_type == "image":
        return process_image(file_path)
    if file_type == "pdf":
        return process_pdf(file_path)
    if file_type == "chat_export":
        return process_chat(file_path)
    if file_type == "note":
        return process_note(file_path)
    return {
        "title": file_path.stem.replace("_", " ").title(),
        "summary": f"Unsupported processor for type {file_type}; stored for manual review.",
        "knowledge_score": 5,
        "confidence": "low",
        "reason_for_score": "No dedicated processor available yet.",
        "open_questions": "Should this file type get a dedicated processor?",
        "what_to_learn": "Define extraction rules for this format.",
    }


def _log(db: Session, run_id: int, file_path: str | None, step: str, status: str, message: str) -> None:
    db.add(
        ProcessingLog(
            run_id=run_id,
            file_path=file_path,
            step=step,
            status=status,
            message=message,
        )
    )


def run_scan(db: Session) -> ScanSummary:
    allowed = db.scalars(select(AllowedSource).where(AllowedSource.enabled.is_(True))).all()

    run = AgentRun(status="running")
    db.add(run)
    db.flush()

    discovered: list[Path] = []
    for source in allowed:
        folder = resolve_source_prefix(source.path_prefix, _project_root())
        if folder is None:
            continue
        if not folder.exists() or not folder.is_dir():
            _log(db, run.id, str(folder), "scan_source", "warning", "Allowed source folder not found")
            continue
    discovered = scan_allowed_sources(_project_root(), allowed, detect_file_type)

    run.files_found = len(discovered)

    processed = 0
    failed = 0

    for file_path in discovered:
        try:
            f_type = detect_file_type(file_path)
            if not f_type:
                continue

            hash_value = _file_hash(file_path)
            existing = db.scalar(select(SourceFile).where(SourceFile.file_hash == hash_value))
            if existing:
                existing.last_seen_at = datetime.utcnow()
                _log(db, run.id, str(file_path), "dedupe", "skipped", "File hash already processed")
                continue

            rel_path = file_path.resolve().as_posix()
            src = SourceFile(
                file_path=rel_path,
                original_filename=file_path.name,
                file_type=f_type,
                file_hash=hash_value,
                file_size=file_path.stat().st_size,
                status="processed",
            )
            db.add(src)
            db.flush()

            analysis = _process_by_type(file_path, f_type)
            topic = route_topic(db, f_type, f"{file_path.name} {analysis['summary']}")

            capture = Capture(
                source_type=f_type,
                file_path=rel_path,
                original_filename=file_path.name,
                title=str(analysis["title"]),
                summary=str(analysis["summary"]),
                main_topic_id=topic.id if topic else None,
                knowledge_score=int(analysis["knowledge_score"]),
                confidence=str(analysis["confidence"]),
                status="pending_review",
            )
            db.add(capture)
            db.flush()

            decision = AgentDecision(
                source_file_id=src.id,
                capture_id=capture.id,
                suggested_topic=topic.name if topic else "Unassigned",
                suggested_status="pending_review",
                knowledge_score=int(analysis["knowledge_score"]),
                confidence=str(analysis["confidence"]),
                reason_for_topic=f"Matched to topic using file name/type routing for {f_type}.",
                reason_for_score=str(analysis["reason_for_score"]),
                what_to_learn_from_this=str(analysis["what_to_learn"]),
                open_questions=str(analysis["open_questions"]),
            )
            db.add(decision)

            _log(db, run.id, rel_path, "process_file", "ok", "File analyzed and queued for review")
            processed += 1
        except Exception as exc:
            failed += 1
            _log(db, run.id, str(file_path), "process_file", "error", f"{type(exc).__name__}: {exc}")

    run.files_processed = processed
    run.files_failed = failed
    run.status = "completed" if failed == 0 else "completed_with_errors"
    run.finished_at = datetime.utcnow()

    db.commit()

    return ScanSummary(
        run_id=run.id,
        files_found=run.files_found,
        files_processed=run.files_processed,
        files_failed=run.files_failed,
    )
