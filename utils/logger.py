import json
import datetime
import os

LOG_FILE = "app_logs.json"

def log_event(event_type, details):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "details": details
    }
    
    # Simple JSON append (local only, no cloud)
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []
            
    logs.append(log_entry)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs[-100:], f, indent=2) # Keep last 100 logs
