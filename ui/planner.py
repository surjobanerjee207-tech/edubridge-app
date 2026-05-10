import flet as ft
from database import get_connection
from ai_engine.planner import StudyPlanner

class PlannerScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.planner = StudyPlanner()
        self.expand = True
        
        self.task_input = ft.TextField(label="New Task", expand=True)
        self.date_input = ft.TextField(label="Due Date (YYYY-MM-DD)", width=150)
        self.priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            width=120
        )
        
        self.task_list_view = ft.ListView(expand=True, spacing=10)
        self.ai_plan_area = ft.Column(visible=False)
        
        self.build_ui()
        self.load_tasks()

    def build_ui(self):
        self.controls = [
            ft.Text("Study Planner", size=28, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                self.task_input,
                self.date_input,
                self.priority_dropdown,
                ft.IconButton(ft.icons.ADD, on_click=self.add_task),
            ]),
            
            ft.ElevatedButton("Generate AI Study Schedule", icon=ft.icons.AUTO_AWESOME, on_click=self.generate_ai_plan),
            
            ft.Divider(),
            
            ft.Row([
                ft.Column([ft.Text("My Tasks", size=20), self.task_list_view], expand=1),
                ft.VerticalDivider(),
                ft.Column([ft.Text("AI Recommendation", size=20), self.ai_plan_area], expand=1),
            ], expand=True)
        ]

    def add_task(self, e):
        if not self.task_input.value: return
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)", 
                       (self.task_input.value, self.date_input.value, self.priority_dropdown.value))
        conn.commit()
        conn.close()
        
        self.task_input.value = ""
        self.load_tasks()
        self.page.update()

    def load_tasks(self):
        self.task_list_view.controls.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, due_date, priority FROM tasks WHERE status='pending' ORDER BY due_date ASC")
        for row in cursor.fetchall():
            self.task_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(row[1]),
                    subtitle=ft.Text(f"Due: {row[2]} | {row[3]} Priority"),
                    trailing=ft.IconButton(ft.icons.CHECK, on_click=lambda _, tid=row[0]: self.complete_task(tid))
                )
            )
        conn.close()

    def complete_task(self, task_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status='completed' WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        self.load_tasks()
        self.page.update()

    def generate_ai_plan(self, e):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, due_date, priority FROM tasks WHERE status='pending'")
        tasks = [{"title": r[0], "due_date": r[1], "priority": r[2]} for r in cursor.fetchall()]
        conn.close()
        
        if not tasks:
            self.page.snack_bar = ft.SnackBar(ft.Text("Add some tasks first!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        self.ai_plan_area.controls.clear()
        self.ai_plan_area.visible = True
        self.ai_plan_area.controls.append(ft.ProgressRing())
        self.page.update()
        
        plan = self.planner.generate_schedule(tasks)
        self.ai_plan_area.controls.clear()
        self.ai_plan_area.controls.append(ft.Markdown(plan))
        self.page.update()
