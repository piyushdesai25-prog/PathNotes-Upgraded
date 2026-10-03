from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
load_dotenv(ROOT / ".env")

from ml_engine import analyze_profile
from database import save_analysis

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
CORS(app)


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:filename>")
def frontend(filename):
    # Serve the existing HTML/CSS/JS frontend from the project root.
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    target = ROOT / filename
    if target.is_file():
        return send_from_directory(ROOT, filename)
    return jsonify({"error": "Frontend file not found", "file": filename}), 404

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "PathNotes AI API"})

@app.get("/api/dataset-info")
def dataset_info():
    from ml_engine import load_career_data
    df = load_career_data()
    return jsonify({
        "rows": int(len(df)),
        "columns": list(df.columns),
        "roles": sorted(df["role"].unique().tolist()),
        "skills": sorted(df["skill"].unique().tolist()),
    })

@app.post("/api/analyze-profile")
def analyze():
    payload = request.get_json(silent=True) or {}
    try:
        result = analyze_profile(payload)
        db_status = save_analysis(payload, result)
        result["database"] = db_status
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/what-if")
def what_if():
    payload = request.get_json(silent=True) or {}
    extra_skills = payload.get("addSkills") or []
    base = payload.get("profile") or {}
    current = list(base.get("skills") or [])
    existing = {str(x).strip().lower() for x in current}
    for skill in extra_skills:
        skill = str(skill).strip()
        if skill and skill.lower() not in existing:
            current.append(skill)
            existing.add(skill.lower())
    hypothetical = dict(base)
    hypothetical["skills"] = current
    before = analyze_profile(base)
    after = analyze_profile(hypothetical)
    b = before.get("primary_role", {})
    a = after.get("primary_role", {})
    return jsonify({
        "added_skills": [x for x in current if x not in (base.get("skills") or [])],
        "before": {"role": b.get("role"), "readiness": b.get("readiness", 0), "missing": b.get("missing", [])},
        "after": {"role": a.get("role"), "readiness": a.get("readiness", 0), "missing": a.get("missing", [])},
        "improvement": a.get("readiness", 0) - b.get("readiness", 0),
        "explanation": a.get("explanation", [])
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
