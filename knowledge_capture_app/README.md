# Knowledge Capture Dashboard

Local web app for personal knowledge capture with FastAPI, SQLite, and a browser dashboard.

## Features

- Backend API with FastAPI.
- SQLite database with SQLAlchemy.
- Frontend dashboard with Jinja2 templates.
- Views for captures, topics, open questions, and reminders.
- Filtering captures by topic and knowledge score.
- Safe-by-default: original files are never modified by the app.

## Project Structure

- `app/` - backend code, routes, templates, static files
- `database/` - SQLite database file location
- `data/inbox/images/` - place source images here

## Quick Start (macOS / Linux / Windows PowerShell)

1. Create and activate virtual environment.

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy env file.

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

4. Run the app.

```bash
uvicorn app.main:app --reload
```

5. Open browser:

- `http://127.0.0.1:8000`

## Notes

- The app seeds initial demo data if the database is empty.
- Add your own image files under `data/inbox/images/` and then create capture entries from backend scripts or API extensions.
