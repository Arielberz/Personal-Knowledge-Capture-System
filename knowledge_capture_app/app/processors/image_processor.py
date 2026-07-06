from pathlib import Path

try:
    from app.services.ai_service import analyze_with_mock
except ModuleNotFoundError:
    from services.ai_service import analyze_with_mock


def process_image(file_path: Path) -> dict[str, str | int]:
    result = analyze_with_mock(file_path, "image")
    result["reason_for_score"] = (
        "Image OCR is not configured yet; used fallback analysis. "
        + str(result.get("reason_for_score", ""))
    )
    return result
