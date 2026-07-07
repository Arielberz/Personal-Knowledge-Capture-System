from pathlib import Path

try:
    from app.services.ai_service import analyze_image_for_capture, analyze_with_mock
except ModuleNotFoundError:
    from services.ai_service import analyze_image_for_capture, analyze_with_mock


def process_image(file_path: Path) -> dict[str, str | int]:
    try:
        return analyze_image_for_capture(file_path)
    except Exception:
        result = analyze_with_mock(file_path, "image")
        result["reason_for_score"] = (
            "Image vision analysis failed; used fallback analysis. "
            + str(result.get("reason_for_score", ""))
        )
        return result
