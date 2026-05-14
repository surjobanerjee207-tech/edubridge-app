# 🎓 EduBridge AI

**EduBridge AI** is a cross-platform (Windows, macOS, Linux, Android, iOS) application designed to reduce student workload and support academic wellbeing using local, private AI.

## 🚀 Features
- **AI Study Planner**: Automatically generate weekly study schedules from your task list.
- **AI Document Assistant**: Summarize PDFs/TXTs and generate instant quizzes.
- **Community Navigator**: Browse local NGOs, counseling services, and campus resources.
- **Wellbeing Tracker**: Track your mood and receive AI-powered coping suggestions.
- **Privacy First**: Runs 100% locally via Ollama. Your data never leaves your device.

## 🛠️ Setup & Installation

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com).

### 2. Pull the AI Model
Open your terminal and run:
```bash
ollama pull gemma2:9b
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python main.py
```

## 📦 Packaging for Distribution
To build a standalone executable:
```bash
# Windows
flet build windows

# Android
flet build android

# iOS
flet build ios
```

## ⚖️ IBM Alignment & Ethics
- **Privacy**: Local-only data storage (SQLite) and local AI processing (Ollama).
- **Accessibility**: High-contrast dark mode, dyslexic-friendly font support (configurable).
- **Ethics**: AI suggestions include clear disclaimers that they are not medical or professional advice.
- **Transparency**: Clear indicators when content is AI-generated.

## 📄 License
Apache 2.0
hi

