# PathNotes — AI/ML Upgrade

This version keeps the original frontend and adds a real Python machine-learning layer.

## New architecture

```text
HTML/CSS/JavaScript
        |
        | POST /api/analyze-profile
        v
Flask API (Python)
        |
        +-- Pandas -> reads career_skill_requirements.csv
        +-- NumPy -> feature vectors / calculations
        +-- Scikit-learn -> K-Means + Isolation Forest + StandardScaler
        +-- Explainable scoring -> skill coverage + preparation + projects
        +-- MySQL (optional) -> stores analysis history
```

## Models

### 1. Skill-gap / role matching
A CSV role-skill matrix is loaded using Pandas. The API compares the student's normalized skills with required skills for each role and reports matched/missing skills.

### 2. K-Means clustering
The profile is converted into a numerical feature vector containing skill count, projects, internship/certification signals, preparation levels and profile links. StandardScaler normalizes these values before K-Means groups the student with similar demo profiles.

### 3. Isolation Forest
Isolation Forest checks whether the student's feature vector is unusual compared with the included demo student population. The result is presented as an anomaly signal, not as a judgement about the student.

### 4. Explainability
The readiness value is decomposed into visible factors:
- 50% required-skill coverage
- 30% preparation level
- 20% project evidence

The UI shows the individual factor values and missing skills instead of presenting an unexplained AI number.

## Run on Windows

```powershell
cd PathNotes
python -m venv .venv
.venv\\Scripts\\activate
pip install -r backend\\requirements.txt
python backend\\app.py
```

Then open `dashboard.html` using a local web server. A simple option is:

```powershell
python -m http.server 5500
```

Open `http://127.0.0.1:5500/`.

## Run on Linux/macOS

```bash
cd PathNotes
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

In another terminal:

```bash
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500/`.

## MySQL

1. Install MySQL Server.
2. Run `sql/schema.sql` in MySQL.
3. Copy `.env.example` to `.env` and enter your MySQL password.
4. Start the Flask API.

If MySQL is not configured, PathNotes still works and simply skips database storage.

## Dataset

`data/career_skill_requirements.csv` is a project dataset derived from the role requirements already used by the frontend. It is deliberately kept as CSV so it can be replaced with a larger Kaggle/government dataset later without changing the API contract.

`data/student_profiles.csv` is a small demo population for the unsupervised-learning modules. For a stronger final project, replace it with a larger anonymized student-skill dataset.

## Start the complete website locally (recommended)

From the `PathNotes` root folder on Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r backend\requirements.txt
python backend\app.py
```

Then open **http://127.0.0.1:5000/**. Flask now serves the existing frontend, so you do not need a separate Live Server terminal.

## New What-If Skill Simulator

The dashboard includes an interactive simulator. Enter skills such as `SQL, Power BI` and PathNotes sends the current profile plus those hypothetical skills to `/api/what-if`. The backend runs the same analysis again and reports before/after readiness, remaining gaps and explanation factors.
