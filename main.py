import flet as ft
from ui.theme import AppTheme
from ui.sidebar import create_sidebar
from config import Config
from database import init_db

from ui.screens.dashboard      import dashboard_screen
from ui.screens.assessment     import assessment_screen
from ui.screens.roadmap        import roadmap_screen
from ui.screens.resume_lab     import resume_lab_screen
from ui.screens.settings       import settings_screen
from ui.screens.placeholder    import placeholder_screen
from ui.screens.planner_screen   import planner_screen
from ui.screens.wellbeing_screen import wellbeing_screen
from ui.screens.ai_chat_screen   import ai_chat_screen
from ui.screens.analytics        import analytics_screen
from ui.screens.interview_prep   import interview_prep_screen


def main(page: ft.Page):
    init_db()

    page.title        = Config.APP_NAME
    page.theme_mode   = ft.ThemeMode.DARK
    page.bgcolor      = "#05091e"
    page.padding      = 0
    page.spacing      = 0
    page.window_width      = 1280
    page.window_height     = 850
    page.window_min_width  = 960   # ensures sidebar + content always both visible
    page.window_min_height = 600

    page.theme = AppTheme().get_page_theme()

    # ── space background image with dark overlay ──────────────────────────────
    page.decoration = ft.BoxDecoration(
        image=ft.DecorationImage(
            src="assets/bg_space.jpg",
            fit=ft.BoxFit.COVER,
            opacity=0.28,
        ),
        bgcolor="#05091e",
    )

    # ── restore saved theme preference ───────────────────────────────────────
    try:
        from data_service import get_preference
        if get_preference("dark_mode", "true") == "false":
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor    = "#f1f5f9"
    except Exception:
        pass

    current_index = [0]
    sidebar_ref   = ft.Ref[ft.Container]()
    content_ref   = ft.Ref[ft.Container]()

    def get_screen(index):
        mapping = {
            0:  lambda: dashboard_screen(page, navigate_to=change_view),
            1:  lambda: assessment_screen(page),
            2:  lambda: roadmap_screen(page),
            3:  lambda: resume_lab_screen(page),
            4:  lambda: settings_screen(page, refresh_current_screen),
            5:  lambda: analytics_screen(page),
            6:  lambda: placeholder_screen(page, "Job Board",      ft.Icons.WORK_OUTLINE),
            7:  lambda: interview_prep_screen(page),
            8:  lambda: placeholder_screen(page, "Mentorship",     ft.Icons.PEOPLE_OUTLINE),
            9:  lambda: ai_chat_screen(page),          # Course Library → AI Career Copilot
            10: lambda: placeholder_screen(page, "Achievements",   ft.Icons.EMOJI_EVENTS),
            11: lambda: planner_screen(page),           # Schedule → Planner
            12: lambda: wellbeing_screen(page),         # Community → Wellbeing
            13: lambda: placeholder_screen(page, "Notifications",  ft.Icons.NOTIFICATIONS_NONE),
        }
        return mapping.get(index, lambda: dashboard_screen(page))()

    def change_view(index):
        current_index[0] = index
        if sidebar_ref.current:
            sidebar_ref.current.content = create_sidebar(page, index, change_view)
        if content_ref.current:
            content_ref.current.bgcolor = "transparent"
            content_ref.current.content = get_screen(index)
        page.update()

    def refresh_current_screen():
        change_view(current_index[0])

    sidebar_host = ft.Container(
        ref=sidebar_ref,
        content=create_sidebar(page, 0, change_view),
        width=240,          # pin sidebar to exact fixed width so it never expands
    )

    content_area = ft.Container(
        ref=content_ref,
        expand=True,
        bgcolor="transparent",
        content=get_screen(0),
    )

    # ── Shell with Floating AI Button ────────────────────────────────────────

    copilot_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color="#ffffff", size=20),
            ft.Text("AI Copilot", color="#ffffff", weight=ft.FontWeight.BOLD, size=13),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        width=140,
        height=50,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#6366f1", "#a855f7"]
        ),
        border_radius=25,
        shadow=ft.BoxShadow(
            blur_radius=20, spread_radius=0,
            color="#806366f1", offset=ft.Offset(0, 8)
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        on_click=lambda e: change_view(9), # Index 9 is AI Copilot
        on_hover=lambda e: setattr(e.control, 'scale', 1.05 if e.data == "true" else 1.0) or e.control.update(),
    )

    page.add(
        ft.Stack([
            ft.Row([
                sidebar_host,
                ft.VerticalDivider(width=1, color="#1e293b"),
                content_area,
            ], expand=True, spacing=0, tight=True),
            # Floating Button Position
            ft.Container(
                content=copilot_btn,
                bottom=30,
                right=30,
            )
        ], expand=True)
    )

    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
