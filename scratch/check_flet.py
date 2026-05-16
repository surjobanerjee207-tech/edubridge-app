import flet as ft

def main(page: ft.Page):
    print(f"Page type: {type(page)}")
    print(f"Has client_storage: {hasattr(page, 'client_storage')}")
    if hasattr(page, 'client_storage'):
        print(f"client_storage type: {type(page.client_storage)}")
    page.window_close()

ft.app(target=main)
