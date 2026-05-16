import flet as ft
from main import main

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, assets_dir="assets")
