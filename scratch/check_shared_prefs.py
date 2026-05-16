import flet as ft

def main(page: ft.Page):
    print(f"shared_preferences: {page.shared_preferences}")
    # try setting something
    try:
        page.shared_preferences.set("test_key", "test_value")
        val = page.shared_preferences.get("test_key")
        print(f"Value retrieved: {val}")
    except Exception as e:
        print(f"Error: {e}")
    page.window_destroy()

ft.app(target=main)
