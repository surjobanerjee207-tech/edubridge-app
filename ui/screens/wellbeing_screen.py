import flet as ft
import threading
from ui.theme import get_colors
from database import get_connection
from ai_engine.wellbeing import WellbeingAdvisor


def wellbeing_screen(page: ft.Page):
    colors = get_colors(page)
    advisor = WellbeingAdvisor()

    mood_slider   = ft.Slider(min=1, max=5, divisions=4, label="{value}/5",
                               active_color=colors.PRIMARY)
    journal_input = ft.TextField(
        hint_text="How are you feeling today?",
        multiline=True, min_lines=4,
        bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY),
    )
    ai_area      = ft.Ref[ft.Column]()
    history_area = ft.Ref[ft.Column]()

    MOOD_LABELS = {1: "😞 Very Low", 2: "😕 Low", 3: "😐 Okay", 4: "🙂 Good", 5: "😄 Great"}
    MOOD_COLORS = {1: "#ef4444", 2: "#f97316", 3: "#f59e0b", 4: "#22c55e", 5: "#10b981"}

    def load_history():
        conn = get_connection()
        rows = conn.execute(
            "SELECT score, note, date FROM mood_logs ORDER BY date DESC LIMIT 5"
        ).fetchall()
        conn.close()
        return rows

    def refresh_history():
        rows = load_history()
        if not rows:
            history_area.current.controls = [
                ft.Text("No mood logs yet.", size=13, color=colors.TEXT_SECONDARY)
            ]
        else:
            history_area.current.controls = [
                ft.Container(
                    bgcolor=colors.SURFACE, border_radius=10,
                    border=ft.Border.all(1, colors.BORDER),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row([
                        ft.Container(width=10, height=10, border_radius=5,
                                     bgcolor=MOOD_COLORS.get(int(score), "#94a3b8")),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text(MOOD_LABELS.get(int(score), str(score)),
                                    size=13, color=colors.TEXT_PRIMARY,
                                    weight=ft.FontWeight.W_500),
                            ft.Text(note[:60] + "…" if note and len(note) > 60 else note or "",
                                    size=11, color=colors.TEXT_SECONDARY),
                        ], spacing=2, expand=True),
                        ft.Text(str(dt)[:10], size=11, color=colors.TEXT_SECONDARY),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
                for score, note, dt in rows
            ]
        history_area.current.update()

    def save_mood(e):
        score = int(mood_slider.value or 3)
        note  = journal_input.value or ""

        conn = get_connection()
        conn.execute("INSERT INTO mood_logs (score, note) VALUES (?,?)", (score, note))
        conn.commit()
        conn.close()

        ai_area.current.controls = [
            ft.Row([ft.ProgressRing(width=20, height=20, stroke_width=2,
                                    color=colors.PRIMARY),
                    ft.Container(width=10),
                    ft.Text("Getting AI wellness tip…", size=13,
                            color=colors.TEXT_SECONDARY)])
        ]
        ai_area.current.update()
        refresh_history()

        def _run():
            tip = advisor.get_suggestion(score, note)
            ai_area.current.controls = [
                ft.Container(
                    bgcolor=f"{colors.PRIMARY}18",
                    border_radius=10,
                    border=ft.Border.all(1, f"{colors.PRIMARY}40"),
                    padding=16,
                    content=ft.Text(tip, size=14, italic=True, color=colors.TEXT_PRIMARY),
                )
            ]
            ai_area.current.update()

        threading.Thread(target=_run, daemon=True).start()
        journal_input.value = ""
        journal_input.update()

    initial_hist = load_history()
    initial_hist_controls = (
        [ft.Text("No mood logs yet.", size=13, color=colors.TEXT_SECONDARY)]
        if not initial_hist else
        [ft.Container(
            bgcolor=colors.SURFACE, border_radius=10,
            border=ft.Border.all(1, colors.BORDER),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row([
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor=MOOD_COLORS.get(int(s), "#94a3b8")),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(MOOD_LABELS.get(int(s), str(s)), size=13, color=colors.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_500),
                    ft.Text((n or "")[:60], size=11, color=colors.TEXT_SECONDARY),
                ], spacing=2, expand=True),
                ft.Text(str(dt)[:10], size=11, color=colors.TEXT_SECONDARY),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ) for s, n, dt in initial_hist]
    )

    return ft.Container(
        expand=True, bgcolor=colors.BACKGROUND,
        padding=ft.Padding.all(28),
        content=ft.Column([
            ft.Text("Mood & Wellbeing", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_PRIMARY),
            ft.Text("Track your mood and receive AI-powered wellness suggestions.",
                    size=15, color=colors.TEXT_SECONDARY),
            ft.Container(height=24),

            ft.Row([
                # Left: form
                ft.Container(
                    expand=1,
                    bgcolor=colors.SURFACE, border_radius=14,
                    border=ft.Border.all(1, colors.BORDER), padding=24,
                    content=ft.Column([
                        ft.Text("How are you feeling? (1 = Very Low · 5 = Great)",
                                size=14, color=colors.TEXT_SECONDARY),
                        mood_slider,
                        ft.Container(height=8),
                        journal_input,
                        ft.Container(height=12),
                        ft.ElevatedButton("Save & Get AI Tip", icon=ft.Icons.FAVORITE,
                                          bgcolor=colors.PRIMARY, color="#ffffff",
                                          on_click=save_mood,
                                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                        ft.Container(height=16),
                        ft.Text("AI Suggestion", size=14, weight=ft.FontWeight.W_600,
                                color=colors.TEXT_PRIMARY),
                        ft.Container(height=8),
                        ft.Column(ref=ai_area, controls=[
                            ft.Text("Log your mood to get a personalised tip.",
                                    size=13, color=colors.TEXT_SECONDARY)
                        ], spacing=0),
                    ], spacing=4),
                ),
                ft.Container(width=20),
                # Right: history
                ft.Container(
                    expand=1,
                    bgcolor=colors.SURFACE, border_radius=14,
                    border=ft.Border.all(1, colors.BORDER), padding=24,
                    content=ft.Column([
                        ft.Text("Recent Mood History", size=16, weight=ft.FontWeight.W_600,
                                color=colors.TEXT_PRIMARY),
                        ft.Container(height=12),
                        ft.Column(ref=history_area, controls=initial_hist_controls, spacing=8),
                    ], spacing=0),
                ),
            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )
