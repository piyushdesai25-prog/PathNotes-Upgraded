import os
from datetime import datetime


def save_analysis(profile, result):
    """Save an analysis to MySQL when configured; otherwise keep the app fully local."""
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE", "pathnotes")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    if not all([host, user, database]):
        return {"enabled": False, "message": "MySQL not configured; analysis returned without database storage."}
    try:
        import mysql.connector
        conn = mysql.connector.connect(host=host, user=user, password=password or "", database=database, port=port)
        cur = conn.cursor()
        sql = """INSERT INTO profile_analyses (student_name, primary_role, readiness, cluster_label, anomaly, created_at)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        personal = profile.get("personal") or {}
        primary = result.get("primary_role") or {}
        cur.execute(sql, (
            personal.get("fullName", "Student"),
            primary.get("role", "Unknown"),
            primary.get("readiness", 0),
            (result.get("cluster") or {}).get("label", "Unknown"),
            int(bool((result.get("anomaly") or {}).get("is_anomaly"))),
            datetime.utcnow(),
        ))
        conn.commit()
        cur.close()
        conn.close()
        return {"enabled": True, "message": "Analysis saved to MySQL."}
    except Exception as exc:
        return {"enabled": True, "saved": False, "message": f"MySQL connection failed: {exc}"}
