import flet as ft
import threading
from ui.theme import GlassColors
from database import get_dashboard_data

C = GlassColors()

# Per-skill accent colors
SKILL_ACCENTS = {
    "Python":     "#6366f1",
    "SQL":        "#14b8a6",
    "Data Viz":   "#f59e0b",
    "ML Basics":  "#22c55e",
    "Statistics": "#8b5cf6",
}
SKILL_FALLBACK = ["#6366f1", "#14b8a6", "#f59e0b", "#22c55e", "#8b5cf6", "#ec4899"]

DOT_COLORS = {
    "article":   "#22c55e",
    "learning":  "#6366f1",
    "practice":  "#f59e0b",
    "course":    "#8b5cf6",
}

# ── glass helpers ─────────────────────────────────────────────────────────────

def glass(content, padding=20, expand=False, height=None, strong=False, radius=16):
    bg     = C.GLASS_MED   if strong else C.GLASS_WEAK
    border = C.BORDER_MED  if strong else C.BORDER_WEAK
    return ft.Container(
        content=content,
        bgcolor=bg,
        border_radius=radius,
        border=ft.Border.all(1, border),
        shadow=ft.BoxShadow(blur_radius=32, spread_radius=0, color=C.SHADOW),
        padding=padding,
        expand=expand,
        height=height,
    )


def _anim_wrap(page, content, delay: float, dy: float = 0.05):
    c = ft.Container(
        content=content,
        opacity=0,
        offset=ft.Offset(0, dy),
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
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


# ── stat card ─────────────────────────────────────────────────────────────────

def _stat_card(accent, value, label, sub, sub_color):
    return ft.Container(
        expand=True,
        content=ft.Column([
            # coloured top accent bar
            ft.Container(height=3, bgcolor=accent,
                         border_radius=ft.BorderRadius.only(top_left=16, top_right=16)),
            ft.Container(
                content=ft.Column([
                    ft.Text(value, size=30, weight=ft.FontWeight.W_700,
                            color=C.TEXT_WHITE),
                    ft.Text(label.upper(), size=10, color=C.TEXT_45,
                            weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    ft.Text(sub, size=12, color=sub_color,
                            weight=ft.FontWeight.W_500),
                ], spacing=3),
                padding=ft.Padding.only(left=18, right=18, top=14, bottom=16),
            ),
        ], spacing=0),
        bgcolor=C.GLASS_WEAK,
        border_radius=16,
        border=ft.Border.all(1, C.BORDER_WEAK),
        shadow=ft.BoxShadow(blur_radius=24, spread_radius=0, color=C.SHADOW),
    )


# ── custom bar chart ──────────────────────────────────────────────────────────

def _weekly_chart(weekly_data, w_badge, w_color, w_bg):
    if not weekly_data:
        return ft.Text("No data yet.", color=C.TEXT_55, size=12)

    max_val  = max(h for _, h in weekly_data) or 1
    MAX_H    = 110

    bars = []
    for i, (day, val) in enumerate(weekly_data):
        is_today = (i == len(weekly_data) - 1)
        bar_h    = max(4, int((val / max_val) * MAX_H))
        bar_col  = "#d96366f1" if is_today else "#26ffffff"
        bars.append(
            ft.Column([
                ft.Text(f"{val:.1f}", size=9, color=C.TEXT_30,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(
                    width=26, height=bar_h,
                    bgcolor=bar_col,
                    border_radius=ft.BorderRadius.only(top_left=4, top_right=4),
                ),
                ft.Text(day[:3], size=10, color=C.TEXT_45,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.END, spacing=4)
        )

    return glass(
        expand=True, height=220, padding=20,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Weekly Learning Activity", size=14,
                            weight=ft.FontWeight.W_600, color=C.TEXT_WHITE),
                    ft.Text("Hours this week", size=11, color=C.TEXT_55),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Text(w_badge, size=11, color=w_color,
                                    weight=ft.FontWeight.W_600),
                    bgcolor=w_bg, border_radius=20,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                ),
            ]),
            ft.Container(height=12),
            ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.END,
                   expand=True),
        ], spacing=0),
    )


