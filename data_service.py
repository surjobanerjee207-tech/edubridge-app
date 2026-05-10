"""
data_service.py — All dashboard data queries in one place.
All functions return live values from the SQLite database.
"""
from database import get_connection
from datetime import date, timedelta


# ── stat cards ───────────────────────────────────────────────────────────────

def get_career_match():
    """Latest career match % and week-over-week change."""
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute(
        "SELECT career_match, date FROM assessments ORDER BY date DESC LIMIT 2"
    ).fetchall()
    conn.close()
    if not rows:
        return 0, 0
    latest = rows[0][0]
    prev   = rows[1][0] if len(rows) > 1 else latest
    return latest, latest - prev


def get_skills_assessed():
    """Latest (assessed, total) skills count."""
    conn = get_connection()
    c = conn.cursor()
    row = c.execute(
        "SELECT skills_assessed, 20 FROM assessments ORDER BY date DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row if row else (0, 20)


def get_next_milestone():
    """Nearest upcoming milestone (title, days_away)."""
    today = date.today().strftime('%Y-%m-%d')
    conn  = get_connection()
    c     = conn.cursor()
    row   = c.execute(
        "SELECT title, due_date FROM milestones WHERE status='pending' AND due_date >= ? ORDER BY due_date ASC LIMIT 1",
        (today,)
    ).fetchone()
    conn.close()
    if not row:
        return "No milestones", 0
    title    = row[0]
    due      = date.fromisoformat(row[1])
    days_left = (due - date.today()).days
    return title, days_left


def get_day_streak():
    """Consecutive days with activity (counts from yesterday if today has none)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT log_date FROM activity_logs ORDER BY log_date DESC"
    ).fetchall()
    conn.close()

    dates  = {r[0] for r in rows}
    today  = date.today()
    check  = today if today.strftime('%Y-%m-%d') in dates else today - timedelta(days=1)

    streak = 0
    while check.strftime('%Y-%m-%d') in dates:
        streak += 1
        check  -= timedelta(days=1)
    return streak


# ── user preferences ───────────────────────────────────────────────────────────────

def get_preference(key: str, default: str = "") -> str:
    conn = get_connection()
    row  = conn.execute("SELECT value FROM user_preferences WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default


def set_preference(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?,?)",
        (key, value)
    )
    conn.commit()
    conn.close()


# ── assessment answers ─────────────────────────────────────────────────────────────

def get_assessment_answers():
    conn = get_connection()
    row  = conn.execute(
        "SELECT education_level, skills_raw, career_interests FROM assessment_answers ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        return "", "", ""
    return row[0] or "", row[1] or "", row[2] or ""


def save_assessment_answers(education: str, skills_raw: str, interests: str):
    from datetime import datetime
    conn = get_connection()
    conn.execute(
        "INSERT INTO assessment_answers (education_level, skills_raw, career_interests) VALUES (?,?,?)",
        (education, skills_raw, interests)
    )
    # Update user_skills table from parsed skills
    if skills_raw:
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
        for skill in skills:
            conn.execute(
                "INSERT OR IGNORE INTO user_skills (skill_name, proficiency) VALUES (?,?)",
                (skill, 50)
            )
        conn.execute(
            "INSERT INTO assessments (career_match, skills_assessed, date) VALUES (?,?,?)",
            (min(100, 60 + len(skills) * 2), len(skills), datetime.today().strftime('%Y-%m-%d'))
        )
    conn.commit()
    conn.close()


# ── weekly bar chart ─────────────────────────────────────────────────────────

def get_weekly_activity():
    """Returns list of (day_label, hours) for the last 7 days, oldest first."""
    today   = date.today()
    days    = [(today - timedelta(days=6-i)) for i in range(7)]
    day_strs = [d.strftime('%Y-%m-%d') for d in days]

    conn = get_connection()
    c    = conn.cursor()
    rows = c.execute(
        f"SELECT log_date, SUM(hours) FROM activity_logs "
        f"WHERE log_date IN ({','.join('?'*7)}) GROUP BY log_date",
        day_strs
    ).fetchall()
    conn.close()

    hours_map = {r[0]: r[1] for r in rows}
    labels    = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    result    = []
    for i, d in enumerate(days):
        result.append((labels[d.weekday()], hours_map.get(d.strftime('%Y-%m-%d'), 0)))
    return result


# ── career match trend (line chart) ─────────────────────────────────────────

def get_career_match_trend():
    """Returns list of (month_label, match_pct) for last 6 assessments."""
    conn = get_connection()
    c    = conn.cursor()
    rows = c.execute(
        "SELECT career_match, date FROM assessments ORDER BY date ASC LIMIT 6"
    ).fetchall()
    conn.close()

    result = []
    for match, dt in rows:
        month = date.fromisoformat(dt).strftime('%b')
        result.append((month, match))
    return result


# ── skill proficiency ────────────────────────────────────────────────────────

def get_skill_proficiencies():
    """Returns list of (skill_name, proficiency_pct)."""
    conn = get_connection()
    c    = conn.cursor()
    rows = c.execute(
        "SELECT skill_name, proficiency FROM user_skills ORDER BY proficiency DESC"
    ).fetchall()
    conn.close()
    return rows


# ── recent activity ──────────────────────────────────────────────────────────

def get_recent_activities(limit=4):
    """Returns list of (description, relative_time) for recent log entries."""
    conn = get_connection()
    c    = conn.cursor()
    rows = c.execute(
        "SELECT description, log_date FROM activity_logs ORDER BY log_date DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    today = date.today()
    result = []
    for desc, log_date in rows:
        d = date.fromisoformat(log_date)
        diff = (today - d).days
        if diff == 0:
            rel = "Today"
        elif diff == 1:
            rel = "Yesterday"
        else:
            rel = f"{diff} days ago"
        result.append((desc, rel))
    return result
