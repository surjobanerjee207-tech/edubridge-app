from .client import OllamaClient

class WellbeingAdvisor:
    def __init__(self):
        self.client = OllamaClient()

    def get_suggestion(self, mood_score, note):
        mood_map = {1: "Very Low", 2: "Low", 3: "Neutral", 4: "Good", 5: "Excellent"}
        mood_str = mood_map.get(mood_score, "Neutral")
        
        system_prompt = (
            "You are a supportive counselor. Provide a short, empathetic wellbeing tip based on the user's mood. "
            "If the mood is low, suggest grounding exercises or local support. "
            "Always include the disclaimer: 'This is not medical advice.'"
        )
        
        user_prompt = f"User Mood: {mood_str}\nJournal Note: {note}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.client.chat(messages)
