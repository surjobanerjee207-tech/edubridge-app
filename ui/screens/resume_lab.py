import flet as ft
import threading
import os
import tkinter as tk
from tkinter import filedialog
from ui.theme import get_colors


# ── simple resume analyser ────────────────────────────────────────────────────

KEYWORDS = ["python", "java", "sql", "javascript", "react", "aws", "docker",
            "machine learning", "data analysis", "communication", "leadership",
            "project management", "agile", "git", "excel", "tableau", "tensorflow"]

SECTION_HEADERS = ["experience", "education", "skills", "projects",
                   "summary", "objective", "certifications", "achievements"]


def _analyse_resume(text: str) -> dict:
    lower = text.lower()
    words = len(text.split())

    found_kw  = [k for k in KEYWORDS if k in lower]
    found_sec = [s for s in SECTION_HEADERS if s in lower]

    keyword_score = min(40, len(found_kw) * 4)
    section_score = min(30, len(found_sec) * 5)
    length_score  = 20 if 300 <= words <= 800 else (10 if words > 100 else 0)
    format_score  = 10 if any(c in text for c in ['•', '-', '●', '▪']) else 5
    total = keyword_score + section_score + length_score + format_score

    missing_sec = [s.title() for s in SECTION_HEADERS if s not in lower]
    missing_kw  = [k.title() for k in ["Python", "Git", "Communication", "Leadership"]
                   if k.lower() not in lower]

    strengths = []
    if found_kw:  strengths.append(f"Good keyword coverage ({len(found_kw)} found)")
    if found_sec: strengths.append(f"Clear section structure ({len(found_sec)} sections)")
    if 300 <= words <= 800: strengths.append("Appropriate resume length")

    suggestions = []
    if missing_sec: suggestions.append(f"Add missing section: {missing_sec[0]}")
    if missing_kw:  suggestions.append(f"Include key skill: {missing_kw[0]}")
    if words < 300: suggestions.append("Expand content — resume is too short")
    if not found_kw: suggestions.append("Include industry-relevant keywords")
    if not suggestions: suggestions.append("Resume looks good! Consider adding more keywords.")

    return {
        "score": min(100, total),
        "word_count": words,
        "keywords_found": found_kw,
        "strengths": strengths or ["Resume uploaded successfully"],
        "suggestions": suggestions,
    }


def _try_read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            except ImportError:
                return "Error: pypdf not installed. Run: pip install pypdf"
        else:
            return f"Error: Unsupported file type '{ext}'. Use .txt or .pdf."
    except Exception as ex:
        return f"Error reading file: {ex}"


def _pick_file_native() -> str:
    """Open native OS file dialog — no Flet FilePicker needed."""
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select your resume",
        filetypes=[("Resume files", "*.pdf *.txt"), ("All files", "*.*")],
    )
    root.destroy()
    return path or ""


# ── screen ────────────────────────────────────────────────────────────────────

def resume_lab_screen(page: ft.Page):
    colors = get_colors(page)

    result_area   = ft.Ref[ft.Column]()
    filename_text = ft.Ref[ft.Text]()
    choose_btn    = ft.Ref[ft.ElevatedButton]()

    def _show_loading():
        result_area.current.controls = [
            ft.Row([
                ft.ProgressRing(width=20, height=20, stroke_width=2, color=colors.PRIMARY),
                ft.Container(width=12),
                ft.Text("Analysing resume…", size=14, color=colors.TEXT_SECONDARY),
            ])
        ]
        result_area.current.update()

    def _show_results(analysis: dict):
        score = analysis["score"]
        score_color = "#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"

        strength_rows = [
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color="#10b981", size=16),
                    ft.Container(width=8),
                    ft.Text(s, size=13, color=colors.TEXT_PRIMARY)], spacing=0)
            for s in analysis["strengths"]
        ]
        suggestion_rows = [
            ft.Row([ft.Icon(ft.Icons.LIGHTBULB, color=colors.WARNING, size=16),
                    ft.Container(width=8),
                    ft.Text(s, size=13, color=colors.TEXT_PRIMARY)], spacing=0)
            for s in analysis["suggestions"]
        ]

        result_area.current.controls = [
            ft.Container(
                bgcolor=colors.SURFACE,
                border_radius=14,
                border=ft.Border.all(1, colors.BORDER),
                padding=24,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("ATS Score", size=14, color=colors.TEXT_SECONDARY),
                            ft.Text(f"{score}/100", size=48,
                                    weight=ft.FontWeight.BOLD, color=score_color),
                            ft.Text(f"{analysis['word_count']} words · "
                                    f"{len(analysis['keywords_found'])} keywords",
                                    size=12, color=colors.TEXT_SECONDARY),
                        ], spacing=2),
                        ft.Container(width=40),
                        ft.Column([
                            ft.Text("Strengths", size=16, weight=ft.FontWeight.W_600,
                                    color=colors.TEXT_PRIMARY),
                            *strength_rows,
                        ], spacing=8),
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Divider(color=colors.BORDER),
                    ft.Text("Suggested Improvements", size=16, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Container(
                        bgcolor=colors.BACKGROUND, border_radius=8, padding=14,
                        content=ft.Column(suggestion_rows, spacing=10),
                    ),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        "Analyse Another Resume",
                        icon=ft.Icons.UPLOAD_FILE,
                        bgcolor=colors.PRIMARY, color="#ffffff",
                        on_click=on_choose_file,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=16),
            )
        ]
        result_area.current.update()

    def _show_error(msg: str):
        result_area.current.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color="#ef4444"),
                    ft.Container(width=10),
                    ft.Text(msg, color="#ef4444", size=13),
                ]),
                padding=20,
            )
        ]
        result_area.current.update()

    def on_choose_file(e):
        def _pick_and_analyse():
            path = _pick_file_native()
            if not path:
                return
            fname = os.path.basename(path)
            filename_text.current.value   = f"📄 {fname}"
            filename_text.current.visible = True
            filename_text.current.update()
            page.update()
            _show_loading()
            text = _try_read_file(path)
            if text.startswith("Error"):
                _show_error(text)
            else:
                _show_results(_analyse_resume(text))

        threading.Thread(target=_pick_and_analyse, daemon=True).start()

    return ft.Container(
        expand=True,
        bgcolor="transparent",
        padding=ft.Padding.all(28),
        content=ft.Column([
            ft.Text("Resume Lab", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_WHITE),
            ft.Text("AI-powered ATS resume analysis", size=15, color=colors.TEXT_55),
            ft.Container(height=24),

            # Upload zone
            ft.Container(
                width=580, height=185,
                bgcolor=colors.GLASS_WEAK,
                border_radius=16,
                border=ft.Border.all(2, colors.PRIMARY),
                padding=30,
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_UPLOAD, size=52, color=colors.PRIMARY),
                    ft.Text("Drop your resume here or click to browse",
                            size=15, color=colors.TEXT_WHITE),
                    ft.Text("Supports PDF, TXT", size=12, color=colors.TEXT_55),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        ref=choose_btn,
                        text="Choose File",
                        bgcolor=colors.PRIMARY, color="#ffffff",
                        on_click=on_choose_file,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            ),

            ft.Container(height=10),
            ft.Text("", ref=filename_text, size=13, color=colors.PRIMARY, visible=False),
            ft.Container(height=16),
            ft.Column(ref=result_area, controls=[], spacing=0),
            ft.Container(height=20),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )
