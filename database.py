import sqlite3
from datetime import date, timedelta
from config import Config

# Persistent shared connection — avoids reopening SQLite on every query
_shared_conn: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection."""
    conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def get_dashboard_data() -> dict:
    """Fetch ALL dashboard data in a single DB round-trip."""
    conn  = get_connection()
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')

    # ── career match ──────────────────────────────────────────────────────────
    rows = conn.execute(
        "SELECT career_match FROM assessments ORDER BY date DESC LIMIT 2"
    ).fetchall()
    if rows:
        latest_match = rows[0][0]
        prev_match   = rows[1][0] if len(rows) > 1 else latest_match
        career_match  = latest_match
        match_change  = latest_match - prev_match
    else:
        career_match, match_change = 0, 0

    # ── skills assessed ───────────────────────────────────────────────────────
    row = conn.execute(
        "SELECT skills_assessed FROM assessments ORDER BY date DESC LIMIT 1"
    ).fetchone()
    skills_done  = row[0] if row else 0
    skills_total = 20

    # ── next milestone ────────────────────────────────────────────────────────
    row = conn.execute(
        "SELECT title, due_date FROM milestones "
        "WHERE status='pending' AND due_date>=? ORDER BY due_date ASC LIMIT 1",
        (today_str,)
    ).fetchone()
    if row:
        milestone_title = row[0]
        days_left = (date.fromisoformat(row[1]) - today).days
    else:
        milestone_title, days_left = "No milestones", 0

    # ── day streak ────────────────────────────────────────────────────────────
    date_rows = conn.execute(
        "SELECT DISTINCT log_date FROM activity_logs ORDER BY log_date DESC"
    ).fetchall()
    dates = {r[0] for r in date_rows}
    check = today if today_str in dates else today - timedelta(days=1)
    streak = 0
    while check.strftime('%Y-%m-%d') in dates:
        streak += 1
        check  -= timedelta(days=1)

    # ── weekly activity ───────────────────────────────────────────────────────
    days     = [(today - timedelta(days=6-i)) for i in range(7)]
    day_strs = [d.strftime('%Y-%m-%d') for d in days]
    w_rows   = conn.execute(
        f"SELECT log_date, SUM(hours) FROM activity_logs "
        f"WHERE log_date IN ({','.join('?'*7)}) GROUP BY log_date",
        day_strs
    ).fetchall()
    hours_map   = {r[0]: r[1] for r in w_rows}
    day_labels  = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    weekly_data = [(day_labels[d.weekday()], hours_map.get(d.strftime('%Y-%m-%d'), 0)) for d in days]

    # ── career match trend ────────────────────────────────────────────────────
    t_rows = conn.execute(
        "SELECT career_match, date FROM assessments ORDER BY date ASC LIMIT 6"
    ).fetchall()
    trend_data = [(date.fromisoformat(dt).strftime('%b'), m) for m, dt in t_rows]

    # ── skill proficiencies ───────────────────────────────────────────────────
    skill_rows = conn.execute(
        "SELECT skill_name, proficiency FROM user_skills ORDER BY proficiency DESC"
    ).fetchall()

    # ── recent activities ─────────────────────────────────────────────────────
    act_rows = conn.execute(
        "SELECT description, log_date FROM activity_logs ORDER BY log_date DESC LIMIT 5"
    ).fetchall()
    activities = []
    for desc, log_date in act_rows:
        diff = (today - date.fromisoformat(log_date)).days
        rel  = "Today" if diff == 0 else "Yesterday" if diff == 1 else f"{diff} days ago"
        activities.append((desc, rel))

    conn.close()

    return {
        "career_match":    career_match,
        "match_change":    match_change,
        "skills_done":     skills_done,
        "skills_total":    skills_total,
        "milestone_title": milestone_title,
        "days_left":       days_left,
        "streak":          streak,
        "weekly_data":     weekly_data,
        "trend_data":      trend_data,
        "skill_rows":      skill_rows,
        "activities":      activities,
    }

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ── existing tables ──────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, due_date TEXT, priority TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, category TEXT, location TEXT,
        contact TEXT, open_hours TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mood_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER, note TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assessment_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        education_level TEXT,
        skills_raw TEXT,
        career_interests TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ── career assessment history ─────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        career_match INTEGER,
        skills_assessed INTEGER,
        date TEXT NOT NULL
    )''')

    # ── user skills ──────────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL UNIQUE,
        proficiency INTEGER DEFAULT 0,
        total_skills INTEGER DEFAULT 20,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ── daily activity log ───────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT NOT NULL,
        hours REAL DEFAULT 0,
        description TEXT,
        activity_type TEXT DEFAULT 'learning',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ── milestones ───────────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # ── search history ───────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ── seed data (only once) ────────────────────────────────────────────────
    today = date.today()

    # Resources seed
    c.execute("SELECT COUNT(*) FROM resources")
    if c.fetchone()[0] == 0:
        c.executemany(
            'INSERT INTO resources (name,category,location,contact,open_hours) VALUES (?,?,?,?,?)',
            [
                ('Campus Counseling', 'Wellbeing',  'Building A, Room 101', '555-0199', '9AM-5PM'),
                ('City Food Bank',    'Social Work','123 Main St',           '555-0200', '10AM-4PM'),
                ('Academic Success',  'Education',  'Library Floor 2',       '555-0201', '8AM-8PM'),
            ]
        )

    # Assessment history (last 6 months)
    c.execute("SELECT COUNT(*) FROM assessments")
    if c.fetchone()[0] == 0:
        months = [(today - timedelta(days=30*i)) for i in range(5, -1, -1)]
        scores = [62, 65, 68, 72, 79, 85]
        skills = [6, 8, 9, 10, 11, 12]
        for i, d in enumerate(months):
            c.execute(
                "INSERT INTO assessments (career_match, skills_assessed, date) VALUES (?,?,?)",
                (scores[i], skills[i], d.strftime('%Y-%m-%d'))
            )

    # Skills seed
    c.execute("SELECT COUNT(*) FROM user_skills")
    if c.fetchone()[0] == 0:
        skills_data = [
            ('Python',     78),
            ('SQL',        65),
            ('ML Basics',  42),
            ('Data Viz',   55),
            ('Statistics', 38),
        ]
        for name, prof in skills_data:
            c.execute(
                "INSERT INTO user_skills (skill_name, proficiency, total_skills) VALUES (?,?,?)",
                (name, prof, 20)
            )

    # Activity logs (last 7 days)
    c.execute("SELECT COUNT(*) FROM activity_logs")
    if c.fetchone()[0] == 0:
        hours  = [1.5,  2.0,  1.8,  3.0,  2.5,  1.0,  0.5]
        descs  = [
            'Completed Python Basics Assessment',
            'Roadmap updated — ML Engineer track added',
            'Resume Uploaded & Analyzed',
            'New course: Data Structures added',
            'Practiced SQL exercises',
            'Reviewed ML concepts',
            'Read career articles',
        ]
        for i in range(7):
            log_date = (today - timedelta(days=6-i)).strftime('%Y-%m-%d')
            c.execute(
                "INSERT INTO activity_logs (log_date, hours, description, activity_type) VALUES (?,?,?,?)",
                (log_date, hours[i], descs[i], 'learning')
            )

    # Milestones seed
    c.execute("SELECT COUNT(*) FROM milestones")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO milestones (title, due_date, status) VALUES (?,?,?)",
            [
                ('Python Certification', (today + timedelta(days=3)).strftime('%Y-%m-%d'), 'pending'),
                ('SQL Advanced Course',  (today + timedelta(days=14)).strftime('%Y-%m-%d'), 'pending'),
                ('Resume Review',        (today + timedelta(days=7)).strftime('%Y-%m-%d'), 'pending'),
            ]
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
