from database import get_connection
import time
import json

def save_search_history(page, query):
    if not query:
        return
    conn = get_connection()
    # Remove existing to move to top
    conn.execute("DELETE FROM search_history WHERE query = ?", (query,))
    conn.execute("INSERT INTO search_history (query) VALUES (?)", (query,))
    # Keep last 50
    conn.execute("DELETE FROM search_history WHERE id NOT IN (SELECT id FROM search_history ORDER BY created_at DESC LIMIT 50)")
    conn.commit()
    conn.close()

def load_search_history(page):
    conn = get_connection()
    rows = conn.execute("SELECT query FROM search_history ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return [{"q": r[0]} for r in rows]

def save_chat_log(page, messages):
    """Saves the entire chat session log. We'll store it as a JSON string in user_preferences for simplicity."""
    from data_service import set_preference
    set_preference("career_chat_log", json.dumps(messages))

def load_chat_log(page):
    """Loads the saved chat session log."""
    from data_service import get_preference
    log = get_preference("career_chat_log", "[]")
    return json.loads(log)

def clear_history(page):
    conn = get_connection()
    conn.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()
    from data_service import set_preference
    set_preference("career_chat_log", "[]")
