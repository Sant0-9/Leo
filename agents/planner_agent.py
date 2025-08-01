from openai import OpenAI
from utils.prompts import PLANNER_PROMPT

class PlannerAgent:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def plan(self, goal: str) -> dict:
        # Map friendly model names to actual API model names
        model_mapping = {
            "GPT-3.5 Turbo": "gpt-3.5-turbo",
            "GPT-4": "gpt-4",
            "GPT-4 Turbo": "gpt-4-turbo-preview",
            "Claude-3": "gpt-4"  # Fallback to GPT-4 for Claude-3 for now
        }
        
        actual_model = model_mapping.get(self.model, "gpt-3.5-turbo")
        
        try:
            response = self.client.chat.completions.create(
                model=actual_model,
                messages=[
                    {"role": "system", "content": PLANNER_PROMPT},
                    {"role": "user", "content": goal}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Safely parse the response without using eval()
            import json
            try:
                plan = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback to a safe default plan
                plan = {
                    "weeks": [
                        {
                            "week": 1,
                            "tasks": [
                                {"day": "Monday", "task": "Start working on your goal"},
                                {"day": "Tuesday", "task": "Continue progress"},
                                {"day": "Wednesday", "task": "Review and adjust"},
                                {"day": "Thursday", "task": "Deep work session"},
                                {"day": "Friday", "task": "Weekly review and planning"}
                            ]
                        }
                    ]
                }
            
            return plan
            
        except Exception as e:
            # Return a safe fallback plan if API call fails
            return {
                "weeks": [
                    {
                        "week": 1,
                        "tasks": [
                            {"day": "Monday", "task": "Start working on your goal"},
                            {"day": "Tuesday", "task": "Continue progress"},
                            {"day": "Wednesday", "task": "Review and adjust"},
                            {"day": "Thursday", "task": "Deep work session"},
                            {"day": "Friday", "task": "Weekly review and planning"}
                        ]
                    }
                ]
            }
