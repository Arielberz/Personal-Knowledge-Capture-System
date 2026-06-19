from pathlib import Path

try:
    from app.models import AllowedSource
except ModuleNotFoundError:
    from models import AllowedSource


ALLOWED_MANUAL_PREFIX = "manual://"


def resolve_source_prefix(prefix: str, project_root: Path) -> Path | None:
    if prefix.startswith(ALLOWED_MANUAL_PREFIX):
        return None
    p = Path(prefix)
    if p.is_absolute():
        return p
    return (project_root / prefix).resolve()


def scan_allowed_sources(project_root: Path, allowed_sources: list[AllowedSource], detect_file_type) -> list[Path]:
    discovered: list[Path] = []
    for source in allowed_sources:
        folder = resolve_source_prefix(source.path_prefix, project_root)
        if folder is None or not folder.exists() or not folder.is_dir():
            continue
        for child in folder.rglob("*"):
            if child.is_file() and detect_file_type(child):
                discovered.append(child)
    return discovered
