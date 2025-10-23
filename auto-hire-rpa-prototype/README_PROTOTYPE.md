# Auto Hire RPA - Prototype

## Setup (local)
1. Copy `.env.example` to `.env` and fill SMTP/database values.
2. Create virtualenv & install:
   - python -m venv venv
   - source venv/bin/activate   # on Windows use `venv\Scripts\activate`
   - pip install -r requirements.txt
3. Initialize DB:
   - python -c "import sqlite3; conn=sqlite3.connect('auto_hire.db'); conn.executescript(open('db_schema.sql').read()); conn.commit(); conn.close()"
4. Run Flask:
   - python app.py
5. Open http://localhost:8000

## Quick flow
- `POST /jobs` with JSON `{ "title": "...", "description": "..." }`
- `POST /candidates` form-data: `resume_text` or `resume_file`, optionally `job_id` to auto-score
- `GET /jobs/<job_id>/shortlist?n=5` to get top candidates
- `POST /applications/<app_id>/invite` to send email invite (requires SMTP settings)

## Notes
- The scheduler is a stub. Integrate Google Calendar API for real scheduling.
- Replace TF-IDF ranking with ML model for better results.
- Use proper resume parsing libraries (e.g., `pyresparser`, `resume-parser`) for production.
