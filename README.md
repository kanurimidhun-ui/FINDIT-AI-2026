# FindIt AI

A text-first lost-and-found app. Post a lost or found item with its category,
location, description, and optional date or image URL. Potential matches compare
description (60%), category (20%), location (12%), and date (8%). This version
uses text-overlap heuristics, not a trained AI model or image-recognition system;
match scores are suggestions, not validated accuracy measurements.

Live demo: <https://findit-ai-2026.onrender.com>

## Run locally

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the application or
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the API.
Reports are stored in `data/reports.json`. Set `FINDIT_DATA_FILE` to use another
JSON file.

## API

- `GET /api/health` — service health
- `GET /api/reports` — list reports
- `GET /api/reports?report_type=lost` — filter by lost or found
- `POST /api/reports` — create a report and return current potential matches
- `GET /api/reports/{item_id}/matches` — find opposite-type reports

## Deploy

The repository includes `render.yaml` for Render. Import the GitHub repository
in each hosting provider. Render can deploy the blueprint or use
`pip install -r requirements.txt` and
`uvicorn main:app --host 0.0.0.0 --port $PORT`. Vercel detects the FastAPI
application in `main.py` from `requirements.txt` and routes requests to it.

The JSON file is suitable for local demos only. Serverless instances and
ephemeral hosting filesystems do not provide durable shared storage. Before
using this publicly, configure a persistent database, authentication, privacy
controls, rate limiting, safe contact methods, and secure image storage.
