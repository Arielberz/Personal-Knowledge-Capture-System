from __future__ import annotations

import json
import mimetypes
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ModuleNotFoundError:  # pragma: no cover - handled gracefully at runtime
    genai = None
    types = None

try:
    from app.config import settings
except ModuleNotFoundError:
    from config import settings


SYSTEM_INSTRUCTION = (
    "You are an expert knowledge management assistant. Analyze, organize, "
    "and structure incoming text into a clean JSON format."
)

KNOWLEDGE_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["title", "summary", "tags", "category"],
    "properties": {
        "title": {
            "type": "string",
            "description": "A concise, catchy title for the content.",
        },
        "summary": {
            "type": "string",
            "description": "A 2-3 sentence summary of the main points.",
        },
        "tags": {
            "type": "array",
            "maxItems": 5,
            "items": {"type": "string"},
            "description": "Up to 5 relevant tags for categorization.",
        },
        "category": {
            "type": "string",
            "description": "The primary category (e.g., Tech, Personal, Work, Ideas).",
        },
    },
}


def _normalize_structured_result(payload: dict[str, object]) -> dict[str, object]:
    tags_raw = payload.get("tags")
    tags = tags_raw if isinstance(tags_raw, list) else []
    clean_tags: list[str] = []
    for tag in tags:
        if isinstance(tag, str):
            normalized = tag.strip()
            if normalized:
                clean_tags.append(normalized)
    clean_tags = clean_tags[:5]

    return {
        "title": str(payload.get("title", "")).strip(),
        "summary": str(payload.get("summary", "")).strip(),
        "tags": clean_tags,
        "category": str(payload.get("category", "")).strip(),
    }


def processIncomingContent(rawText: str) -> dict[str, object]:
    if not isinstance(rawText, str) or not rawText.strip():
        raise ValueError("rawText is required and must be a non-empty string")

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    if genai is None or types is None:
        raise RuntimeError("google-genai package is not installed")

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=rawText.strip(),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=KNOWLEDGE_RESPONSE_SCHEMA,
        ),
    )

    parsed: dict[str, object] | None = None
    if isinstance(response.parsed, dict):
        parsed = response.parsed
    elif isinstance(response.text, str) and response.text.strip():
        parsed = json.loads(response.text)

    if not isinstance(parsed, dict):
        raise RuntimeError("AI response is empty or not a valid JSON object")

    return _normalize_structured_result(parsed)


def process_incoming_content(raw_text: str) -> dict[str, object]:
    return processIncomingContent(raw_text)


def _score_for_category(category: str) -> int:
    normalized = category.strip().lower()
    high_value = {"tech", "work", "research", "learning", "ideas"}
    if normalized in high_value:
        return 8
    if normalized in {"personal", "lifestyle"}:
        return 6
    return 7


def _confidence_for_tags(tags: list[str]) -> str:
    if len(tags) >= 4:
        return "high"
    if len(tags) >= 2:
        return "medium"
    return "low"


def analyze_text_for_capture(raw_text: str, file_label: str = "content") -> dict[str, str | int]:
    structured = processIncomingContent(raw_text)
    tags = structured.get("tags", [])
    tag_list = tags if isinstance(tags, list) else []
    clean_tags = [tag for tag in tag_list if isinstance(tag, str)]

    category = str(structured.get("category", "")).strip() or "General"
    score = _score_for_category(category)
    confidence = _confidence_for_tags(clean_tags)
    tags_text = ", ".join(clean_tags) if clean_tags else "none"

    return {
        "title": str(structured.get("title", "")).strip() or Path(file_label).stem.replace("_", " ").title(),
        "summary": str(structured.get("summary", "")).strip(),
        "knowledge_score": score,
        "confidence": confidence,
        "reason_for_score": f"Category='{category}', tags={tags_text}.",
        "open_questions": f"Which action should be taken next for category '{category}'?",
        "what_to_learn": f"Deepen understanding in {category} using tags: {tags_text}.",
    }


