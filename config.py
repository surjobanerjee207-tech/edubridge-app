import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "EduBridge AI"
    
    # Local AI Settings (LM Studio / Ollama)
    AI_PROVIDER = "local" 
    AI_HOST = os.getenv("AI_HOST", "http://localhost:1234/v1")
    AI_MODEL = os.getenv("AI_MODEL", "google/gemma-3-4b")
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", r"D:\LM models\lmstudio-community")
    
    DB_PATH = os.getenv("DB_PATH", "edubridge.db")
    
    # AI Ethics & Disclaimers
    AI_DISCLAIMER = "AI suggestions are not medical advice. Use for educational purposes only."
    
    # Theme Settings
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#0D47A1"
    DARK_MODE = True
    DYSLEXIA_FONT = "OpenDyslexic"
