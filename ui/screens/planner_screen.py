import flet as ft
import threading
from ui.theme import get_colors
from database import get_connection
from ai_engine.planner import StudyPlanner


def planner_screen(page: ft.Page):
    colors = get_colors(page)
    planner = StudyPlanner()

    task_input = ft.TextField(
        hint_text="New task title…", expand=True,
        bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY),
    )
    date_input = ft.TextField(
        hint_text="Due date (YYYY-MM-DD)", width=180,
        bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY),
    )
    priority_dd = ft.Dropdown(
        hint_text="Priority", width=120,
        options=[ft.dropdown.Option("High"), ft.dropdown.Option("Medium"),
                 ft.dropdown.Option("Low")],
        bgcolor=colors.BACKGROUND, border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
    )
    task_list   = ft.Ref[ft.Column]()
    ai_area     = ft.Ref[ft.Column]()

    def load_tasks():
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, title, due_date, priority FROM tasks WHERE status='pending' ORDER BY due_date ASC"
        ).fetchall()
        conn.close()
        return rows

    def _task_tile(row):
        tid, title, due, pri = row
        pri_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}.get(pri, colors.TEXT_SECONDARY)
        return ft.Container(
            bgcolor=colors.SURFACE,
            border_radius=10,
            border=ft.Border.all(1, colors.BORDER),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            content=ft.Row([
                ft.Column([
                    ft.Text(title, size=14, color=colors.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_500),
                    ft.Text(f"Due: {due or '—'} · {pri or '—'}",
                            size=12, color=pri_color),
                ], spacing=3, expand=True),
                ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color="#10b981",
                              icon_size=20, tooltip="Mark complete",
                              on_click=lambda e, t=tid: complete_task(t)),
            ]),
        )

    def refresh_tasks():
        rows = load_tasks()
        task_list.current.controls = (
            [_task_tile(r) for r in rows]
            if rows else [ft.Text("No pending tasks!", size=13, color=colors.TEXT_SECONDARY)]
        )
        task_list.current.update()

    def add_task(e):
        if not task_input.value.strip(): return
        conn = get_connection()
        conn.execute("INSERT INTO tasks (title, due_date, priority) VALUES (?,?,?)",
                     (task_input.value.strip(), date_input.value.strip() or None,
                      priority_dd.value or "Medium"))
        conn.commit()
        conn.close()
        task_input.value = ""
        date_input.value = ""
        refresh_tasks()

    def complete_task(tid):
        conn = get_connection()
        conn.execute("UPDATE tasks SET status='completed' WHERE id=?", (tid,))
        conn.commit()
        conn.close()
        refresh_tasks()

    def generate_ai_plan(e):
        rows = load_tasks()
        if not rows:
            page.snack_bar = ft.SnackBar(ft.Text("Add some tasks first!"))
            page.snack_bar.open = True
            page.update()
            return
        tasks = [{"title": r[1], "due_date": r[2], "priority": r[3]} for r in rows]
        ai_area.current.controls = [
            ft.Row([ft.ProgressRing(width=20, height=20, stroke_width=2,
                                    color=colors.PRIMARY),
                    ft.Container(width=10),
                    ft.Text("Generating AI schedule…", size=13,
                            color=colors.TEXT_SECONDARY)])
        ]
        ai_area.current.update()

        def _run():
            plan = planner.generate_schedule(tasks)
            ai_area.current.controls = [
                ft.Markdown(plan, selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED)
            ]
            ai_area.current.update()

        threading.Thread(target=_run, daemon=True).start()

    initial_rows = load_tasks()
    initial_tiles = (
        [_task_tile(r) for r in initial_rows]
        if initial_rows else [ft.Text("No pending tasks!", size=13, color=colors.TEXT_SECONDARY)]
    )

    return ft.Container(
        expand=True, bgcolor=colors.BACKGROUND,
        padding=ft.Padding.all(28),
        content=ft.Column([
            ft.Text("Study Planner", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_PRIMARY),
            ft.Text("Manage your tasks and get an AI-generated study schedule.",
                    size=15, color=colors.TEXT_SECONDARY),
            ft.Container(height=24),

            # Add task row
            ft.Container(
                bgcolor=colors.SURFACE, border_radius=12,
                border=ft.Border.all(1, colors.BORDER), padding=16,
                content=ft.Row([
                    task_input, date_input, priority_dd,
                    ft.ElevatedButton("Add", bgcolor=colors.PRIMARY, color="#ffffff",
                                      on_click=add_task,
                                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                ], spacing=12),
            ),
            ft.Container(height=16),

            ft.ElevatedButton("✨ Generate AI Schedule", bgcolor="#6366f1", color="#ffffff",
                              on_click=generate_ai_plan,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
            ft.Container(height=20),

            ft.Row([
                ft.Column([
                    ft.Text("My Tasks", size=16, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Container(height=10),
                    ft.Column(ref=task_list, controls=initial_tiles, spacing=8),
                ], expand=1),
                ft.VerticalDivider(width=1, color=colors.BORDER),
                ft.Column([
                    ft.Text("AI Recommendation", size=16, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Container(height=10),
                    ft.Column(ref=ai_area, controls=[
                        ft.Text("Click 'Generate AI Schedule' to get started.",
                                size=13, color=colors.TEXT_SECONDARY)
                    ], spacing=0),
                ], expand=1),
            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START, spacing=20),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )
