from pathlib import Path
import re
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "career_skill_requirements.csv"
PROFILE_FILE = ROOT / "data" / "student_profiles.csv"

LEVEL_VALUE = {"Beginner": 33, "Intermediate": 66, "Advanced": 100}

ROLE_INTEREST = {
    "Full Stack Developer": "Web Development",
    "Software Development Engineer": "Software Development",
    "Data Analyst": "Data Science",
    "Data Scientist": "Artificial Intelligence / Machine Learning",
    "Cybersecurity Analyst": "Cybersecurity",
    "Cloud / DevOps Engineer": "Cloud Computing",
    "Mobile App Developer": "Mobile App Development",
    "UI/UX Designer": "UI/UX Design",
}

FEATURE_COLUMNS = [
    "skills_count", "projects_count", "internship", "certifications",
    "dsa", "dev", "cs", "comm", "apt", "github", "linkedin"
]


def normalize(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def load_career_data():
    df = pd.read_csv(DATA_FILE)
    return df.dropna(subset=["role", "skill"]).copy()


def load_profiles():
    return pd.read_csv(PROFILE_FILE).fillna(0)


def profile_features(profile):
    skills = profile.get("skills") or []
    experience = profile.get("experience") or {}
    levels = profile.get("preparationLevels") or {}
    return [
        len(skills),
        len(experience.get("projects") or []),
        0 if str(experience.get("internshipExp", "None")).lower() in ("none", "0", "") else 1,
        0 if not str(experience.get("certifications", "")).strip() else 1,
        LEVEL_VALUE.get(levels.get("dsa"), 0),
        LEVEL_VALUE.get(levels.get("dev"), 0),
        LEVEL_VALUE.get(levels.get("cs"), 0),
        LEVEL_VALUE.get(levels.get("comm"), 0),
        LEVEL_VALUE.get(levels.get("apt"), 0),
        1 if str(experience.get("githubLink", "")).strip() else 0,
        1 if str(experience.get("linkedinLink", "")).strip() else 0,
    ]


def clean_skills(skills):
    return {normalize(x): str(x).strip() for x in (skills or []) if str(x).strip()}


def role_requirements(df):
    return {role: group["skill"].tolist() for role, group in df.groupby("role")}


def explain_score(role, user_skills, levels, projects):
    required = role["required"]
    user_norm = {normalize(x) for x in user_skills}
    matched = [s for s in required if normalize(s) in user_norm]
    missing = [s for s in required if normalize(s) not in user_norm]
    coverage = round((len(matched) / len(required)) * 100) if required else 0
    level_avg = round(np.mean([LEVEL_VALUE.get(levels.get(k), 0) for k in ["dsa", "dev", "cs", "comm", "apt"]]))
    project_score = min(len(projects) / 3, 1) * 100
    readiness = round(coverage * 0.50 + level_avg * 0.30 + project_score * 0.20)
    contributions = [
        {"factor": "Required skill coverage", "value": coverage, "weight": 50, "effect": "positive" if coverage >= 60 else "needs-work"},
        {"factor": "Preparation level", "value": level_avg, "weight": 30, "effect": "positive" if level_avg >= 66 else "needs-work"},
        {"factor": "Project evidence", "value": round(project_score), "weight": 20, "effect": "positive" if project_score >= 67 else "needs-work"},
    ]
    return matched, missing, readiness, contributions


def cluster_profile(profile, profiles):
    matrix = profiles[FEATURE_COLUMNS].astype(float).values
    current = np.array(profile_features(profile), dtype=float).reshape(1, -1)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    current_scaled = scaler.transform(current)
    n_clusters = min(3, len(profiles))
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = model.fit_predict(scaled)
    label = int(model.predict(current_scaled)[0])
    centroid = model.cluster_centers_[label]
    names = {}
    for idx in range(n_clusters):
        avg = float(np.mean(model.cluster_centers_[idx]))
        names[idx] = "Skill Builder" if avg < -0.15 else ("Balanced Candidate" if avg < 0.45 else "Advanced Profile")
    distance = float(np.linalg.norm(current_scaled[0] - centroid))
    return {
        "cluster": label + 1,
        "label": names[label],
        "distance_to_cluster": round(distance, 3),
        "cluster_sizes": {str(i + 1): int((labels == i).sum()) for i in range(n_clusters)},
    }


def anomaly_profile(profile, profiles):
    matrix = profiles[FEATURE_COLUMNS].astype(float).values
    current = np.array(profile_features(profile), dtype=float).reshape(1, -1)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    current_scaled = scaler.transform(current)
    contamination = min(0.25, max(0.10, 2 / max(len(profiles), 4)))
    model = IsolationForest(random_state=42, contamination=contamination, n_estimators=150)
    model.fit(scaled)
    prediction = int(model.predict(current_scaled)[0])
    score = float(model.decision_function(current_scaled)[0])
    return {
        "is_anomaly": prediction == -1,
        "anomaly_score": round(score, 4),
        "interpretation": "Profile is unusual compared with the demo student population." if prediction == -1 else "Profile is within the normal range of the demo student population.",
    }


def analyze_profile(profile):
    df = load_career_data()
    profiles = load_profiles()
    req = role_requirements(df)
    skills = profile.get("skills") or []
    interests = profile.get("careerInterests") or []
    levels = profile.get("preparationLevels") or {}
    projects = (profile.get("experience") or {}).get("projects") or []

    role_results = []
    for role, required in req.items():
        matched, missing, readiness, contributions = explain_score(
            {"required": required}, skills, levels, projects
        )
        interest_match = ROLE_INTEREST.get(role) in interests
        rank_score = readiness + (10 if interest_match else 0)
        role_results.append({
            "role": role,
            "interest": ROLE_INTEREST.get(role, "Other"),
            "match": round((len(matched) / len(required)) * 100) if required else 0,
            "readiness": readiness,
            "matched": matched,
            "missing": missing,
            "interest_match": interest_match,
            "explanation": contributions,
            "rank_score": rank_score,
        })

    role_results.sort(key=lambda x: x["rank_score"], reverse=True)
    primary = role_results[0]
    cluster = cluster_profile(profile, profiles)
    anomaly = anomaly_profile(profile, profiles)

    all_missing = primary["missing"][:5]
    recommendations = [
        f"Learn {skill} because it is required by your selected role and is currently missing." for skill in all_missing
    ]
    if not recommendations:
        recommendations.append("Maintain your current core skills and strengthen project evidence.")

    return {
        "model": {
            "skill_matching": "CSV role-skill matrix + explainable weighted scoring",
            "clustering": "K-Means",
            "anomaly_detection": "Isolation Forest",
            "preprocessing": "Pandas + StandardScaler",
        },
        "primary_role": primary,
        "role_matches": role_results[:5],
        "cluster": cluster,
        "anomaly": anomaly,
        "recommendations": recommendations,
        "feature_vector": dict(zip(FEATURE_COLUMNS, profile_features(profile))),
        "dataset": {"career_rows": int(len(df)), "student_profiles": int(len(profiles))},
    }
