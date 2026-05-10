import flet as ft
from database import get_connection
from ai_engine.wellbeing import WellbeingAdvisor

class WellbeingScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.advisor = WellbeingAdvisor()
        self.expand = True
        
        self.mood_slider = ft.Slider(min=1, max=5, divisions=4, label="{value}/5")
        self.journal_input = ft.TextField(label="How are you feeling today?", multiline=True, min_lines=3)
        self.ai_response_area = ft.Column()
        
        self.build_ui()

    def build_ui(self):
        self.controls = [
            ft.Text("Mood & Wellbeing Tracker", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Track your mood and get AI-powered coping suggestions.", size=14),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Select your mood (1: Low, 5: Great)"),
                    self.mood_slider,
                    self.journal_input,
                    ft.ElevatedButton("Save & Get AI Tip", icon=ft.icons.SAVE, on_click=self.save_mood),
                ]),
                padding=20,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10
            ),
            
            ft.Divider(),
            ft.Text("AI Wellbeing Suggestion", size=20, weight=ft.FontWeight.BOLD),
            self.ai_response_area
        ]

    def save_mood(self, e):
        score = int(self.mood_slider.value)
        note = self.journal_input.value
        
        # Save to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mood_logs (score, note) VALUES (?, ?)", (score, note))
        conn.commit()
        conn.close()
        
        # Get AI Tip
        self.ai_response_area.controls.clear()
        self.ai_response_area.controls.append(ft.ProgressRing())
        self.page.update()
        
        tip = self.advisor.get_suggestion(score, note)
        self.ai_response_area.controls.clear()
        self.ai_response_area.controls.append(
            ft.Container(
                content=ft.Text(tip, italic=True),
                padding=15,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5
            )
        )
        self.page.update()
