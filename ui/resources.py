import flet as ft
from database import get_connection

class ResourcesScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.resource_grid = ft.GridView(expand=True, max_extent=300, child_aspect_ratio=1.0)
        
        self.build_ui()
        self.load_resources()

    def build_ui(self):
        self.controls = [
            ft.Text("Community & Campus Resources", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Find NGOs, counseling services, and support near you.", size=14),
            ft.Divider(),
            self.resource_grid
        ]

    def load_resources(self):
        self.resource_grid.controls.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, category, location, contact, open_hours FROM resources")
        for row in cursor.fetchall():
            self.resource_grid.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(row[0], size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(row[1], size=12, color=ft.colors.BLUE_200),
                            ft.Divider(),
                            ft.Row([ft.Icon(ft.icons.LOCATION_ON, size=16), ft.Text(row[2], size=12)], wrap=True),
                            ft.Row([ft.Icon(ft.icons.PHONE, size=16), ft.Text(row[3], size=12)]),
                            ft.Row([ft.Icon(ft.icons.ACCESS_TIME, size=16), ft.Text(row[4], size=12)]),
                        ], spacing=5),
                        padding=15
                    )
                )
            )
        conn.close()
