import flet as ft
from ui.theme import get_colors
from data_service import get_preference, set_preference


def settings_screen(page: ft.Page, refresh_callback):
    colors = get_colors(page)

    # ── load persisted preferences ────────────────────────────────────────────
    notif_val = get_preference("notifications", "true") == "true"

    saved_text = ft.Ref[ft.Text]()

    def toggle_dark_mode(e):
        if e.control.value:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor    = "#0f172a"
            set_preference("dark_mode", "true")
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor    = "#f1f5f9"
            set_preference("dark_mode", "false")
        page.update()
        refresh_callback()

    def toggle_notifications(e):
        set_preference("notifications", "true" if e.control.value else "false")

    def save_settings(e):
        saved_text.current.visible = True
        saved_text.current.update()
        import threading
        def _hide():
            import time; time.sleep(2)
            saved_text.current.visible = False
            saved_text.current.update()
        threading.Thread(target=_hide, daemon=True).start()

    def _pref_row(label, sub, control):
        return ft.Container(
            bgcolor=colors.SURFACE,
            border_radius=10,
            border=ft.Border.all(1, colors.BORDER),
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            content=ft.Row([
                ft.Column([
                    ft.Text(label, size=14, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Text(sub, size=12, color=colors.TEXT_SECONDARY),
                ], spacing=2, expand=True),
                control,
            ]),
        )

    return ft.Container(
        expand=True, bgcolor=colors.BACKGROUND,
        padding=ft.Padding.all(28),
        content=ft.Column([
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_PRIMARY),
            ft.Text("Manage your preferences", size=15, color=colors.TEXT_SECONDARY),
            ft.Container(height=24),

            ft.Text("Appearance", size=13, color=colors.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=8),
            _pref_row("Dark Mode",
                      "Switch between dark and light theme",
                      ft.Switch(value=page.theme_mode == ft.ThemeMode.DARK,
                                on_change=toggle_dark_mode)),

            ft.Container(height=20),
            ft.Text("Notifications", size=13, color=colors.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=8),
            _pref_row("Push Notifications",
                      "Receive milestone and activity reminders",
                      ft.Switch(value=notif_val, on_change=toggle_notifications)),

            ft.Container(height=28),
            ft.Row([
                ft.ElevatedButton(
                    "Save Changes",
                    icon=ft.Icons.SAVE,
                    bgcolor=colors.PRIMARY, color="#ffffff",
                    on_click=save_settings,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                         padding=ft.Padding.symmetric(horizontal=24, vertical=12)),
                ),
                ft.Text("✅ Saved!", ref=saved_text, size=13, color="#10b981",
                        visible=False),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=4, scroll=ft.ScrollMode.AUTO),
    )
