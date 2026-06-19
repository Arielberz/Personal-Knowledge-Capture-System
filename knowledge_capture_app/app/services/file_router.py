from pathlib import Path

SUPPORTED_TYPES: dict[str, str] = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".pdf": "pdf",
    ".md": "note",
    ".txt": "note",
    ".json": "chat_export",
    ".html": "chat_export",
    ".csv": "table",
}


def detect_file_type(file_path: Path) -> str | None:
    return SUPPORTED_TYPES.get(file_path.suffix.lower())
