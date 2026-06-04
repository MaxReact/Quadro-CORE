import os
import uuid
from pathlib import Path

STORAGE_ROOT = Path(__file__).parent.parent / "storage"

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {"xlsx", "docx", "xmind", "txt", "md"}


def _project_dir(project_id: int) -> Path:
    d = STORAGE_ROOT / str(project_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_file(project_id: int, original_filename: str, data: bytes) -> str:
    ext = Path(original_filename).suffix.lstrip(".").lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = _project_dir(project_id) / filename
    path.write_bytes(data)
    return str(path.relative_to(STORAGE_ROOT.parent))  # relative to repo root


def delete_file(file_path: str) -> None:
    path = STORAGE_ROOT.parent / file_path
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
