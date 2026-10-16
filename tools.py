
import json
from pathlib import Path

from fastapi import HTTPException


def load_reports(path="data/reports.json"):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Report data in {file_path} is not valid JSON") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not read report data from {file_path}") from exc

    if not isinstance(data, list):
        raise RuntimeError(f"Report data in {file_path} must be a JSON array")
    return data


def save_reports(path, reports):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        temp_path.write_text(
            json.dumps(reports, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp_path.replace(file_path)
    except OSError as exc:
        raise RuntimeError(f"Could not save report data to {file_path}") from exc


def validate_image(image_path):
    # This validates a reference only; it does not upload an image.
    if not isinstance(image_path, str) or len(image_path) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Invalid image reference",
        )

    if not image_path.startswith(("https://", "http://", "/")):
        raise HTTPException(
            status_code=400,
            detail="Image must be a URL or local path reference",
        )
