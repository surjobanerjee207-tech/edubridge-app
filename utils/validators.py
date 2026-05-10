import re

def sanitize_text(text):
    # Remove potentially harmful characters for LLM injection or Shell injection
    return re.sub(r'[<>{}[\]]', '', text)

def validate_mood_score(score):
    try:
        s = int(score)
        return 1 <= s <= 5
    except:
        return False
