from .client import OllamaClient

class StudyPlanner:
    def __init__(self):
        self.client = OllamaClient()

    def generate_schedule(self, tasks, pace="balanced"):
        task_list = "\n".join([f"- {t['title']} (Due: {t['due_date']}, Priority: {t['priority']})" for t in tasks])
        
        system_prompt = (
            "You are an expert academic advisor. Create a realistic, high-performance study schedule. "
            "Prioritize tasks by deadline and importance. Use a balanced pace. "
            "Output the plan in a clear, day-by-day markdown format."
        )
        
        user_prompt = f"Tasks to schedule:\n{task_list}\nPace: {pace}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.client.chat(messages)
