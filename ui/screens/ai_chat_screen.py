import flet as ft
import threading
import base64
import os
import time
import random
import speech_recognition as sr
from ui.theme import GlassColors
from database import get_dashboard_data
from ai_engine.client import OllamaClient
from utils.history_manager import save_search_history, load_search_history, save_chat_log, load_chat_log
import tkinter as tk
from tkinter import filedialog

C = GlassColors() # Refresh comment

def ai_chat_screen(page: ft.Page, file_picker=None):
    client = OllamaClient()
    user_data = get_dashboard_data()
    
    # Session Memory
    session_messages = load_chat_log(page) # Persist across sessions
    
    # AI Mode State
    mode_state = {"is_quick": True} # Use dict for mutable reference in inner functions

    def set_mode(is_quick):
        mode_state["is_quick"] = is_quick
        footer_status.visible = is_quick
        # Re-build header to reflect selection
        header.content.controls[0].controls[2].content.controls[0].bgcolor = "#33ffffff" if is_quick else "transparent"
        header.content.controls[0].controls[2].content.controls[0].border = ft.Border.all(1, "#40ffffff") if is_quick else None
        header.content.controls[0].controls[2].content.controls[1].bgcolor = "#33ffffff" if not is_quick else "transparent"
        header.content.controls[0].controls[2].content.controls[1].border = ft.Border.all(1, "#40ffffff") if not is_quick else None
        
        # Update icons/text color
        header.content.controls[0].controls[2].content.controls[0].content.controls[0].color = "#ffffff" if is_quick else "#ffffff40"
        header.content.controls[0].controls[2].content.controls[0].content.controls[1].color = "#ffffff" if is_quick else "#ffffff40"
        header.content.controls[0].controls[2].content.controls[1].content.controls[0].color = "#ffffff" if not is_quick else "#ffffff40"
        header.content.controls[0].controls[2].content.controls[1].content.controls[1].color = "#ffffff" if not is_quick else "#ffffff40"
        
        page.update()
    
    chat_history = ft.ListView(
        expand=True, 
        spacing=14, 
        auto_scroll=True,
        padding=ft.Padding(0, 0, 0, 20)
    )

    def clear_chat(e):
        session_messages.clear()
        save_chat_log(page, []) # Clear persistent log
        chat_history.controls.clear()
        page.update()
    input_field = ft.TextField(
        hint_text="Message your Career Copilot...",
        multiline=False,
        bgcolor="transparent",
        border_color="transparent",
        focused_border_color="transparent",
        color="#ffffff",
        hint_style=ft.TextStyle(color="#59ffffff", size=15), # rgba(255,255,255,0.35)
        text_style=ft.TextStyle(size=15),
        cursor_color="#6366f1",
        expand=True,
        autofocus=True,
        enable_interactive_selection=True,
        on_submit=lambda e: send_message(None),
        on_change=lambda e: on_input_change(e)
    )
    
    def on_input_change(e):
        if not is_recording[0]:
            if input_field.value and input_field.value.strip():
                send_btn_icon.icon = ft.Icons.SEND_ROUNDED
                send_btn_icon.tooltip = "Send (Enter)"
            else:
                send_btn_icon.icon = ft.Icons.MIC_ROUNDED
                send_btn_icon.tooltip = "Voice Typing"
            send_btn_icon.update()
    
    async def do_paste(e):
        clipboard_data = await page.clipboard.get()
        if clipboard_data:
            input_field.value = (input_field.value or "") + clipboard_data
            input_field.update()
            try:
                await input_field.focus()
            except:
                input_field.focus() # Fallback for sync focus
            on_input_change(None)
    
    # --- Voice Typing Logic ---
    is_recording = [False]
    
    waveform_bars = ft.Row(
        spacing=3,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=4, height=6, 
                bgcolor="#a096ff", 
                border_radius=2, 
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            ) for _ in range(20)
        ]
    )
    
    waveform_container = ft.Container(
        content=waveform_bars,
        expand=True,
        visible=False,
        height=40,
        alignment=ft.alignment.Alignment(0, 0)
    )

    def animate_waveform():
        while is_recording[0]:
            for bar in waveform_bars.controls:
                bar.height = random.randint(6, 35)
            try:
                waveform_bars.update()
            except: break
            time.sleep(0.15)

    def listen_loop():
        print("Voice: Starting listen loop...")
        r = sr.Recognizer()
        try:
            print("Voice: Accessing microphone...")
            with sr.Microphone() as source:
                print("Voice: Microphone accessed. Adjusting for noise...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("Voice: Listening...")
                while is_recording[0]:
                    try:
                        audio = r.listen(source, timeout=2, phrase_time_limit=10)
                        print("Voice: Audio captured. Recognizing...")
                        text = r.recognize_google(audio)
                        print(f"Voice: Recognized text: {text}")
                        if is_recording[0]:
                            current_val = input_field.value or ""
                            input_field.value = (current_val + " " + text).strip()
                            input_field.update()
                            on_input_change(None)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        print("Voice: Could not understand audio")
                        continue
                    except Exception as ex:
                        print(f"Voice: Recognition error: {ex}")
                        continue
        except Exception as e:
            print(f"Voice: Microphone error: {e}")
            is_recording[0] = False

    def start_voice_typing(e):
        if is_recording[0]: return
        is_recording[0] = True
        input_field.visible = False
        waveform_container.visible = True
        
        # UI Toggles
        send_btn_icon.icon = ft.Icons.MIC_ROUNDED
        send_btn_icon.icon_color = "#ffffff"
        send_btn_icon.tooltip = "Click to stop & keep text"
        
        # Red background while recording
        send_btn_container.gradient = None
        send_btn_container.bgcolor = "#E24B4A"
        
        voice_controls.visible = True
        page.update()
        
        threading.Thread(target=animate_waveform, daemon=True).start()
        threading.Thread(target=listen_loop, daemon=True).start()

    def stop_voice_typing(confirm=True):
        is_recording[0] = False
        input_field.visible = True
        waveform_container.visible = False
        
        # Back to purple gradient
        send_btn_container.bgcolor = None
        send_btn_container.gradient = ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#6366f1", "#8b5cf6"]
        )
        
        # Restore icon based on text
        if input_field.value and input_field.value.strip():
            send_btn_icon.icon = ft.Icons.SEND_ROUNDED
            send_btn_icon.tooltip = "Send (Enter)"
        else:
            send_btn_icon.icon = ft.Icons.MIC_ROUNDED
            send_btn_icon.tooltip = "Voice Typing"
            
        send_btn_icon.icon_color = "#ffffff"
        voice_controls.visible = False
        
        if not confirm:
            input_field.value = ""
            
        page.update()

    def on_mic_click(e):
        print(f"DEBUG: Mic Clicked. Recording: {is_recording[0]}, Input text: '{input_field.value}'")
        if input_field.value and input_field.value.strip() and not is_recording[0]:
            print("DEBUG: Sending message")
            send_message(None)
        elif is_recording[0]:
            print("DEBUG: Stopping voice typing (confirm)")
            stop_voice_typing(True)
        else:
            print("DEBUG: Starting voice typing")
            start_voice_typing(e)

    def on_broadcast_message(msg):
        if msg == "trigger_mic":
            print("DEBUG: Received trigger_mic signal")
            on_mic_click(None)
    
    page.pubsub.subscribe(on_broadcast_message)

    # --- UI Components for Input Bar ---
    cancel_btn = ft.IconButton(
        icon=ft.Icons.CLOSE_ROUNDED,
        icon_color="#ff4444",
        icon_size=20,
        on_click=lambda e: stop_voice_typing(False),
        tooltip="Cancel & Discard"
    )
    confirm_btn = ft.IconButton(
        icon=ft.Icons.CHECK_ROUNDED,
        icon_color="#10b981",
        icon_size=20,
        on_click=lambda e: stop_voice_typing(True),
        tooltip="Confirm text"
    )
    voice_controls = ft.Row([
        cancel_btn,
        confirm_btn,
        ft.Container(width=5), # Extra spacing
    ], visible=False, spacing=0)

    send_btn_icon = ft.IconButton(
        icon=ft.Icons.MIC_ROUNDED,
        icon_color="#ffffff",
        icon_size=18,
        on_click=on_mic_click,
        tooltip="Voice Typing",
    )
    send_btn_container = ft.Container(
        content=send_btn_icon,
        on_click=on_mic_click, # Capture clicks on the entire circle
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#6366f1", "#8b5cf6"]
        ),
        width=48, # Increased size for better hit area
        height=48,
        border_radius=24,
        alignment=ft.alignment.Alignment(0, 0),
        shadow=ft.BoxShadow(
            blur_radius=14, spread_radius=0,
            color="#806366f1", offset=ft.Offset(0, 4)
        ),
        margin=ft.Margin(right=4, top=0, bottom=0, left=0)
    )
    
    def _chat_bubble(text, is_user=False, image_b64=None):
        markdown_ref = ft.Ref[ft.Markdown]()
        text_ref = ft.Ref[ft.Text]()

        def copy_text(e):
            if text:
                page.clipboard.set(text)
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

        # Turbo-Text: Use plain Text for lightning fast streaming, swap to Markdown later
        msg_markdown = ft.Markdown(
            text,
            ref=markdown_ref,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            code_theme="atom-one-dark",
            visible=False if not text else True # Hide if empty for streaming
        )
        msg_text = ft.Text(text, ref=text_ref, size=14, color="#e2e8f0", visible=True if not text else False)

        content_items = []
        if image_b64:
            content_items.append(
                ft.Container(
                    content=ft.Image(
                        src_base64=image_b64,
                        width=200,
                        border_radius=12,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    margin=ft.Margin(0, 0, 0, 8) if text else 0,
                )
            )
        
        # Quick Answer Badge
        if not is_user and mode_state["is_quick"] and text:
             content_items.append(
                 ft.Container(
                     content=ft.Row([
                         ft.Icon(ft.Icons.BOLT, size=12, color="#6366f1"),
                         ft.Text("Quick answer", size=10, weight=ft.FontWeight.BOLD, color="#6366f1"),
                     ], spacing=4),
                     bgcolor="#ffffff",
                     padding=ft.Padding(8, 4, 8, 4),
                     border_radius=20,
                     margin=ft.Margin(0, 0, 0, 8),
                 )
             )
        
        content_items.extend([msg_markdown, msg_text])
        msg_content = ft.Column(content_items, tight=True)

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
                ft.Container(content=msg_content, padding=ft.Padding.only(top=10, right=35, left=0, bottom=5)), 
                copy_button
            ]) if not is_user else msg_content,
            padding=16,
            gradient=ft.LinearGradient(colors=["#6c63ff", "#8b5cf6"], begin=ft.alignment.Alignment(-1, -1), end=ft.alignment.Alignment(1, 1)) if is_user else None,
            bgcolor=None if is_user else "#14ffffff", 
            blur=ft.Blur(16, 16, ft.BlurTileMode.MIRROR) if not is_user else None,
            border_radius=ft.BorderRadius(
                top_left=16, top_right=16,
                bottom_left=16 if is_user else 16,
                bottom_right=4 if is_user else 16
            ) if is_user else ft.BorderRadius(
                top_left=16, top_right=16,
                bottom_left=16,
                bottom_right=4
            ),
            border=ft.Border.all(1, "#33ffffff" if is_user else "#1effffff"), 
            shadow=ft.BoxShadow(
                blur_radius=24, spread_radius=0,
                color="#596c63ff" if is_user else "#40000000", 
                offset=ft.Offset(0, 4)
            ),
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0.2), 
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            opacity=1.0, 
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
        )

        def trigger_anim():
            import time
            time.sleep(0.05)
            bubble.offset = ft.Offset(0, 0)
            try: bubble.update()
            except: pass
        threading.Thread(target=trigger_anim, daemon=True).start()

        return ft.Row(
            [bubble],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        ), markdown_ref, text_ref

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
            bgcolor="#10ffffff",
            blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
            border_radius=ft.BorderRadius(top_left=18, top_right=18, bottom_left=18, bottom_right=4),
            border=ft.Border.all(1, "#20ffffff"),
            shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#20000000", offset=ft.Offset(0, 8)),
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
            if f['type'] == 'image':
                preview_content = ft.Image(
                    src=base64.b64decode(f['content']),
                    width=60, height=60,
                    border_radius=8,
                    fit=ft.BoxFit.COVER
                )
            else:
                preview_content = ft.Column([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF if f['type']=='pdf' else ft.Icons.INSERT_DRIVE_FILE, size=20, color="white"),
                    ft.Text(f['name'][:6]+"...", size=8, color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
            
            attachment_preview.controls.append(
                ft.Stack([
                    ft.Container(
                        content=preview_content,
                        width=60, height=60,
                        bgcolor="#22ffffff",
                        border_radius=8,
                        padding=4 if f['type'] != 'image' else 0,
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            ft.Icons.CLOSE, 
                            icon_size=12, 
                            icon_color="white",
                            bgcolor="#cc000000",
                            on_click=lambda _, idx=i: remove_attachment(idx)
                        ),
                        top=-8, right=-8,
                        width=24, height=24,
                    )
                ], clip_behavior=ft.ClipBehavior.NONE)
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

        if query:
            save_search_history(page, query) # Save to history
            
        input_field.value = ""
        
        # Extract image if any
        image_b64 = None
        remaining_files = []
        for f in attached_files:
            if f['type'] == 'image' and not image_b64:
                image_b64 = f['content']
            else:
                remaining_files.append(f['name'])

        # Add to memory with image data for the AI client
        msg_obj = {"role": "user", "content": query or "Analyze this image"}
        if image_b64:
            msg_obj["images"] = [image_b64]
        session_messages.append(msg_obj)

        # Build user display message
        display_msg = query
        if remaining_files:
            display_msg += ("\n\n" if display_msg else "") + "*Attached files:* " + ", ".join(remaining_files)
            
        chat_history.controls.append(_chat_bubble(display_msg, is_user=True, image_b64=image_b64)[0])

        typing_row, d1, d2, d3, pulse_fn, pulse_state = _typing_indicator()
        chat_history.controls.append(typing_row)
        page.update()
        threading.Thread(target=pulse_fn, daemon=True).start()

        def _get_ai_response():
            # Create bubble early for streaming
            ai_bubble_row, markdown_ref, text_ref = _chat_bubble("", is_user=False)
            
            markdown_control = markdown_ref.current
            text_control = text_ref.current
            
            attached_files.clear()
            update_attachment_ui()

            full_text = ""
            # BAZZLING FAST: Limit history to last 6 messages to keep context evaluation instant
            messages = session_messages[-6:].copy() if len(session_messages) > 6 else session_messages.copy()
            
            first_chunk_received = False
            
            try:
                # Dynamic Prompting based on Mode
                if mode_state["is_quick"]:
                    sys_prompt = "Career exam assistant. Max 3 bullet points. Each point < 15 words. No fluff. Bold key terms. If analyzing: Subject, Key Point, Significance only."
                else:
                    sys_prompt = "Professional career coach. Provide detailed, comprehensive explanations. Use clear headings and structured formatting. Be thorough but clear."

                for chunk in client.stream(messages, system_prompt=sys_prompt):
                    if not first_chunk_received:
                        # Success! First token arrived. Remove indicator and show bubble.
                        chat_history.controls.remove(typing_row)
                        chat_history.controls.append(ai_bubble_row)
                        pulse_state.running = False
                        first_chunk_received = True
                        page.update()

                    full_text += chunk
                    # Update plain text (DAZZLING FAST compared to Markdown)
                    text_control.value = full_text
                    text_control.update() 
                
                # STREAM FINISHED: Instantly swap to high-quality Markdown
                text_control.visible = False
                markdown_control.value = full_text
                markdown_control.visible = True
                markdown_control.update()
                
                # Add AI response to memory
                session_messages.append({"role": "assistant", "content": full_text})
                save_chat_log(page, session_messages) # Persist log
                
            except Exception as e:
                if not first_chunk_received:
                    chat_history.controls.remove(typing_row)
                    chat_history.controls.append(ai_bubble_container)
                text_control.value = f"Error: {str(e)}"
                text_control.update()

            pulse_state.running = False
            page.update()

        threading.Thread(target=_get_ai_response, daemon=True).start()
        page.update()

    def on_history_search(message):
        if message.get("type") == "history_search":
            query = message.get("query")
            input_field.value = query
            send_message(None, preset_query=query)

    page.pubsub.subscribe(on_history_search)

    # Quick Action Buttons
    def quick_action(label, query):
        return ft.Container(
            content=ft.Text(label, size=12, color="#ffffff", weight=ft.FontWeight.W_500),
            bgcolor="#14ffffff", # rgba(255,255,255,0.08)
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=24,
            border=ft.Border.all(1, "#26ffffff"), # rgba(255,255,255,0.15)
            on_click=lambda e: send_message(None, preset_query=query),
            on_hover=lambda e: setattr(e.control, 'bgcolor', "#21ffffff" if e.data == "true" else "#14ffffff") or setattr(e.control, 'offset', ft.Offset(0, -0.05) if e.data == "true" else ft.Offset(0,0)) or e.control.update(),
            animate=ft.Animation(200, ft.AnimationCurve.EASE),
            animate_offset=ft.Animation(200, ft.AnimationCurve.EASE),
            offset=ft.Offset(0,0),
        )

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME, color="#ffffff", size=20),
                    width=40, height=40, border_radius=20,
                    gradient=ft.LinearGradient(["#6366f1", "#a855f7"]),
                    alignment=ft.alignment.Alignment(0, 0),
                    tooltip="New Chat",
                    on_click=clear_chat,
                    on_hover=lambda e: (
                        setattr(e.control, 'scale', 1.15 if e.data == "true" else 1.0),
                        e.control.update()
                    ),
                    animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                ),
                ft.Column([
                    ft.Text("AI Career Copilot", size=20, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text("Your personal path to success", size=12, color=C.TEXT_55),
                ], spacing=2, expand=True),
                
                # Mode Toggle Buttons
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.BOLT, size=16, color="#ffffff" if mode_state["is_quick"] else "#ffffff40"),
                                ft.Text("Quick", size=13, weight=ft.FontWeight.BOLD, color="#ffffff" if mode_state["is_quick"] else "#ffffff40"),
                            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                            width=90, height=40, border_radius=10,
                            bgcolor="#33ffffff" if mode_state["is_quick"] else "transparent",
                            border=ft.Border.all(1, "#40ffffff") if mode_state["is_quick"] else None,
                            on_click=lambda _: set_mode(True),
                            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.BOOK_OUTLINED, size=16, color="#ffffff" if not mode_state["is_quick"] else "#ffffff40"),
                                ft.Text("Deep dive", size=13, weight=ft.FontWeight.BOLD, color="#ffffff" if not mode_state["is_quick"] else "#ffffff40"),
                            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                            width=110, height=40, border_radius=10,
                            bgcolor="#33ffffff" if not mode_state["is_quick"] else "transparent",
                            border=ft.Border.all(1, "#40ffffff") if not mode_state["is_quick"] else None,
                            on_click=lambda _: set_mode(False),
                            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                        ),
                    ], spacing=0),
                    bgcolor="#10ffffff",
                    padding=4,
                    border_radius=12,
                    border=ft.Border.all(1, "#10ffffff"),
                ),
                
                ft.Container(width=10),
                
                ft.TextButton(
                    "New Chat",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color="#ffffff40",
                    style=ft.ButtonStyle(color="#ffffff60"),
                    on_click=clear_chat,
                    tooltip="Start a fresh conversation"
                )
            ]),
            ft.Container(height=10),
            ft.Row([
                quick_action("📊 Analyze my path", "Based on my current skills and match %, what is my best next step?"),
                quick_action("📚 Study plan", "Create a focused study plan for my weakest skills."),
                quick_action("🎯 Next Milestone", "How can I better prepare for my upcoming milestone?"),
            ], wrap=True)
        ]),
        padding=24,
        bgcolor="#0fffffff", # rgba(255,255,255,0.06)
        blur=ft.Blur(24, 24, ft.BlurTileMode.MIRROR),
        border_radius=16,
        border=ft.Border.all(1, "#1affffff"),
        shadow=ft.BoxShadow(blur_radius=32, color="#4d000000", offset=ft.Offset(0, 8))
    )



    # Initial render of chat log if it exists
    if session_messages:
        for msg in session_messages:
            is_user = msg["role"] == "user"
            bubble, _, _ = _chat_bubble(msg["content"], is_user=is_user)
            chat_history.controls.append(bubble)

    return ft.Container(
        expand=True,
        padding=24,
        content=ft.Column([
            header,
            ft.Container(height=20),
            ft.Container(
                content=chat_history,
                expand=True,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                width=float("inf"),
                bgcolor="transparent", # Let background show through for glass effect
                padding=20,
            ),
            # ── Modern pill input bar ──────────────────────────────────────────
            footer_status := ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.BOLT, size=14, color="#ffffff60"),
                    ft.Text("Quick mode — concise, bullet-point answers", size=11, color="#ffffff60"),
                ], spacing=6),
                padding=ft.Padding(10, 0, 0, 8),
                visible=mode_state["is_quick"]
            ),
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=attachment_preview,
                        padding=ft.Padding(0, 5, 0, 10),
                    ),
                    ft.Row([
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
                        ft.Stack([
                            input_field,
                            waveform_container,
                        ], expand=True),
                        # Dedicated Paste Button (Fix for Win+V issues)
                        ft.IconButton(
                            icon=ft.Icons.PASTE_ROUNDED,
                            icon_color="#ffffff30",
                            icon_size=18,
                            tooltip="Paste",
                            on_click=do_paste
                        ),
                        # Voice Controls (X and ✓)
                        voice_controls,
                        # Main Mic/Send Button
                        send_btn_container
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                ], tight=True),
                bgcolor="#12ffffff", # rgba(255, 255, 255, 0.07)
                blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
                border_radius=24, # Reduced from 50 to look more like a card with attachments
                border=ft.Border.all(1, "#26ffffff"), # rgba(255, 255, 255, 0.15)
                shadow=ft.BoxShadow(
                    blur_radius=30, spread_radius=0,
                    color="#30000000", offset=ft.Offset(0, 8)
                ),
                padding=ft.Padding.only(left=20, right=8, top=12, bottom=8),
                margin=ft.Margin(top=12, bottom=0, left=0, right=0),
            )
        ], expand=True)
    )
