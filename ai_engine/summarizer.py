import json
from .client import OllamaClient

class DocumentSummarizer:
    def __init__(self):
        self.client = OllamaClient()

    def summarize_and_quiz(self, raw_text):
        system_prompt = (
            "You are a study assistant. Analyze the provided text. "
            "1. Provide a concise summary.\n"
            "2. List 5 key takeaway points.\n"
            "3. Generate 5 multiple-choice questions (MCQs) with answers.\n"
            "Format your response as a JSON-like structure (but as plain text) "
            "with sections: [SUMMARY], [KEY_POINTS], [QUIZ]."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text to analyze:\n{raw_text[:4000]}"} # Limit context for speed
        ]
        
        return self.client.chat(messages)
