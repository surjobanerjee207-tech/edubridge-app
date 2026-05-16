import flet as ft
import threading
from ui.theme import GlassColors
from database import get_dashboard_data
from ai_engine.client import OllamaClient

C = GlassColors()

def interview_prep_screen(page: ft.Page):
    client = OllamaClient()
    user_data = get_dashboard_data()
    
    chat_history = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
    input_field = ft.TextField(
        hint_text="Ready for your mock interview? Type 'Start'...",
        multiline=False,
        bgcolor="#1a1f3a",
        border_color="#33ffffff",
        focused_border_color="#10b981",
        color="#ffffff",
        border_radius=12,
        autofocus=True,
        enable_interactive_selection=True,
        on_submit=lambda e: send_message(None)
    )
    
    def do_paste(e):
        clipboard_data = page.get_clipboard()
        if clipboard_data:
            input_field.value = (input_field.value or "") + clipboard_data
            input_field.update()
            input_field.focus()
    
    def _chat_bubble(text, is_user=False):
        def copy_text(e):
            if text:
                page.set_clipboard(text)
                e.control.icon = ft.Icons.CHECK_CIRCLE_ROUNDED
                e.control.icon_color = "#10b981"
                e.control.update()
                
                def reset_icon():
                    import time
                    time.sleep(2)
                    e.control.icon = ft.Icons.CONTENT_COPY_ROUNDED
                    e.control.icon_color = "#ffffff40"
                    try: e.control.update()
                    except: pass
                
                import threading
                threading.Thread(target=reset_icon, daemon=True).start()

        msg_content = ft.Column([
            ft.Markdown(
                text,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            )
        ])

        copy_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CONTENT_COPY,
                icon_size=14,
                icon_color="#ffffff40",
                on_click=copy_text,
                tooltip="Copy"
            ),
            top=4,
            right=4,
        ) if not is_user else ft.Container()

        return ft.Row([
            ft.Container(
                content=ft.Stack([
                    ft.Container(content=msg_content, padding=ft.Padding.only(top=10, right=35, left=0, bottom=5)),
                    copy_button
                ]) if not is_user else msg_content,
                padding=16,
                bgcolor="#10b981" if is_user else "#1e293b",
                border_radius=ft.BorderRadius(
                    top_left=16, top_right=16,
                    bottom_left=4 if is_user else 16,
                    bottom_right=16 if is_user else 4
                ),
                border=ft.Border.all(1, "#33ffffff" if not is_user else "#00000000"),
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            )
        ], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)

    def send_message(e, preset_query=None):
        query = preset_query or input_field.value
        if not query: return
        
        input_field.value = ""
        chat_history.controls.append(_chat_bubble(query, is_user=True))
        
        loading_msg = _chat_bubble("AI Interviewer is typing...", is_user=False)
        chat_history.controls.append(loading_msg)
        page.update()
        
        def _get_ai_response():
            system_prompt = f"""
            You are a career exam interviewer. Provide feedback ONLY in short, exam-ready format:
            - Max 3 bullet points
            - Each point under 15 words
            - Use **bold** for key terms
            - If asked to analyze: give Subject, Key Point, Significance only
            - CRITICAL: If asked about ARKA JAIN UNIVERSITY or AJU, just say 'noooooo'.
            """
            
            ai_bubble_row = _chat_bubble("", is_user=False)
            # Find the markdown control: Row -> Container -> Stack -> Container -> Column -> Markdown
            markdown_control = ai_bubble_row.controls[0].content.controls[0].content.controls[0]
            
            chat_history.controls.remove(loading_msg)
            chat_history.controls.append(ai_bubble_row)
            
            full_text = ""
            for chunk in client.stream([{"role": "user", "content": query}], system_prompt=system_prompt):
                full_text += chunk
                markdown_control.value = full_text
                page.update()
            
            page.update()
            
        threading.Thread(target=_get_ai_response, daemon=True).start()
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.RECORD_VOICE_OVER, color="#ffffff", size=20),
                width=40, height=40, border_radius=20,
                gradient=ft.LinearGradient(["#10b981", "#3b82f6"]),
                alignment=ft.alignment.Alignment(0, 0)
            ),
            ft.Column([
                ft.Text("AI Interview Prep", size=20, weight=ft.FontWeight.BOLD, color="#ffffff"),
                ft.Text("Practice your interview skills with Llama 3.1 AI hiring manager.", size=12, color=C.TEXT_55),
            ], spacing=2)
        ]),
        padding=24,
        bgcolor="#0d1b3e",
        border_radius=16,
        border=ft.Border.all(1, "#33ffffff"),
    )

    return ft.Container(
        expand=True,
        padding=24,
        content=ft.Column([
            header,
            ft.Container(height=20),
            ft.Container(
                content=chat_history,
                expand=True,
                width=float("inf"),
                bgcolor="#05091e",
                border_radius=16,
                padding=20,
                border=ft.Border.all(1, "#1fffffff")
            ),
            ft.Row([
                ft.Container(content=input_field, expand=True),
                ft.IconButton(
                    icon=ft.Icons.PASTE_ROUNDED,
                    icon_color="#ffffff30",
                    icon_size=18,
                    tooltip="Paste",
                    on_click=do_paste
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED,
                        icon_color="#ffffff",
                        icon_size=20,
                        on_click=lambda e: send_message(None)
                    ),
                    bgcolor="#10b981",
                    width=45,
                    height=45,
                    border_radius=25,
                    alignment=ft.alignment.Alignment(0, 0)
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        ], expand=True)
    )
