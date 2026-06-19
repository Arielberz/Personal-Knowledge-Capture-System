from pathlib import Path

try:
    from app.services.ai_service import analyze_with_mock
except ModuleNotFoundError:
    from services.ai_service import analyze_with_mock


def process_chat(file_path: Path) -> dict[str, str | int]:
    return analyze_with_mock(file_path, "chat_export")
