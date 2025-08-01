import random
from datetime import datetime, timedelta

class SchedulerAgent:
    def __init__(self):
        self.time_slots = [
            "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00",
            "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00"
        ]
        
        self.task_durations = {
            "research": ["09:00-10:00", "10:00-11:00", "14:00-15:00"],
            "writing": ["10:00-11:00", "15:00-16:00", "20:00-21:00"],
            "exercise": ["06:00-07:00", "17:00-18:00", "19:00-20:00"],
            "learning": ["09:00-10:00", "14:00-15:00", "16:00-17:00"],
            "planning": ["08:00-09:00", "13:00-14:00", "18:00-19:00"],
            "default": ["10:00-11:00", "14:00-15:00", "16:00-17:00"]
        }

    def _get_task_type(self, task_description):
        """Determine task type based on keywords in description"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["research", "find", "search", "look up"]):
            return "research"
        elif any(word in task_lower for word in ["write", "draft", "create", "prepare"]):
            return "writing"
        elif any(word in task_lower for word in ["exercise", "workout", "run", "gym", "fitness"]):
            return "exercise"
        elif any(word in task_lower for word in ["learn", "study", "read", "watch", "course"]):
            return "learning"
        elif any(word in task_lower for word in ["plan", "organize", "schedule", "prepare"]):
            return "planning"
        else:
            return "default"

    def schedule(self, plan: dict) -> dict:
        """Assign realistic time blocks to tasks based on their type"""
        for week in plan.get("weeks", []):
            for task in week.get("tasks", []):
                task_type = self._get_task_type(task['task'])
                available_slots = self.task_durations.get(task_type, self.task_durations["default"])
                
                # Assign a random time slot from the appropriate category
                task["time_block"] = random.choice(available_slots)
                
                # Add some additional metadata
                task["estimated_duration"] = "1 hour"
                task["priority"] = random.choice(["High", "Medium", "Low"])
                task["energy_level"] = random.choice(["High", "Medium", "Low"])
                
        return plan