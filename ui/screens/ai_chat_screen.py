import flet as ft
import threading
import base64
import os
from ui.theme import GlassColors
from database import get_dashboard_data
from ai_engine.client import OllamaClient
import tkinter as tk
from tkinter import filedialog

C = GlassColors() # Refresh comment

def ai_chat_screen(page: ft.Page, file_picker=None):
    client = OllamaClient()
    user_data = get_dashboard_data()
    
    chat_history = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
    input_field = ft.TextField(
        hint_text="Message your Career Copilot...",
        multiline=False,
        bgcolor="transparent",
        border_color="transparent",
        focused_border_color="transparent",
        color="#e2e8f0",
        hint_style=ft.TextStyle(color="#ffffff30", size=14),
        text_style=ft.TextStyle(size=14),
        cursor_color="#6366f1",
        expand=True,
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
                code_theme="atom-one-dark",
            )
        ], tight=True)

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

        bubble = ft.Container(
            content=ft.Stack([
                ft.Container(content=msg_content, padding=ft.Padding.only(top=10, right=35, left=0, bottom=5)), # Increased right padding
                copy_button
            ]) if not is_user else msg_content,
            padding=16,
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),
                end=ft.alignment.Alignment(1, 1),
                colors=["#6366f1", "#8b5cf6"] if is_user else ["#1e2744", "#1a2035"]
            ) if is_user else None,
            bgcolor=None if is_user else "#161f38",
            border_radius=ft.BorderRadius(
                top_left=18, top_right=18,
                bottom_left=4 if is_user else 18,
                bottom_right=18 if is_user else 4
            ),
            border=ft.Border.all(1, "#ffffff15" if not is_user else "#ffffff00"),
            shadow=ft.BoxShadow(
                blur_radius=16, spread_radius=0,
                color="#406366f1" if is_user else "#20000000",
                offset=ft.Offset(0, 4)
            ),
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )

        return ft.Row(
            [bubble],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        )

    def _typing_indicator():
        """Modern animated typing indicator — 3 pulsing dots."""
        dot = lambda delay: ft.Container(
            width=8, height=8,
            border_radius=4,
            bgcolor="#6366f1",
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
            opacity=0.3,
        )
        d1, d2, d3 = dot(0), dot(200), dot(400)

        class PulseState:
            running = True

        state = PulseState()

        def _pulse():
            import time
            while state.running:
                # Breathing effect: Scale up and brighten
                typing_bubble.scale = 1.05
                for d in [d1, d2, d3]:
                    if not state.running: break
                    d.opacity = 1.0
                    try: page.update()
                    except: return
                    time.sleep(0.2)
                
                # Breathing effect: Scale down and dim
                typing_bubble.scale = 1.0
                for d in [d1, d2, d3]:
                    if not state.running: break
                    d.opacity = 0.3
                    try: page.update()
                    except: return
                    time.sleep(0.2)
                time.sleep(0.2)

        typing_bubble = ft.Container(
            content=ft.Row([d1, d2, d3], spacing=6),
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            bgcolor="#161f38",
            border_radius=ft.BorderRadius(top_left=18, top_right=18, bottom_left=18, bottom_right=4),
            border=ft.Border.all(1, "#ffffff15"),
            shadow=ft.BoxShadow(blur_radius=16, spread_radius=0, color="#20000000", offset=ft.Offset(0, 4)),
            animate_scale=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
        )

        return ft.Row([typing_bubble], alignment=ft.MainAxisAlignment.START), d1, d2, d3, _pulse, state

    # File Attachment State
    attached_files = [] # List of {'name': str, 'type': str, 'content': str/base64}
    
    def pick_files_native(e):
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        paths = filedialog.askopenfilenames(
            title="Select files or photos",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp"),
                ("Documents", "*.pdf *.txt"),
                ("All files", "*.*")
            ]
        )
        root.destroy()
        
        if not paths: return
        
        for path in paths:
            file_name = os.path.basename(path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            try:
                with open(path, "rb") as file_data:
                    raw_bytes = file_data.read()
                    
                if file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    b64 = base64.b64encode(raw_bytes).decode("utf-8")
                    attached_files.append({"name": file_name, "type": "image", "content": b64})
                elif file_ext == ".pdf":
                    try:
                        from pypdf import PdfReader
                        reader = PdfReader(path)
                        text = ""
                        for page_num in range(len(reader.pages)):
                            text += reader.pages[page_num].extract_text()
                        attached_files.append({"name": file_name, "type": "pdf", "content": text})
                    except Exception as ex:
                        chat_history.controls.append(ft.Text(f"Error reading PDF: {str(ex)}", color="red"))
                else:
                    try:
                        text = raw_bytes.decode("utf-8")
                        attached_files.append({"name": file_name, "type": "text", "content": text})
                    except:
                        chat_history.controls.append(ft.Text(f"Unsupported file type: {file_ext}", color="orange"))
            except Exception as ex:
                chat_history.controls.append(ft.Text(f"Error opening file: {str(ex)}", color="red"))
        
        update_attachment_ui()
        page.update()

    file_picker = None

    attachment_preview = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def update_attachment_ui():
        attachment_preview.controls.clear()
        for i, f in enumerate(attached_files):
            attachment_preview.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.IMAGE if f['type']=='image' else ft.Icons.PICTURE_AS_PDF if f['type']=='pdf' else ft.Icons.INSERT_DRIVE_FILE, size=12, color="white"),
                        ft.Text(f['name'][:10]+"...", size=10, color="white"),
                        ft.IconButton(ft.Icons.CLOSE, icon_size=10, icon_color="white60", on_click=lambda _, idx=i: remove_attachment(idx))
                    ], spacing=4),
                    bgcolor="#33ffffff",
                    padding=ft.Padding(8, 4, 4, 4),
                    border_radius=15,
                )
            )
        attachment_preview.visible = len(attached_files) > 0
        page.update()

    def remove_attachment(index):
        if 0 <= index < len(attached_files):
            attached_files.pop(index)
            update_attachment_ui()

    def send_message(e, preset_query=None):
        query = preset_query or input_field.value
        if not query and not attached_files: return

        input_field.value = ""
        
        # Build user display message
        display_msg = query
        if attached_files:
            display_msg += "\n\n*Attached files:* " + ", ".join([f['name'] for f in attached_files])
            
        chat_history.controls.append(_chat_bubble(display_msg, is_user=True))

        typing_row, d1, d2, d3, pulse_fn, pulse_state = _typing_indicator()
        chat_history.controls.append(typing_row)
        page.update()
        threading.Thread(target=pulse_fn, daemon=True).start()

        def _get_ai_response():
            # Create bubble early for streaming
            ai_bubble_container = _chat_bubble("", is_user=False)
            # Find the markdown control inside the stack/container structure
            # bubble -> Stack -> Container -> Column -> Markdown
            markdown_control = ai_bubble_container.controls[0].content.controls[0].content.controls[0]
            
            chat_history.controls.remove(typing_row)
            chat_history.controls.append(ai_bubble_container)
            
            # Build message payload for multi-modal
            user_content_list = []
            if query:
                user_content_list.append({"type": "text", "text": query})
            
            for f in attached_files:
                if f['type'] == 'image':
                    user_content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{f['content']}"}
                    })
                else:
                    # Append file content as text context
                    user_content_list.append({
                        "type": "text", 
                        "text": f"\n[File Content: {f['name']}]\n{f['content']}\n"
                    })
            
            # Clear attachments after sending
            attached_files.clear()
            update_attachment_ui()

            full_text = ""
            messages = [{"role": "user", "content": user_content_list}]
            
            for chunk in client.stream(messages, system_prompt=client._get_sys_prompt(user_data)):
                pulse_state.running = False # Stop pulsing on first chunk
                full_text += chunk
                markdown_control.value = full_text
                page.update()
            
            pulse_state.running = False # Safety stop
            page.update()

        threading.Thread(target=_get_ai_response, daemon=True).start()
        page.update()

    # Quick Action Buttons
    def quick_action(label, query):
        return ft.Container(
            content=ft.Text(label, size=12, color="#ffffff", weight=ft.FontWeight.W_500),
            bgcolor="#1a1f3a",
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=20,
            border=ft.Border.all(1, "#33ffffff"),
            on_click=lambda e: send_message(None, preset_query=query),
            on_hover=lambda e: setattr(e.control, 'bgcolor', "#312e81" if e.data == "true" else "#1a1f3a") or e.control.update()
        )

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME, color="#ffffff", size=20),
                    width=40, height=40, border_radius=20,
                    gradient=ft.LinearGradient(["#6366f1", "#a855f7"]),
                    alignment=ft.alignment.Alignment(0, 0)
                ),
                ft.Column([
                    ft.Text("AI Career Copilot", size=20, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text("Your personal path to success, powered by Llama 3.1 AI.", size=12, color=C.TEXT_55),
                ], spacing=2)
            ]),
            ft.Container(height=10),
            ft.Row([
                quick_action("📊 Analyze my path", "Based on my current skills and match %, what is my best next step?"),
                quick_action("📚 Study plan", "Create a focused study plan for my weakest skills."),
                quick_action("🎯 Next Milestone", "How can I better prepare for my upcoming milestone?"),
            ], wrap=True)
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
            # Attachment Preview Area
            attachment_preview,
            # ── Modern pill input bar ──────────────────────────────────────────
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ADD, 
                            icon_color="#6366f1", 
                            icon_size=20,
                            on_click=pick_files_native, 
                            tooltip="Attach photos/files"
                        ),
                        padding=ft.Padding.only(left=0, right=0),
                    ),
                    input_field,
                    # Dedicated Paste Button (Fix for Win+V issues)
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
                            icon_size=18,
                            on_click=lambda e: send_message(None),
                            tooltip="Send (Enter)",
                        ),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.Alignment(-1, -1),
                            end=ft.alignment.Alignment(1, 1),
                            colors=["#6366f1", "#8b5cf6"]
                        ),
                        width=42,
                        height=42,
                        border_radius=21,
                        alignment=ft.alignment.Alignment(0, 0),
                        shadow=ft.BoxShadow(
                            blur_radius=14, spread_radius=0,
                            color="#806366f1", offset=ft.Offset(0, 4)
                        ),
                        margin=ft.Margin(right=4, top=0, bottom=0, left=0)
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                bgcolor="#111827",
                border_radius=28,
                border=ft.Border.all(1, "#ffffff18"),
                shadow=ft.BoxShadow(
                    blur_radius=24, spread_radius=0,
                    color="#30000000", offset=ft.Offset(0, 4)
                ),
                padding=ft.Padding.only(left=10, right=6, top=4, bottom=4),
                margin=ft.Margin(top=12, bottom=0, left=0, right=0),
            )
        ], expand=True)
    )
