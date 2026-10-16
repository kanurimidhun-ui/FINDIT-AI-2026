import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from model import ItemReport, MatchResult, MatchingEngine
from tools import load_reports, save_reports, validate_image


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_REPORTS_PATH = (
    Path("/tmp/findit-reports.json")
    if os.environ.get("VERCEL") == "1"
    else BASE_DIR / "data" / "reports.json"
)
REPORTS_PATH = Path(os.environ.get("FINDIT_DATA_FILE", DEFAULT_REPORTS_PATH))

app = FastAPI(title="FindIt AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

engine = MatchingEngine()
for saved_report in load_reports(REPORTS_PATH):
    engine.add_report(ItemReport.model_validate(saved_report))


@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/reports", response_model=List[ItemReport])
def list_reports(report_type: Optional[str] = Query(default=None)):
    if report_type is not None and report_type not in {"lost", "found"}:
        raise HTTPException(status_code=400, detail="report_type must be 'lost' or 'found'")

    reports = engine.reports
    if report_type:
        reports = [report for report in reports if report.report_type == report_type]
    return list(reversed(reports))


@app.post("/api/reports", response_model=dict, status_code=201)
@app.post("/reports/", response_model=dict, status_code=201, include_in_schema=False)
def create_report(report: ItemReport):
    if report.image_path:
        validate_image(report.image_path)

    report.item_id = report.item_id or uuid.uuid4().hex[:8]
    potential_matches = engine.find_matches(report)
    updated_reports = [*engine.reports, report]
    save_reports(REPORTS_PATH, [item.model_dump(mode="json") for item in updated_reports])
    engine.add_report(report)

    return {
        "status": "success",
        "item_id": report.item_id,
        "message": f"Report registered successfully as '{report.report_type}'.",
        "matches_found": len(potential_matches),
        "matches": potential_matches,
    }


@app.get("/api/reports/{item_id}/matches", response_model=List[MatchResult])
@app.get("/reports/matches/{item_id}", response_model=List[MatchResult], include_in_schema=False)
def get_matches_for_item(item_id: str):
    target_report = next((report for report in engine.reports if report.item_id == item_id), None)
    if not target_report:
        raise HTTPException(status_code=404, detail="Item report not found.")

    return engine.find_matches(target_report)