IMAGE_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["title", "summary", "tags", "category", "confidence"],
    "properties": {
        "title": {
            "type": "string",
            "description": "A concise title for the image content.",
        },
        "summary": {
            "type": "string",
            "description": "A short factual summary of what is visible.",
        },
        "tags": {
            "type": "array",
            "maxItems": 6,
            "items": {"type": "string"},
            "description": "Up to 6 concise topical tags derived from visual evidence.",
        },
        "category": {
            "type": "string",
            "description": "Primary category such as Finance, Technology, Personal, Work.",
        },
        "confidence": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "How confident you are in the classification.",
        },
    },
}


def _normalize_image_result(payload: dict[str, object], file_path: Path) -> dict[str, str | int]:
    raw_tags = payload.get("tags")
    tags = raw_tags if isinstance(raw_tags, list) else []
    clean_tags = [str(tag).strip() for tag in tags if isinstance(tag, str) and str(tag).strip()][:6]

    category = str(payload.get("category", "")).strip() or "General"
    confidence = str(payload.get("confidence", "")).strip().lower()
    if confidence not in {"low", "medium", "high"}:
        confidence = "medium"

    score_by_confidence = {"low": 5, "medium": 7, "high": 8}
    score = score_by_confidence[confidence]

    tags_text = ", ".join(clean_tags) if clean_tags else "none"
    title = str(payload.get("title", "")).strip() or file_path.stem.replace("_", " ").title()
    summary = str(payload.get("summary", "")).strip() or f"Image analysis for {file_path.name}."

    return {
        "title": title,
        "summary": summary,
        "knowledge_score": score,
        "confidence": confidence,
        "category": category,
        "tags": clean_tags,
        "reason_for_score": f"Visual analysis category='{category}', confidence='{confidence}', tags={tags_text}.",
        "open_questions": f"What follow-up action should be taken for this {category} image?",
        "what_to_learn": f"Review the visual signals in {category} context and validate with source data.",
    }


def analyze_image_for_capture(file_path: Path) -> dict[str, str | int]:
    if not settings.gemini_api_key:
        return analyze_with_mock(file_path, "image")

    if genai is None or types is None:
        return analyze_with_mock(file_path, "image")

    try:
        image_bytes = file_path.read_bytes()
        mime_type = mimetypes.guess_type(file_path.name)[0] or "image/png"

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                "Analyze this image and classify it for knowledge management. If it appears to be a stock/ETF/market chart or financial dashboard, set category to Finance and include finance tags.",
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an expert knowledge management assistant. Use only visible evidence from the image. "
                    "Return structured JSON and avoid hallucinations."
                ),
                response_mime_type="application/json",
                response_schema=IMAGE_RESPONSE_SCHEMA,
            ),
        )

        parsed: dict[str, object] | None = None
        if isinstance(response.parsed, dict):
            parsed = response.parsed
        elif isinstance(response.text, str) and response.text.strip():
            parsed = json.loads(response.text)

        if not isinstance(parsed, dict):
            return analyze_with_mock(file_path, "image")

        return _normalize_image_result(parsed, file_path)
    except Exception as exc:
        fallback = analyze_with_mock(file_path, "image")
        fallback["reason_for_score"] = (
            "Gemini vision analysis failed and fallback was used. "
            + f"Error: {type(exc).__name__}. "
            + str(fallback.get("reason_for_score", ""))
        )
        return fallback


def analyze_with_mock(file_path: Path, file_type: str) -> dict[str, str | int]:
    name = file_path.stem.replace("_", " ")
    summary = f"Auto-analyzed {file_type} file '{file_path.name}' from configured inbox source."

    score = 6
    confidence = "medium"
    if file_type in {"image", "pdf"}:
        score = 8
    elif file_type == "chat_export":
        score = 7

    category = "General"
    tags: list[str] = [file_type]
    if file_type == "image":
        category = "Visual"
        tags = ["image", "requires_check"]

    return {
        "title": name.title(),
        "summary": summary,
        "knowledge_score": score,
        "confidence": confidence,
        "category": category,
        "tags": tags,
        "reason_for_score": "Derived from file type and likely reuse value in your knowledge workflow.",
        "open_questions": "What should be verified manually before approval?",
        "what_to_learn": "Review the core claim and map it to existing topic notes.",
    }
