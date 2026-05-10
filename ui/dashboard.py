import flet as ft
from database import get_connection

class DashboardScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.spacing = 20
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        
        self.build_ui()

    def build_ui(self):
        # Stats from DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='pending'")
        pending_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(score) FROM mood_logs")
        avg_mood = cursor.fetchone()[0] or 0
        conn.close()

        self.controls = [
            ft.Text("Welcome to EduBridge AI", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Empowering students through AI and Community Support", size=16, italic=True),
            
            ft.Row([
                self.stat_card("Pending Tasks", str(pending_tasks), ft.icons.ASSIGNMENT),
                self.stat_card("Avg Mood", f"{avg_mood:.1f}/5.0", ft.icons.EMOJI_EMOTIONS),
                self.stat_card("Resources", "3 Local", ft.icons.LOCATION_ON),
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(),
            
            ft.Text("Quick Actions", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("New AI Summary", icon=ft.icons.AUTO_AWESOME, on_click=lambda _: self.page.go("/ai-chat")),
                ft.ElevatedButton("Plan My Week", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.page.go("/planner")),
                ft.ElevatedButton("How are you feeling?", icon=ft.icons.FAVORITE, on_click=lambda _: self.page.go("/wellbeing")),
            ]),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.INFO),
                            title=ft.Text("AI Ethics & Transparency"),
                            subtitle=ft.Text("EduBridge AI uses local LLMs to ensure your data never leaves your device. Suggestions are AI-generated; always verify critical information."),
                        )
                    ]),
                    padding=10
                )
            )
        ]

    def stat_card(self, title, value, icon):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=30, color=ft.colors.BLUE_400),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            width=150
        )
