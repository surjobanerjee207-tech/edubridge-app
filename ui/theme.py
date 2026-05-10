import flet as ft
from dataclasses import dataclass


# ── glassmorphism palette ────────────────────────────────────────────────────
# Flet/Flutter uses 0xAARRGGBB — when passing "#AARRGGBB" hex strings,
# the FIRST two hex digits are the alpha channel.

@dataclass
class GlassColors:
    # Solid accents
    PRIMARY    = "#6366f1"
    SECONDARY  = "#8b5cf6"
    TEAL       = "#14b8a6"
    AMBER      = "#f59e0b"
    GREEN      = "#22c55e"
    RED        = "#ef4444"
    ACCENT     = "#ec4899"

    # Glass surfaces  — format: #AARRGGBB (alpha FIRST)
    GLASS_WEAK   = "#12ffffff"   # rgba(255,255,255, 0.07)
    GLASS_MED    = "#1fffffff"   # rgba(255,255,255, 0.12)
    GLASS_STRONG = "#2bffffff"   # rgba(255,255,255, 0.17)
    GLASS_HOVER  = "#33ffffff"   # rgba(255,255,255, 0.20)

    SIDEBAR_BG   = "#b20a143c"   # rgba(10, 20, 60,  0.70)
    ACTIVE_NAV   = "#406366f1"   # rgba(99,102,241,  0.25)
    ACTIVE_BORDER= "#596366f1"   # rgba(99,102,241,  0.35)

    BORDER_WEAK  = "#1fffffff"   # rgba(255,255,255, 0.12)
    BORDER_MED   = "#33ffffff"   # rgba(255,255,255, 0.20)
    SHADOW       = "#59000000"   # rgba(0,0,0,        0.35)

    # Text hierarchy (#AARRGGBB)
    TEXT_WHITE   = "#ffffff"
    TEXT_55      = "#8cffffff"   # rgba(255,255,255, 0.55)
    TEXT_45      = "#73ffffff"   # rgba(255,255,255, 0.45)
    TEXT_30      = "#4dffffff"   # rgba(255,255,255, 0.30)

    # Aliases expected by non-dashboard screens
    BACKGROUND     = "#05091e"
    SURFACE        = "#12ffffff"
    CARD           = "#1fffffff"
    BORDER         = "#1fffffff"
    TEXT_PRIMARY   = "#ffffff"
    TEXT_SECONDARY = "#8cffffff"
    SUCCESS        = "#22c55e"
    WARNING        = "#f59e0b"
    ERROR          = "#ef4444"


def get_colors(page: ft.Page):
    return GlassColors()


@dataclass
class AppTheme:
    def __init__(self):
        pass

    def get_page_theme(self) -> ft.Theme:
        return ft.Theme(
            font_family="Segoe UI",
            color_scheme=ft.ColorScheme(
                primary="#6366f1",
                secondary="#8b5cf6",
            ),
        )
