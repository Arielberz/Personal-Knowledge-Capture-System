from pathlib import Path

try:
    from app.services.ai_service import analyze_text_for_capture, analyze_with_mock
except ModuleNotFoundError:
    from services.ai_service import analyze_text_for_capture, analyze_with_mock


def process_chat(file_path: Path) -> dict[str, str | int]:
    try:
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        return analyze_text_for_capture(raw_text, file_path.name)
    except Exception:
        return analyze_with_mock(file_path, "chat_export")
