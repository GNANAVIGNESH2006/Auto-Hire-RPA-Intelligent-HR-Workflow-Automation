from flask import Flask, request, jsonify, render_template_string
import sqlite3
from config import Config
from parser import parse_resume_text
from ranker import score_candidate_for_job
from email_bot import send_interview_email
import json
import os

app = Flask(__name__)
app.config.from_object(Config)

DB = Config.DATABASE_URL.replace("sqlite:///", "")

def get_db_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/jobs", methods=["POST"])
def create_job():
    payload = request.json
    title = payload.get("title")
    description = payload.get("description")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return jsonify({"job_id": job_id}), 201

@app.route("/candidates", methods=["POST"])
def add_candidate():
    data = request.form.to_dict()
    resume_text = request.form.get("resume_text")
    if not resume_text and request.files.get("resume_file"):
        resume_text = request.files.get("resume_file").read().decode('utf-8', errors='ignore')
    parsed = parse_resume_text(resume_text)
    name = parsed.get("name") or data.get("name")
    email = parsed.get("email") or data.get("email")
    phone = parsed.get("phone") or data.get("phone")
    skills = ",".join(parsed.get("skills", []))
    exp = parsed.get("experience_years", None)

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidates (name, email, phone, experience_years, skills, resume_text, parsed_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, phone, exp, skills, resume_text, json.dumps(parsed))
    )
    conn.commit()
    candidate_id = cur.lastrowid

    job_id = data.get("job_id")
    if job_id:
        job_row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if job_row:
            score = score_candidate_for_job(resume_text, job_row["description"])
            conn.execute("INSERT INTO applications (job_id, candidate_id, score) VALUES (?, ?, ?)", (job_id, candidate_id, float(score)))
            conn.commit()
    conn.close()
    return jsonify({"candidate_id": candidate_id}), 201

@app.route("/jobs/<int:job_id>/shortlist", methods=["GET"])
def shortlist(job_id):
    top_n = int(request.args.get("n", 5))
    conn = get_db_conn()
    rows = conn.execute(
        "SELECT a.id,a.score,c.id as candidate_id, c.name, c.email, c.skills FROM applications a JOIN candidates c ON a.candidate_id=c.id WHERE a.job_id=? ORDER BY a.score DESC LIMIT ?",
        (job_id, top_n)
    ).fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return jsonify(result)

@app.route("/applications/<int:app_id>/invite", methods=["POST"])
def invite(app_id):
    conn = get_db_conn()
    row = conn.execute("SELECT a.*, c.email, c.name FROM applications a JOIN candidates c ON a.candidate_id=c.id WHERE a.id=?", (app_id,)).fetchone()
    if not row:
        return jsonify({"error":"application not found"}), 404
    email_to = row["email"]
    candidate_name = row["name"]
    job_row = conn.execute("SELECT j.title FROM jobs j JOIN applications a ON a.job_id=j.id WHERE a.id=?", (app_id,)).fetchone()
    job_title = job_row["title"] if job_row else "Interview"
    subject = f"Interview Invitation - {job_title}"
    body = f"Hello {candidate_name},\n\nWe would like to invite you for an interview for the role of {job_title}. Please reply with available slots.\n\nRegards,\nHR Team"
    ok, err = send_interview_email(email_to, subject, body)
    if ok:
        conn.execute("UPDATE applications SET status='interviewed' WHERE id=?", (app_id,))
        conn.commit()
        conn.close()
        return jsonify({"status":"sent"})
    else:
        conn.close()
        return jsonify({"status":"failed", "error": str(err)}), 500

@app.route("/")
def index():
    conn = get_db_conn()
    total_jobs = conn.execute("SELECT count(*) as c FROM jobs").fetchone()["c"]
    total_candidates = conn.execute("SELECT count(*) as c FROM candidates").fetchone()["c"]
    total_applications = conn.execute("SELECT count(*) as c FROM applications").fetchone()["c"]
    conn.close()
    html = f"""
    <h1>Auto Hire RPA - Prototype Dashboard</h1>
    <p>Total jobs: {total_jobs}</p>
    <p>Total candidates: {total_candidates}</p>
    <p>Total applications: {total_applications}</p>
    <p>Use API endpoints to create jobs, upload resumes, and shortlist candidates.</p>
    """
    return render_template_string(html)

if __name__ == "__main__":
    if not os.path.exists(DB):
        with open("db_schema.sql", "r") as f:
            import sqlite3
            conn = sqlite3.connect(DB)
            conn.executescript(f.read())
            conn.commit()
            conn.close()
    app.run(host="0.0.0.0", port=8000, debug=True)
