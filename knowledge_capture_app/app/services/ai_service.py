from pathlib import Path


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
