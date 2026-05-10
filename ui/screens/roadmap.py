import flet as ft
from ui.theme import get_colors
from database import get_connection
from datetime import date


def roadmap_screen(page: ft.Page):
    colors = get_colors(page)

    def load_milestones():
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, title, due_date, status FROM milestones ORDER BY due_date ASC"
        ).fetchall()
        conn.close()
        return rows

    def complete_milestone(mid, card_col):
        conn = get_connection()
        conn.execute("UPDATE milestones SET status='completed' WHERE id=?", (mid,))
        conn.commit()
        conn.close()
        refresh()

    milestone_list = ft.Ref[ft.Column]()
    new_title = ft.TextField(hint_text="New milestone title…", expand=True,
                              bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
                              color=colors.TEXT_PRIMARY,
                              hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY))
    new_date  = ft.TextField(hint_text="Due date (YYYY-MM-DD)", width=180,
                              bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
                              color=colors.TEXT_PRIMARY,
                              hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY))

    def add_milestone(e):
        if not new_title.value.strip():
            return
        conn = get_connection()
        conn.execute("INSERT INTO milestones (title, due_date, status) VALUES (?,?,?)",
                     (new_title.value.strip(), new_date.value.strip() or None, 'pending'))
        conn.commit()
        conn.close()
        new_title.value = ""
        new_date.value  = ""
        refresh()

    def _milestone_card(row):
        mid, title, due, status = row
        today     = date.today()
        done      = status == 'completed'
        try:
            due_d = date.fromisoformat(due) if due else None
            overdue = due_d and due_d < today and not done
            days_str = f"{(due_d - today).days}d away" if due_d and not done else ""
            if due_d and not done and due_d < today:
                days_str = f"Overdue by {(today - due_d).days}d"
        except Exception:
            overdue  = False
            days_str = due or ""

        dot_color  = "#10b981" if done else ("#ef4444" if overdue else colors.PRIMARY)
        card_bg    = "#10b98110" if done else colors.SURFACE

        return ft.Container(
            bgcolor=card_bg,
            border_radius=12,
            border=ft.Border.all(1, "#10b98150" if done else colors.BORDER),
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            content=ft.Row([
                ft.Container(width=12, height=12, border_radius=6, bgcolor=dot_color),
                ft.Container(width=14),
                ft.Column([
                    ft.Text(title, size=15, color=colors.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600 if not done else ft.FontWeight.NORMAL,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if done else None)),
                    ft.Text(days_str, size=12,
                            color="#ef4444" if overdue else colors.TEXT_SECONDARY),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Text("✓ Done", size=12, color="#10b981") if done else
                            ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE,
                                          icon_color=colors.PRIMARY, icon_size=20,
                                          tooltip="Mark complete",
                                          on_click=lambda e, m=mid: complete_milestone(m, None)),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def refresh():
        rows = load_milestones()
        pending   = [r for r in rows if r[3] == 'pending']
        completed = [r for r in rows if r[3] == 'completed']

        milestone_list.current.controls = []
        if pending:
            milestone_list.current.controls.append(
                ft.Text("Upcoming", size=13, color=colors.TEXT_SECONDARY,
                        weight=ft.FontWeight.W_600))
            for r in pending:
                milestone_list.current.controls.append(_milestone_card(r))
        if completed:
            milestone_list.current.controls.append(ft.Container(height=12))
            milestone_list.current.controls.append(
                ft.Text("Completed", size=13, color="#10b981", weight=ft.FontWeight.W_600))
            for r in completed:
                milestone_list.current.controls.append(_milestone_card(r))
        if not rows:
            milestone_list.current.controls.append(
                ft.Text("No milestones yet. Add one below!", size=14,
                        color=colors.TEXT_SECONDARY))
        milestone_list.current.update()

    rows = load_milestones()
    pending   = [r for r in rows if r[3] == 'pending']
    completed = [r for r in rows if r[3] == 'completed']

    initial_controls = []
    if pending:
        initial_controls.append(ft.Text("Upcoming", size=13, color=colors.TEXT_SECONDARY,
                                         weight=ft.FontWeight.W_600))
        initial_controls += [_milestone_card(r) for r in pending]
    if completed:
        initial_controls.append(ft.Container(height=12))
        initial_controls.append(ft.Text("Completed", size=13, color="#10b981",
                                          weight=ft.FontWeight.W_600))
        initial_controls += [_milestone_card(r) for r in completed]
    if not rows:
        initial_controls.append(ft.Text("No milestones yet. Add one below!",
                                         size=14, color=colors.TEXT_SECONDARY))

    return ft.Container(
        expand=True, bgcolor=colors.BACKGROUND,
        padding=ft.Padding.all(28),
        content=ft.Column([
            ft.Text("Career Roadmap", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_PRIMARY),
            ft.Text("Track your career milestones and goals", size=15,
                    color=colors.TEXT_SECONDARY),
            ft.Container(height=24),
            ft.Column(ref=milestone_list, controls=initial_controls, spacing=10),
            ft.Container(height=24),
            ft.Container(
                bgcolor=colors.SURFACE, border_radius=12,
                border=ft.Border.all(1, colors.BORDER), padding=20,
                content=ft.Column([
                    ft.Text("Add Milestone", size=15, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Container(height=10),
                    ft.Row([new_title, new_date,
                            ft.ElevatedButton("Add", bgcolor=colors.PRIMARY, color="#ffffff",
                                              on_click=add_milestone,
                                              style=ft.ButtonStyle(
                                                  shape=ft.RoundedRectangleBorder(radius=8)))],
                           spacing=12),
                ], spacing=6),
            ),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )
