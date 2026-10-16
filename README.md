# FindIt

A text-first lost-and-found board. Post a lost or found item with its category,
location, description, and optional date and image URL. Potential matches are
ranked using description (60%), category (20%), location (12%), and date (8%).
The match score is a demo heuristic, not a validated measure of accuracy.

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

The repository includes `render.yaml` for Render and `vercel.json` for Vercel.
Push this project to a GitHub repository, then import that same repository in
each hosting provider. Render uses the web service blueprint; Vercel uses the
Python function in `api/index.py`.

The JSON file is suitable for local demos only. Serverless instances and
ephemeral hosting filesystems do not provide durable shared storage. Before
using this publicly, configure a persistent database, authentication, privacy
controls, rate limiting, safe contact methods, and secure image storage.
