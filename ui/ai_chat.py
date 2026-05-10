import flet as ft
from ai_engine.summarizer import DocumentSummarizer
from utils.file_handler import extract_text
import os

class AIChatScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.summarizer = DocumentSummarizer()
        self.expand = True
        
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)
        
        self.result_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        self.loading_spinner = ft.ProgressRing(visible=False)
        
        self.build_ui()

    def build_ui(self):
        self.controls = [
            ft.Text("AI Document Assistant", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Upload a PDF or TXT to summarize and generate a quiz.", size=14),
            
            ft.Row([
                ft.ElevatedButton("Upload Document", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: self.file_picker.pick_files()),
                self.loading_spinner,
            ]),
            
            ft.Divider(),
            self.result_area
        ]

    def on_file_result(self, e):
        if e.files:
            file_path = e.files[0].path
            self.loading_spinner.visible = True
            self.result_area.controls.clear()
            self.page.update()
            
            text = extract_text(file_path)
            if "Error" in text:
                self.result_area.controls.append(ft.Text(text, color=ft.Colors.RED))
            else:
                summary_data = self.summarizer.summarize_and_quiz(text)
                self.result_area.controls.append(
                    ft.Markdown(summary_data, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED)
                )
            
            self.loading_spinner.visible = False
            self.page.update()
