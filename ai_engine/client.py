import requests
import json
import time
from config import Config

class AIClient:
    def __init__(self):
        self.model = Config.AI_MODEL
        self.host = Config.AI_HOST
        
        if "/v1" in self.host:
            self.base_url = f"{self.host}/chat/completions"
        else:
            self.base_url = f"{self.host}/api/chat"

    def chat(self, messages, system_prompt=None, retries=2, timeout=30):
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
            
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.7
        }
        headers = {"Content-Type": "application/json"}
        
        for attempt in range(retries):
            try:
                response = requests.post(self.base_url, json=payload, headers=headers, timeout=timeout)
                response.raise_for_status()
                resp_json = response.json()
                if "choices" in resp_json:
                    return resp_json["choices"][0].get("message", {}).get("content", "")
                return resp_json.get("message", {}).get("content", "")
            except Exception as e:
                if attempt == retries - 1:
                    return f"Local AI Error: {str(e)}"
                time.sleep(1)
        return "Error: Maximum retries reached."

    def stream(self, messages, system_prompt=None):
        # Translate to Multi-modal format if it's OpenAI-compatible (LM Studio)
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        
        for m in messages:
            new_m = m.copy()
            if "images" in m and "/v1" in self.host:
                # OpenAI Multi-modal format
                text_content = m.get("content", "Analyze this image")
                content = [{"type": "text", "text": text_content}]
                for img_b64 in m["images"]:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    })
                new_m["content"] = content
                del new_m["images"]
            final_messages.append(new_m)

        payload = {
            "model": self.model,
            "messages": final_messages,
            "stream": True,
            "temperature": 0.0,
            "max_tokens": 300
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }

        try:
            # Short connect timeout, long read timeout for generation
            response = requests.post(self.base_url, json=payload, headers=headers, stream=True, timeout=(3, 60))
            response.raise_for_status()
            
            # Force UTF-8 to prevent "symbol replies" (broken characters)
            response.encoding = 'utf-8'
            
            for line in response.iter_lines(decode_unicode=False):
                if not line:
                    continue
                
                try:
                    line_str = line.decode('utf-8')
                except UnicodeDecodeError:
                    continue # Skip partially broken chunks
                
                # OpenAI / LM Studio format
                if line_str.startswith("data: "):
                    data_str = line_str[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        chunk = data["choices"][0]["delta"].get("content", "")
                        if chunk:
                            yield chunk
                    except:
                        continue
                # Standard Ollama format
                else:
                    try:
                        data = json.loads(line_str)
                        chunk = data.get("message", {}).get("content", "") or data.get("response", "")
                        if chunk:
                            yield chunk
                        if data.get("done"):
                            break
                    except:
                        continue
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "retries" in error_msg:
                yield "### ⚠️ AI Connection Error\n"
                yield f"I couldn't reach your AI server at `{self.host}`.\n\n"
                yield "**How to fix:**\n"
                yield "1. **LM Studio**: Open LM Studio, load a model, and start the Local Server (port 1234).\n"
                yield "2. **Ollama**: Ensure Ollama is running (`ollama serve` on port 11434).\n"
                yield "3. **Check .env**: Ensure `AI_HOST` matches your server's port.\n\n"
                yield "---\n*Entering **Demo Mode**: I will provide simulated responses so you can continue testing the UI.*"
                
                # Mock response generator
                time.sleep(1)
                mock_text = "\n\nBased on your profile, I recommend focusing on your Python skills. Since you are at 78%, you should aim for advanced concepts like Decorators and Generators to hit your next milestone!"
                for word in mock_text.split():
                    yield word + " "
                    time.sleep(0.05)
            else:
                yield f"\n\n**Error:** {error_msg}"

    def _get_sys_prompt(self, user_data):
        return (
            "You are a career exam assistant. Answer ONLY in short, exam-ready format:\n"
            "- Max 3 bullet points\n"
            "- Each point under 15 words\n"
            "- No fluff, no explanations unless asked\n"
            "- Use **bold** for key terms\n"
            "- If asked to analyze: give Subject, Key Point, Significance only"
        )

OllamaClient = AIClient

# Alias for backward compatibility
OllamaClient = AIClient
