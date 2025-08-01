class ReminderAgent:
    def summarize(self, today_tasks: list) -> str:
        if not today_tasks:
            return "No tasks for today! Take a break or plan something awesome."
        tasks_str = ", ".join([t['task'] for t in today_tasks])
        return f"Today's plan: {tasks_str}. Let's crush it! 🚀"
    
    def add_reminders(self, plan: dict) -> dict:
        """Add reminder logic to the plan"""
        if 'weeks' not in plan:
            return plan
        
        for week in plan['weeks']:
            if 'tasks' in week:
                for task in week['tasks']:
                    # Add reminder information to each task
                    task['reminder'] = {
                        'enabled': True,
                        'time': '09:00',  # Default reminder time
                        'frequency': 'daily',
                        'message': f"Time to work on: {task.get('task', 'your task')}"
                    }
        
        # Add reminder settings to plan metadata
        if 'metadata' not in plan:
            plan['metadata'] = {}
        
        plan['metadata']['reminders'] = {
            'enabled': True,
            'default_time': '09:00',
            'frequency': 'daily',
            'notification_type': 'in_app'
        }
        
        return plan
