import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "EduBridge AI"
    # Switched from local Ollama to Groq Cloud API. Note: Groq decommissioned Gemma models, using Llama 3.1 8B as fallback.
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://api.groq.com/openai/v1/chat/completions")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama-3.1-8b-instant")
    DB_PATH = os.getenv("DB_PATH", "edubridge.db")
    
    # AI Ethics & Disclaimers
    AI_DISCLAIMER = "AI suggestions are not medical advice. Use for educational purposes only."
    
    # Theme Settings
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#0D47A1"
    DARK_MODE = True
    DYSLEXIA_FONT = "OpenDyslexic"  # Fallback to standard if not found
