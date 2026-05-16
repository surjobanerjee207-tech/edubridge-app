import flet as ft
from ui.theme import GlassColors
from utils.history_manager import load_search_history

C = GlassColors()
SIDEBAR_SOLID = "#0d1b3e"    # deep navy — no alpha ambiguity

NAV_SECTIONS = [
    ("MAIN", [
        ("Dashboard",  0, None),
        ("Analytics",  5, None),
        ("Assessment", 1, None),
        ("Roadmap",    2, None),
    ]),
    ("CAREER TOOLS", [
        ("Job Board",      6, 12),
        ("Resume Lab",     3, None),
        ("Interview Prep", 7, None),
        ("Mentorship",     8, None),
    ]),
    ("LEARN", [
        ("AI Career Copilot", 9,  "FOCUS"),
        ("Achievements",   10, 3),
        ("Schedule",       11, None),
        ("Community",      12, None),
    ]),
]

BOTTOM_NAV = [
    ("Notifications", 13, 5),
    ("Settings",       4, None),
]


def create_sidebar(page: ft.Page, active_index: int, navigate_to):

    def section_label(text):
        return ft.Container(
            content=ft.Text(
                text.upper(), size=10, color="#59ffffff",
                weight=ft.FontWeight.W_600,
            ),
            padding=ft.Padding.only(left=14, top=20, bottom=6),
        )

    def nav_item(label, index, badge=None):
        is_active  = active_index == index
        is_focus   = badge == "FOCUS"
        
        # Base colors
        bg         = "#1Affffff" if is_active else "transparent"
        text_color = "#ffffff" if is_active else C.TEXT_55
        
        # Override for high-focus AI button
        if is_focus:
            bg = ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),
                end=ft.alignment.Alignment(1, 1),
                colors=["#6366f1", "#a855f7"],
            )
            text_color = "#ffffff"
        
        border_l = ft.Border(
            left=ft.BorderSide(3, "#6c63ff" if is_active and not is_focus else "transparent"),
        )

        badge_widget = ft.Container(
            content=ft.Text("NEW", size=8, color="#ffffff", weight=ft.FontWeight.BOLD),
            bgcolor="#ffffff33",
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=6, vertical=1),
        ) if is_focus else (
            ft.Container(
                content=ft.Text(str(badge), size=9, color="#ffffff", weight=ft.FontWeight.BOLD),
                bgcolor="#ef4444",
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            ) if badge is not None else ft.Container(width=0)
        )

        icon_widget = ft.Icon(ft.Icons.AUTO_AWESOME, size=14, color="#ffffff") if is_focus else ft.Container(width=0)

        def _on_hover(e, container, base_bg, focus):
            if focus:
                return  # active focus item keeps its gradient
            hovering = e.data == "true"
            container.offset = ft.Offset(-0.02 if not hovering else 0, 0) if not hovering else ft.Offset(0.02, 0)
            container.bgcolor = "#0Dffffff" if hovering else base_bg
            container.update()

        item = ft.Container(
            content=ft.Row([
                ft.Container(width=4),
                icon_widget if is_focus else ft.Container(width=0),
                ft.Text(label, size=13, color=text_color,
                        weight=ft.FontWeight.BOLD if is_focus or is_active else ft.FontWeight.NORMAL,
                        expand=True),
                badge_widget,
            ], alignment=ft.MainAxisAlignment.START, spacing=8 if is_focus else 0),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10 if is_focus else 9),
            border_radius=10 if is_focus else 8,
            gradient=bg if is_focus else None,
            bgcolor=bg if not is_focus else None,
            border=border_l,
            shadow=ft.BoxShadow(blur_radius=15, color="#606366f1", spread_radius=1) if is_focus else None,
            animate_offset=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0),
            on_click=lambda e, i=index: navigate_to(i),
        )
        if not is_active and not is_focus:
            item.on_hover = lambda e, c=item, b=bg, f=is_focus: _on_hover(e, c, b, f)
        return item


    nav_items = []
    for section_name, items in NAV_SECTIONS:
        nav_items.append(section_label(section_name))
        for label, index, badge in items:
            nav_items.append(nav_item(label, index, badge))

    # ── Search History Section ───────────────────────────────────────────────
    history = load_search_history(page)
    if history:
        nav_items.append(section_label("SEARCH HISTORY"))
        for h in history[:8]: # Last 8 searches
            query = h["q"]
            history_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.HISTORY, size=14, color=C.TEXT_55),
                    ft.Text(query if len(query) < 22 else query[:20]+"...", 
                            size=12, color=C.TEXT_55, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                border_radius=8,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                on_hover=lambda e: (
                    setattr(e.control, 'bgcolor', "#1a1a1a" if e.data == "true" else "transparent"),
                    setattr(e.control, 'scale', 1.05 if e.data == "true" else 1.0),
                    e.control.update()
                ),
                on_click=lambda e, q=query: (
                    navigate_to(9), # Switch to AI Chat
                    page.pubsub.send_all({"type": "history_search", "query": q}) # Trigger search
                ),
            )
            nav_items.append(history_btn)

    bottom_items = [nav_item(label, index, badge) for label, index, badge in BOTTOM_NAV]

    return ft.Container(
        width=240,
        bgcolor="#0Affffff", # rgba(255,255,255,0.04)
        blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
        border=ft.Border(right=ft.BorderSide(1, "#12ffffff")), # rgba(255,255,255,0.07)
        content=ft.Column([
            # ── Logo ─────────────────────────────────────────────────────────
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.SCHOOL, size=18, color="#ffffff"),
                        width=34, height=34, border_radius=8,
                        bgcolor="#6366f1",
                        alignment=ft.alignment.Alignment(0, 0),
                        shadow=ft.BoxShadow(blur_radius=12, color="#806366f1"),
                    ),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Text("CareerPath", size=15, weight=ft.FontWeight.BOLD,
                                color=C.TEXT_WHITE),
                        ft.Text("AI", size=11, color=C.TEXT_55),
                    ], spacing=0),
                ]),
                padding=ft.Padding.symmetric(horizontal=16, vertical=18),
            ),
            ft.Container(height=1, bgcolor="#1affffff"),
            # ── Nav ──────────────────────────────────────────────────────────
            ft.Container(
                expand=True,
                content=ft.Column(nav_items, spacing=1, scroll=ft.ScrollMode.AUTO),
                padding=ft.Padding.symmetric(horizontal=8),
            ),
            ft.Container(height=1, bgcolor="#1affffff"),
            # ── Bottom ───────────────────────────────────────────────────────
            ft.Container(
                content=ft.Column(bottom_items, spacing=1),
                padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            ),
        ], spacing=0),
    )
