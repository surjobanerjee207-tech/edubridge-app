import flet as ft
from ui.theme import get_colors
from data_service import get_assessment_answers, save_assessment_answers, get_skills_assessed


def assessment_screen(page: ft.Page):
    colors = get_colors(page)

    # ── load existing answers ─────────────────────────────────────────────────
    saved_edu, saved_skills, saved_interests = get_assessment_answers()
    selected_interests = set(saved_interests.split(',')) if saved_interests else set()

    # ── form controls ─────────────────────────────────────────────────────────
    education_dd = ft.Dropdown(
        width=400,
        hint_text="e.g. Undergraduate",
        hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY),
        value=saved_edu or None,
        options=[
            ft.dropdown.Option("High School"),
            ft.dropdown.Option("Undergraduate"),
            ft.dropdown.Option("Graduate"),
            ft.dropdown.Option("PhD"),
        ],
        bgcolor=colors.BACKGROUND,
        border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
    )

    skills_field = ft.TextField(
        width=600,
        hint_text="Python, JavaScript, Data Analysis, Communication...",
        value=saved_skills,
        multiline=True,
        min_lines=3,
        bgcolor=colors.BACKGROUND,
        border_color=colors.BORDER,
        color=colors.TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=colors.TEXT_SECONDARY),
    )

    # ── progress calculation ──────────────────────────────────────────────────
    skills_done, skills_total = get_skills_assessed()
    steps_done = sum([
        bool(saved_edu),
        bool(saved_skills),
        bool(saved_interests),
    ])
    total_steps = 5
    progress_val = steps_done / total_steps

    progress_text = ft.Text(f"{steps_done}/{total_steps}", size=14, color=colors.PRIMARY)
    progress_bar  = ft.ProgressBar(value=progress_val, color=colors.PRIMARY, bgcolor=colors.CARD)

    # ── snackbar helper ───────────────────────────────────────────────────────
    def show_snack(msg, color="#10b981"):
        page.snack_bar = ft.SnackBar(
            ft.Text(msg, color="#ffffff"),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # ── save handler ──────────────────────────────────────────────────────────
    def save_and_continue(e):
        edu    = education_dd.value or ""
        skills = skills_field.value or ""

        if not edu:
            show_snack("Please select your education level.", "#ef4444")
            return
        if not skills.strip():
            show_snack("Please enter at least one skill.", "#ef4444")
            return

        interests_str = ",".join(selected_interests)
        save_assessment_answers(edu, skills, interests_str)

        # Update progress display
        new_done = sum([bool(edu), bool(skills), bool(interests_str)])
        progress_text.value = f"{new_done}/{total_steps}"
        progress_bar.value  = new_done / total_steps
        progress_text.update()
        progress_bar.update()

        show_snack("✅ Assessment saved! Dashboard will reflect your updates.")

    # ── interest chips ────────────────────────────────────────────────────────
    INTERESTS = [
        ("Software Development", colors.PRIMARY),
        ("Data Science",         colors.SUCCESS),
        ("Product Management",   colors.WARNING),
        ("UX Design",            colors.ACCENT),
        ("Cybersecurity",        colors.ERROR),
        ("AI / ML",              "#8b5cf6"),
        ("Cloud Computing",      "#06b6d4"),
        ("DevOps",               "#f97316"),
    ]

    chip_controls = []
    for label, color in INTERESTS:
        chip = ft.Chip(
            label=ft.Text(label, size=13, color=colors.TEXT_PRIMARY),
            bgcolor=colors.BACKGROUND,
            selected=label in selected_interests,
            selected_color=f"{color}40",
            on_select=lambda e, lbl=label: (
                selected_interests.add(lbl) if e.control.selected else selected_interests.discard(lbl)
            ),
        )
        chip_controls.append(chip)

    return ft.Container(
        expand=True,
        bgcolor=colors.BACKGROUND,
        padding=ft.Padding.all(28),
        content=ft.Column([
            # Header
            ft.Text("Career Assessment", size=28, weight=ft.FontWeight.BOLD,
                    color=colors.TEXT_PRIMARY),
            ft.Text("Tell us about yourself to get personalized guidance",
                    size=15, color=colors.TEXT_SECONDARY),
            ft.Container(height=20),

            # Progress
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Progress", size=14, color=colors.TEXT_SECONDARY),
                        ft.Container(expand=True),
                        progress_text,
                    ]),
                    progress_bar,
                ], spacing=8),
                padding=ft.Padding.only(bottom=24),
            ),

            # Form card
            ft.Container(
                bgcolor=colors.SURFACE,
                border_radius=16,
                padding=30,
                border=ft.Border.all(1, colors.BORDER),
                content=ft.Column([
                    # Education
                    ft.Text("Education Level", size=16, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    education_dd,
                    ft.Container(height=20),

                    # Skills
                    ft.Text("Your Skills (comma separated)", size=16,
                            weight=ft.FontWeight.W_600, color=colors.TEXT_PRIMARY),
                    ft.Text("Enter skills you have — they'll appear in your skill proficiency chart.",
                            size=12, color=colors.TEXT_SECONDARY),
                    ft.Container(height=6),
                    skills_field,
                    ft.Container(height=20),

                    # Career Interests
                    ft.Text("Career Interests", size=16, weight=ft.FontWeight.W_600,
                            color=colors.TEXT_PRIMARY),
                    ft.Text("Select all that apply", size=12, color=colors.TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Row(chip_controls, wrap=True, spacing=8),
                    ft.Container(height=28),

                    # Buttons
                    ft.Row([
                        ft.ElevatedButton(
                            "Save & Continue",
                            icon=ft.Icons.CHECK,
                            bgcolor=colors.PRIMARY,
                            color="#ffffff",
                            on_click=save_and_continue,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding.symmetric(horizontal=30, vertical=15),
                            ),
                        ),
                        ft.OutlinedButton(
                            "Reset",
                            icon=ft.Icons.REFRESH,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, colors.BORDER),
                                padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                            ),
                            on_click=lambda e: (
                                setattr(education_dd, 'value', None) or
                                setattr(skills_field, 'value', '') or
                                selected_interests.clear() or
                                page.update()
                            ),
                        ),
                    ], spacing=15),
                ], spacing=10),
            ),
        ], spacing=0, scroll=ft.ScrollMode.AUTO),
    )
