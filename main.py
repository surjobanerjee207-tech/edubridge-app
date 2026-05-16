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
    page.bgcolor      = "transparent"
    page.padding      = 0
    page.spacing      = 0
    page.window_width      = 1280
    page.window_height     = 850
    page.window_min_width  = 960   # ensures sidebar + content always both visible
    page.window_min_height = 600

    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    }
    page.theme = AppTheme().get_page_theme()
    page.theme.font_family = "Inter"

    # ── tech tomorrow deep gradient ───────────────────────
    page.decoration = ft.BoxDecoration(
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#0a0a1a", "#0d1b2a", "#0a1628"],
            stops=[0.0, 0.5, 1.0]
        ),
        image=ft.DecorationImage(
            src="assets/starry_mountain_bg.png",
            fit=ft.BoxFit.COVER,
            opacity=0.4,
        ),
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

    # Global FilePicker removed in favor of native dialogs
    file_picker = None

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
            9:  lambda: ai_chat_screen(page, file_picker=file_picker),          # Course Library → AI Career Copilot
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
        
        # Update FAB state
        is_copilot = index == 9
        if is_copilot:
            # Mic mode (on AI Copilot page)
            copilot_btn.content = ft.Icon(ft.Icons.MIC_ROUNDED, color="#ffffff", size=24)
            copilot_btn.width = 60
            copilot_btn.border_radius = 30
            copilot_btn.tooltip = "Click to talk"
        else:
            # Default mode (any other page)
            copilot_btn.content = ft.Row([
                ft.Text("✦", color="#ffffff", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("AI Copilot", color="#ffffff", weight=ft.FontWeight.BOLD, size=13),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
            copilot_btn.width = 130
            copilot_btn.border_radius = 25
            copilot_btn.tooltip = "Open AI Copilot"
            
        page.update()

    def on_fab_click(e):
        if current_index[0] == 9:
            # Already on Copilot, trigger the voice recording!
            page.pubsub.send_all("trigger_mic")
        else:
            change_view(9)

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
            ft.Text("✦", color="#ffffff", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("AI Copilot", color="#ffffff", weight=ft.FontWeight.BOLD, size=13),
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        width=130,
        height=50,
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#6366f1", "#a855f7"]
        ),
        border_radius=25,
        alignment=ft.alignment.Alignment(0, 0),
        shadow=ft.BoxShadow(
            blur_radius=20, spread_radius=0,
            color="#806366f1", offset=ft.Offset(0, 8)
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        on_click=on_fab_click,
        on_hover=lambda e: setattr(e.control, 'scale', 1.05 if e.data == "true" else 1.0) or e.control.update(),
    )

    page.add(
        ft.Stack([
            # Glow Orb 1 (Top Left)
            ft.Container(
                width=400, height=400,
                left=-150, top=-150,
                bgcolor="#1E6c63ff", # 12% opacity
                blur=ft.Blur(100, 100),
                border_radius=200,
            ),
            # Glow Orb 2 (Bottom Right)
            ft.Container(
                width=350, height=350,
                right=-100, bottom=-100,
                bgcolor="#198b5cf6", # 10% opacity
                blur=ft.Blur(80, 80),
                border_radius=175,
            ),
            # Main Layout
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
