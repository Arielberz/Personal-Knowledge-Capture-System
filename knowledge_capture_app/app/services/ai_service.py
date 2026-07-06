from __future__ import annotations

import json
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
    "additionalProperties": False,
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


def analyze_with_mock(file_path: Path, file_type: str) -> dict[str, str | int]:
    name = file_path.stem.replace("_", " ")
    summary = f"Auto-analyzed {file_type} file '{file_path.name}' from configured inbox source."

    score = 6
    confidence = "medium"
    if file_type in {"image", "pdf"}:
        score = 8
    elif file_type == "chat_export":
        score = 7

    return {
        "title": name.title(),
        "summary": summary,
        "knowledge_score": score,
        "confidence": confidence,
        "reason_for_score": "Derived from file type and likely reuse value in your knowledge workflow.",
        "open_questions": "What should be verified manually before approval?",
        "what_to_learn": "Review the core claim and map it to existing topic notes.",
    }
