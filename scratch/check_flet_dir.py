import flet as ft

def main(page: ft.Page):
    with open("scratch/page_dir.txt", "w") as f:
        f.write("\n".join(dir(page)))
    page.window_destroy() # Try another one

ft.app(target=main)