def _trend_chart(trend_data):
    if not trend_data:
        return ft.Text("No trend data.", color=C.TEXT_55, size=12)

    MAX_H = 90
    bars  = []
    for i, (month, val) in enumerate(trend_data):
        is_last = (i == len(trend_data) - 1)
        bar_h   = max(4, int((val / 100) * MAX_H))
        bar_col = "#d96366f1" if is_last else "#406366f1"
        bars.append(
            ft.Column([
                ft.Text(f"{val}%", size=9, color=C.TEXT_30,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(
                    width=30, height=bar_h, bgcolor=bar_col,
                    border_radius=ft.BorderRadius.only(top_left=4, top_right=4),
                ),
                ft.Text(month, size=10, color=C.TEXT_45,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.END, spacing=4)
        )

    return glass(
        expand=True, height=220, padding=20,
        content=ft.Column([
            ft.Text("Career Match Trend", size=14, weight=ft.FontWeight.W_600,
                    color=C.TEXT_WHITE),
            ft.Text("Last 6 months", size=11, color=C.TEXT_55),
            ft.Container(height=14),
            ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.END,
                   expand=True),
        ], spacing=0),
    )


# ── skill bar ─────────────────────────────────────────────────────────────────

def _skill_bar(name, pct, accent):
    return ft.Column([
        ft.Row([
            ft.Text(name, size=13, color=C.TEXT_WHITE, expand=True),
            ft.Text(f"{pct}%", size=13, color=C.TEXT_55),
        ]),
        ft.ProgressBar(
            value=pct / 100, color=accent,
            bgcolor="#14ffffff", height=6, border_radius=99,
        ),
    ], spacing=6)


# ── activity dot ──────────────────────────────────────────────────────────────

def _activity_row(desc, rel, dot_color):
    return ft.Row([
        ft.Container(width=8, height=8, border_radius=4, bgcolor=dot_color),
        ft.Container(width=10),
        ft.Column([
            ft.Text(desc, size=13, color=C.TEXT_WHITE),
            ft.Text(rel,  size=11, color=C.TEXT_45),
        ], spacing=2),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)


# ── main screen ───────────────────────────────────────────────────────────────

def dashboard_screen(page: ft.Page, navigate_to=None):

    # ── live data with error boundary ─────────────────────────────────────────
    try:
        d = get_dashboard_data()
        if not d:
            raise ValueError("No data returned")
    except Exception as e:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.colors.RED, size=50),
                ft.Text("Dashboard failed to load", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(str(e), size=12, color=ft.colors.RED_300)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
    career_match    = d["career_match"]
    match_change    = d["match_change"]
    skills_done     = d["skills_done"]
    skills_total    = d["skills_total"]
    milestone_title = d["milestone_title"]
    days_left       = d["days_left"]
    streak          = d["streak"]
    weekly_data     = d["weekly_data"]
    trend_data      = d["trend_data"]
    skill_rows      = d["skill_rows"]
    activities      = d["activities"]

    # ── derived strings ───────────────────────────────────────────────────────
    match_sub   = (f"↑ {match_change}% this week" if match_change > 0
                   else f"↓ {abs(match_change)}% this week" if match_change < 0
                   else "Stable this week")
    match_col   = "#4ade80" if match_change >= 0 else "#f87171"

    skills_pct  = f"{int(skills_done/skills_total*100)}% complete" if skills_total else "—"
    ms_sub      = f"{milestone_title[:18]}…" if len(milestone_title) > 18 else milestone_title
    streak_sub  = "🔥 Personal best!" if streak >= 7 else f"{streak}-day run"

    if len(weekly_data) >= 2:
        this_w  = sum(h for _, h in weekly_data[-5:])
        last_w  = sum(h for _, h in weekly_data[:5]) or 1
        w_delta = int((this_w - last_w) / last_w * 100)
        w_badge = f"+{w_delta}% vs last week" if w_delta >= 0 else f"{w_delta}% vs last week"
        w_color = "#4ade80" if w_delta >= 0 else "#f87171"
        w_bg    = "#1a4ade80" if w_delta >= 0 else "#1af87171"
    else:
        w_badge, w_color, w_bg = "New", C.TEXT_55, "#1affffff"

    # ── search dialog ─────────────────────────────────────────────────────────
    NAV_ITEMS = [
        ("Dashboard",      0), ("Analytics",   5), ("Assessment",    1),
        ("Roadmap",        2), ("Job Board",   6), ("Resume Lab",    3),
        ("Interview Prep", 7), ("Mentorship",  8), ("Course Library",9),
        ("Achievements",  10), ("Schedule",   11), ("Community",    12),
        ("Settings",       4),
    ]

    search_results_col = ft.Ref[ft.Column]()
    search_field = ft.TextField(
        hint_text="Search screens, skills, milestones…",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor="#1a1f3a",
        border_color="#1fffffff",
        focused_border_color="#6366f1",
        color="#ffffff",
        hint_style=ft.TextStyle(color="#4dffffff"),
        border_radius=8,
        height=44,
        autofocus=True,
        text_size=13,
    )

    def _result_tile(icon, title, subtitle, on_tap):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=16, color="#6366f1"),
                    width=32, height=32, border_radius=8,
                    bgcolor="#1fffffff",
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(width=12),
                ft.Column([
                    ft.Text(title, size=13, color="#ffffff",
                            weight=ft.FontWeight.W_500),
                    ft.Text(subtitle, size=11, color="#4dffffff"),
                ], spacing=1, expand=True),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            on_click=on_tap,
            on_hover=lambda e: setattr(e.control, 'bgcolor',
                "#1fffffff" if e.data == "true" else "transparent") or e.control.update(),
        )

    def do_search(e):
        q = (search_field.value or "").strip().lower()
        if not q:
            search_results_col.current.controls = []
            search_results_col.current.update()
            return

        tiles = []

        # nav item matches
        for label, idx in NAV_ITEMS:
            if q in label.lower():
                def _nav(e, i=idx):
                    close_search(None)
                    if navigate_to:
                        navigate_to(i)
                tiles.append(_result_tile(
                    ft.Icons.NAVIGATION, label, "Go to screen", _nav))

        # skill matches
        from database import get_connection
        conn = get_connection()
        skills = conn.execute(
            "SELECT skill_name, proficiency FROM user_skills WHERE LOWER(skill_name) LIKE ?",
            (f"%{q}%",)
        ).fetchall()
        for name, pct in skills:
            tiles.append(_result_tile(
                ft.Icons.PSYCHOLOGY, name, f"Skill · {pct}% proficiency",
                lambda e, n=name, p=pct: None))

        # milestone matches
        milestones = conn.execute(
            "SELECT title, status FROM milestones WHERE LOWER(title) LIKE ?",
            (f"%{q}%",)
        ).fetchall()
        for title, status in milestones:
            def _ms_nav(e):
                close_search(None)
                if navigate_to:
                    navigate_to(2)
            tiles.append(_result_tile(
                ft.Icons.FLAG, title, f"Milestone · {status.title()}", _ms_nav))
        conn.close()

        if not tiles:
            tiles = [ft.Container(
                content=ft.Text(f'No results for "{search_field.value}"',
                                size=13, color="#4dffffff"),
                padding=16,
            )]

        search_results_col.current.controls = tiles
        search_results_col.current.update()

    search_field.on_change = do_search

    search_dlg = ft.AlertDialog(
        bgcolor="#0d1b3e",
        shape=ft.RoundedRectangleBorder(radius=14),
        content=ft.Container(
            width=520,
            content=ft.Column([
                search_field,
                ft.Container(height=8),
                ft.Column(ref=search_results_col, controls=[], spacing=4,
                          scroll=ft.ScrollMode.AUTO, height=280),
            ], spacing=0, tight=True),
            padding=ft.Padding.all(4),
        ),
    )

    def open_search(e):
        page.dialog = search_dlg
        page.dialog.open = True
        page.update()

    def close_search(e):
        page.dialog.open = False
        search_field.value = ""
        search_results_col.current.controls = []
        page.update()

    search_dlg.on_dismiss = close_search

    # ── top bar ───────────────────────────────────────────────────────────────
    top_bar = ft.Row([
        ft.Column([
            ft.Text("Welcome back, Student 👋", size=22,
                    weight=ft.FontWeight.W_700, color=C.TEXT_WHITE),
            ft.Text("Let's build your dream career path.",
                    size=13, color=C.TEXT_55),
        ], spacing=4, expand=True),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, size=15, color=C.TEXT_45),
                ft.Text("Search anything…", size=13, color=C.TEXT_45),
            ], spacing=8),
            bgcolor=C.GLASS_WEAK,
            border=ft.Border.all(1, C.BORDER_WEAK),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_click=open_search,
        ),
        ft.Container(width=12),
        ft.Container(
            content=ft.Text("ST", size=13, weight=ft.FontWeight.BOLD,
                            color="#ffffff"),
            width=36, height=36, border_radius=18,
            bgcolor="#6366f1",
            alignment=ft.alignment.Alignment(0, 0),
            shadow=ft.BoxShadow(blur_radius=12, color="#806366f1"),
        ),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ── stat cards ────────────────────────────────────────────────────────────

    stat_row = ft.Row(spacing=14, controls=[
        _stat_card("#6366f1", f"{career_match}%", "Career Match",    match_sub,  match_col),
        _stat_card("#14b8a6", f"{skills_done}/{skills_total}", "Skills Assessed", skills_pct, "#2dd4bf"),
        _stat_card("#f59e0b", f"{days_left}d",  "Next Milestone",   ms_sub,     "#fbbf24"),
        _stat_card("#8b5cf6", str(streak),      "Day Streak",       streak_sub, "#a78bfa"),
    ])

    # ── charts ────────────────────────────────────────────────────────────────
    charts_row = ft.Row(spacing=14, expand=True, controls=[
        _weekly_chart(weekly_data, w_badge, w_color, w_bg),
        _trend_chart(trend_data),
    ])

    # ── skill proficiency ─────────────────────────────────────────────────────
    skill_animation_data = []
    skill_bar_widgets = []
    for i, (name, pct) in enumerate(skill_rows):
        accent = SKILL_ACCENTS.get(name, SKILL_FALLBACK[i % len(SKILL_FALLBACK)])
        bar = ft.ProgressBar(
            value=0, color=accent,
            bgcolor="#14ffffff", height=6, border_radius=99,
        )
        pct_text = ft.Text("0%", size=13, color=C.TEXT_55)

        skill_animation_data.append((bar, pct_text, pct))

        skill_bar_widgets.append(ft.Column([
            ft.Row([
                ft.Text(name, size=13, color=C.TEXT_WHITE, expand=True),
                pct_text,
            ]),
            bar,
        ], spacing=6))

    if not skill_bar_widgets:
        skill_bar_widgets = [
            ft.Text("No skills yet.", size=13, color=C.TEXT_55),
            ft.Text("Go to Assessment → add your skills.", size=12, color=C.TEXT_45),
        ]

    skill_card = glass(expand=True, padding=22, content=ft.Column(
        [ft.Text("Skill Proficiency", size=14, weight=ft.FontWeight.W_600,
                 color=C.TEXT_WHITE),
         ft.Container(height=14)] + skill_bar_widgets,
        spacing=14
    ))

    def _animate_bars():
        try:
            import time
            start_time = time.time()
            duration = 0.8  # 800ms fill per bar
            stagger = 0.15  # 150ms stagger between bars
            fps = 60
            frame_time = 1 / fps

            total_needed = duration + (len(skill_animation_data) - 1) * stagger

            while True:
                elapsed = time.time() - start_time
                if elapsed > total_needed + 0.1:
                    # Final cleanup to ensure exact targets
                    for bar, pct_text, target in skill_animation_data:
                        bar.value = target / 100
                        pct_text.value = f"{int(target)}%"
                    page.update()
                    break

                for i, (bar, pct_text, target) in enumerate(skill_animation_data):
                    delay = i * stagger
                    if elapsed < delay:
                        continue

                    bar_elapsed = elapsed - delay
                    if bar_elapsed > duration:
                        bar.value = target / 100
                        pct_text.value = f"{int(target)}%"
                        continue

                    # Animation with cubic ease-out
                    p = bar_elapsed / duration
                    eased = 1 - (1 - p) ** 3
                    bar.value = (target / 100) * eased
                    pct_text.value = f"{int(target * eased)}%"

                page.update()
                time.sleep(frame_time)
        except Exception:
            pass

    if skill_animation_data:
        # Wait for the entrance animation to settle
        threading.Timer(1.0, _animate_bars).start()

    # ── recent activity ───────────────────────────────────────────────────────
    act_type_colors = ["#22c55e", "#6366f1", "#f59e0b", "#8b5cf6", "#14b8a6"]
    act_rows = []
    for i, (desc, rel) in enumerate(activities):
        act_rows.append(_activity_row(desc, rel, act_type_colors[i % len(act_type_colors)]))
        if i < len(activities) - 1:
            act_rows.append(ft.Container(height=1, bgcolor="#0dffffff",
                                          margin=ft.Margin(left=18, right=0, top=8, bottom=8)))

    if not act_rows:
        act_rows = [ft.Text("No activity yet.", size=13, color=C.TEXT_55)]

    activity_card = glass(expand=True, padding=22, content=ft.Column(
        [ft.Text("Recent Activity", size=14, weight=ft.FontWeight.W_600,
                 color=C.TEXT_WHITE),
         ft.Container(height=14)] + act_rows,
        spacing=0
    ))

    bottom_row = ft.Row(spacing=14, controls=[skill_card, activity_card])

    # ── assemble with staggered animations ────────────────────────────────────
    return ft.Container(
        expand=True,
        bgcolor="transparent",
        padding=ft.Padding.all(24),
        content=ft.Column([
            _anim_wrap(page, top_bar,    0.05, dy=-0.04),
            ft.Container(height=22),
            _anim_wrap(page, stat_row,   0.10, dy=0.05),
            ft.Container(height=14),
            _anim_wrap(page, charts_row, 0.15, dy=0.05),
            ft.Container(height=14),
            _anim_wrap(page, bottom_row, 0.20, dy=0.05),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
    )
