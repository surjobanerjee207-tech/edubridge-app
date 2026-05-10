import flet as ft
from ui.theme import get_colors


def placeholder_screen(page: ft.Page, title: str, icon=ft.Icons.CONSTRUCTION):
    colors = get_colors(page)
    return ft.Container(
        expand=True,
        bgcolor=colors.BACKGROUND,
        content=ft.Column([
            ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
            ft.Container(height=40),
            ft.Icon(icon, size=64, color="#334155"),
            ft.Container(height=16),
            ft.Text("Coming Soon", size=20, color=colors.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600),
            ft.Text("This section is under construction.",
                    size=14, color=colors.TEXT_SECONDARY),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER),
    )
