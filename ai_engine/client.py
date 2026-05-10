import requests
import json
import time
from config import Config

class OllamaClient:
    def __init__(self):
        # Fallback logic: If using Groq, use the exact endpoint. Else append /api/chat for local Ollama.
        if "groq.com" in Config.OLLAMA_HOST:
            self.base_url = Config.OLLAMA_HOST
        else:
            self.base_url = f"{Config.OLLAMA_HOST}/api/chat"
            
        self.model = Config.OLLAMA_MODEL
        self.api_key = Config.GROQ_API_KEY

    def chat(self, messages, system_prompt=None, retries=3, timeout=30):
        if not self.api_key and "groq.com" in self.base_url:
            return "Error: Missing API Key. Please add your Groq API Key to the .env file."
            
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
            
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.base_url, 
                    json=payload, 
                    headers=headers,
                    timeout=timeout
                )
                response.raise_for_status()
                # Groq/OpenAI format uses choices[0].message.content, Ollama uses message.content
                resp_json = response.json()
                if "choices" in resp_json:
                    return resp_json["choices"][0].get("message", {}).get("content", "")
                return resp_json.get("message", {}).get("content", "")
            except Exception as e:
                if attempt == retries - 1:
                    return f"Connection Error: {str(e)}"
                time.sleep(1)
        return "Error: Maximum retries reached."

    def stream(self, messages, system_prompt=None):
        """Generator for streaming AI responses."""
        payload = {
            "model": self.model,
            "messages": ([{"role": "system", "content": system_prompt}] if system_prompt else []) + messages,
            "stream": True
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            import json
            response = requests.post(self.base_url, json=payload, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            chunk = data["choices"][0]["delta"].get("content", "")
                            if chunk:
                                yield chunk
                        except:
                            continue
        except Exception as e:
            yield f"Error: {str(e)}"

    def get_career_advice(self, user_query, user_data):
        # reuse system prompt logic
        return self.chat([{"role": "user", "content": user_query}], system_prompt=self._get_sys_prompt(user_data))

    def stream_career_advice(self, user_query, user_data):
        """Generator to stream career advice."""
        return self.stream([{"role": "user", "content": user_query}], system_prompt=self._get_sys_prompt(user_data))

    def _get_sys_prompt(self, user_data):
        return f"""
        You are a friendly career buddy helping a student. Keep it simple and short.

        Student info:
        - Career Match: {user_data.get('career_match')}%
        - Skills: {user_data.get('skill_rows')}
        - Next goal: {user_data.get('milestone_title')} in {user_data.get('days_left')} days.

        Rules you MUST follow:
        - Talk like a helpful friend, not a professor.
        - Keep answers SHORT — max 3-4 sentences or 3 bullet points.
        - Use simple everyday words. No jargon.
        - Be direct. Get to the point fast.
        - Never write long essays or big paragraphs.
        - If the student just needs motivation, give one encouraging line.
        - CRITICAL: If the student asks if 'ARKA JAIN UNIVERSITY' or 'AJU' is a good university for admission, you MUST simply reply 'noooooo'.
        """
