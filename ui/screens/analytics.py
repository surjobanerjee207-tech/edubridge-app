import flet as ft
import threading
from ui.theme import GlassColors
from database import get_dashboard_data

C = GlassColors()

def _anim_wrap(page, content, delay: float, dy: float = 0.05):
    c = ft.Container(
        content=content,
        opacity=0,
        offset=ft.Offset(0, dy),
        animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
    )
    def _fire():
        try:
            c.opacity = 1
            c.offset  = ft.Offset(0, 0)
            page.update()
        except Exception:
            pass
    threading.Timer(delay, _fire).start()
    return c

def glass(content, padding=20, expand=False, height=None, strong=False):
    bg     = C.GLASS_MED if strong else C.GLASS_WEAK
    border = C.BORDER_MED if strong else C.BORDER_WEAK
    return ft.Container(
        content=content,
        bgcolor=bg,
        border_radius=16,
        border=ft.Border.all(1, border),
        shadow=ft.BoxShadow(blur_radius=32, color=C.SHADOW),
        padding=padding,
        expand=expand,
        height=height,
    )

def analytics_screen(page: ft.Page):
    data = get_dashboard_data()
    
    # ── Header ───────────────────────────────────────────────────────────────
    header = ft.Row([
        ft.Column([
            ft.Text("Career Analytics", size=28, weight=ft.FontWeight.BOLD, color="#ffffff"),
            ft.Text("Deep dive into your professional growth and learning patterns.", size=14, color=C.TEXT_55),
        ], expand=True),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=16, color=C.TEXT_45),
                ft.Text("Last 30 Days", size=13, color=C.TEXT_45),
            ], spacing=8),
            bgcolor=C.GLASS_WEAK,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            border_radius=10,
            border=ft.Border.all(1, C.BORDER_WEAK),
        )
    ])

    # ── Readiness Score ──────────────────────────────────────────────────────
    readiness_card = glass(
        height=220,
        content=ft.Column([
            ft.Text("Career Readiness", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
            ft.Container(
                expand=True, 
                alignment=ft.alignment.Alignment(0, 0), 
                content=ft.Stack([
                    ft.ProgressRing(
                        value=data["career_match"] / 100,
                        stroke_width=12,
                        color="#6366f1",
                        bgcolor="#1affffff",
                        width=100,
                        height=100,
                    ),
                    ft.Column([
                        ft.Text(f"{data['career_match']}%", size=22, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ft.Text("Score", size=10, color=C.TEXT_45),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
                ], alignment=ft.alignment.Alignment(0, 0))
            )
        ], spacing=10)
    )

    # ── Weekly Activity ──────────────────────────────────────────────────────
    weekly_bars = []
    max_h = max([h for _, h in data["weekly_data"]] + [1])
    for day, hours in data["weekly_data"]:
        bar_h = (hours / max_h) * 100
        weekly_bars.append(
            ft.Column([
                ft.Container(
                    width=20, height=bar_h, 
                    gradient=ft.LinearGradient(["#6366f1", "#a855f7"], begin=ft.alignment.Alignment(0, 1), end=ft.alignment.Alignment(0, -1)),
                    border_radius=4,
                ),
                ft.Text(day[:1], size=10, color=C.TEXT_45)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, alignment=ft.MainAxisAlignment.END)
        )

    activity_card = glass(
        height=220,
        expand=True,
        content=ft.Column([
            ft.Text("Learning Consistency", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
            ft.Container(height=10),
            ft.Row(weekly_bars, alignment=ft.MainAxisAlignment.SPACE_AROUND, expand=True, vertical_alignment=ft.CrossAxisAlignment.END)
        ])
    )

    # ── Skill Matrix ─────────────────────────────────────────────────────────
    skill_rows = []
    for name, pct in data["skill_rows"][:4]:
        skill_rows.append(
            ft.Column([
                ft.Row([
                    ft.Text(name, size=13, color="#ffffff", expand=True),
                    ft.Text(f"{pct}%", size=12, color=C.TEXT_55),
                ]),
                ft.ProgressBar(value=pct/100, color="#a855f7", bgcolor="#1affffff", height=4, border_radius=10)
            ], spacing=6)
        )
    
    skills_card = glass(
        expand=True,
        content=ft.Column([
            ft.Text("Skill Proficiency", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
            ft.Container(height=10),
            ft.Column(skill_rows, spacing=16)
        ])
    )

    # ── Growth Insights ──────────────────────────────────────────────────────
    insights = [
        ("Consistency", f"You've hit a {data['streak']} day streak!"),
        ("Match Improvement", f"Your match grew by {data['match_change']}% recently."),
        ("Milestones", f"'{data['milestone_title']}' is your next target.")
    ]
    insight_widgets = []
    for title, desc in insights:
        insight_widgets.append(
            ft.Container(
                padding=12,
                bgcolor="#1affffff",
                border_radius=12,
                content=ft.Row([
                    ft.Icon(ft.Icons.INSIGHTS, size=18, color="#6366f1"),
                    ft.Column([
                        ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ft.Text(desc, size=11, color=C.TEXT_55),
                    ], spacing=2)
                ])
            )
        )

    insights_card = glass(
        expand=True,
        content=ft.Column([
            ft.Text("AI Insights", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
            ft.Container(height=10),
            ft.Column(insight_widgets, spacing=10)
        ])
    )

    # ── Layout ───────────────────────────────────────────────────────────────
    return ft.Container(
        expand=True,
        padding=24,
        content=ft.Column([
            _anim_wrap(page, header, 0.1, dy=-0.02),
            ft.Container(height=20),
            ft.Row([
                _anim_wrap(page, readiness_card, 0.2, dy=0.05),
                _anim_wrap(page, activity_card, 0.3, dy=0.05),
            ], spacing=14),
            ft.Container(height=14),
            ft.Row([
                _anim_wrap(page, skills_card, 0.4, dy=0.05),
                _anim_wrap(page, insights_card, 0.5, dy=0.05),
            ], spacing=14, expand=True),
        ], spacing=0, scroll=ft.ScrollMode.AUTO)
    )
