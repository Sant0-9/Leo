import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from .planner_agent import PlannerAgent
from .scheduler_agent import SchedulerAgent
from .research_agent import ResearchAgent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class GoalFlow:
    def __init__(self, ai_model: str = "GPT-3.5 Turbo"):
        self.ai_model = ai_model
        self.planner_agent = PlannerAgent(OPENAI_API_KEY, ai_model)
        self.scheduler_agent = SchedulerAgent()
        self.research_agent = ResearchAgent()
    
    def generate_plan_from_context(self, goal_context: Dict) -> Dict:
        """Generate a complete plan from collected goal context"""
        try:
            # Create enhanced prompt based on collected information
            enhanced_prompt = self._create_enhanced_prompt(goal_context)
            
            # Map friendly model names to actual API model names
            model_mapping = {
                "GPT-3.5 Turbo": "gpt-3.5-turbo",
                "GPT-4": "gpt-4",
                "GPT-4 Turbo": "gpt-4-turbo-preview",
                "Claude-3": "gpt-4"  # Fallback to GPT-4 for Claude-3 for now
            }
            
            actual_model = model_mapping.get(self.ai_model, "gpt-3.5-turbo")
            
            # Generate plan using PlannerAgent
            response = self.planner_agent.client.chat.completions.create(
                model=actual_model,
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": goal_context.get("goal", "")}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            # Safely parse the response without using eval()
            import json
            try:
                plan = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback plan if parsing fails
                plan = self._create_fallback_plan(goal_context)
            
            # Enhance plan with scheduling and resources
            plan = self.scheduler_agent.schedule(plan)
            plan = self.research_agent.enrich(plan)
            
            # Add metadata
            plan['metadata'] = {
                'goal': goal_context.get("goal", ""),
                'timeline': goal_context.get("timeline", "medium_term"),
                'seriousness': goal_context.get("seriousness", "medium"),
                'reminders': goal_context.get("reminders", "weekly"),
                'created_at': datetime.now().isoformat(),
                'ai_model': self.ai_model
            }
            
            return plan
            
        except Exception as e:
            # Return error plan
            return self._create_error_plan(goal_context, str(e))
    
    def _create_enhanced_prompt(self, goal_context: Dict) -> str:
        """Create an enhanced prompt based on collected goal context"""
        goal = goal_context.get("goal", "")
        timeline = goal_context.get("timeline", "medium_term")
        seriousness = goal_context.get("seriousness", "medium")
        reminders = goal_context.get("reminders", "weekly")
        
        # Map timeline to specific timeframes
        timeline_mapping = {
            "short_term": "2-4 weeks",
            "medium_term": "1-3 months", 
            "long_term": "3-6 months"
        }
        
        timeframe = timeline_mapping.get(timeline, "1-3 months")
        
        # Adjust plan complexity based on seriousness
        complexity = {
            "low": "simple, easy-to-follow steps",
            "medium": "balanced approach with moderate complexity",
            "high": "comprehensive, detailed plan with advanced strategies"
        }.get(seriousness, "balanced approach")
        
        # Adjust reminder frequency
        reminder_text = {
            "daily": "daily check-ins and progress tracking",
            "weekly": "weekly progress reviews and adjustments"
        }.get(reminders, "weekly progress reviews")
        
        enhanced_prompt = f"""
        Create a detailed, personalized plan for this goal: "{goal}"
        
        Context:
        - Timeline: {timeframe}
        - Commitment Level: {seriousness.title()}
        - Reminder Preference: {reminder_text}
        - Plan Complexity: {complexity}
        
        Please create a plan that:
        1. Fits the {timeframe} timeline
        2. Matches the {seriousness} commitment level
        3. Provides {complexity}
        4. Includes {reminder_text}
        5. Breaks down into weekly and daily actionable tasks
        6. Is realistic and achievable for the user's commitment level
        
        Return a Python dict with this structure:
        {{'weeks': [{{'week': 1, 'tasks': [{{'day': 'Monday', 'task': '...'}}, ...]}}, ...]}}
        
        Make sure the plan is appropriate for a {seriousness} commitment level and {timeframe} timeline.
        """
        
        return enhanced_prompt
    
    def _create_fallback_plan(self, goal_context: Dict) -> Dict:
        """Create a fallback plan if AI generation fails"""
        goal = goal_context.get("goal", "your goal")
        timeline = goal_context.get("timeline", "medium_term")
        
        # Simple fallback plan
        if timeline == "short_term":
            weeks = 2
        elif timeline == "long_term":
            weeks = 6
        else:
            weeks = 4
        
        plan = {"weeks": []}
        
        for week_num in range(1, weeks + 1):
            week_tasks = []
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for day in days:
                if week_num == 1 and day == "Monday":
                    task = f"Start working on: {goal}"
                elif week_num == weeks and day == "Sunday":
                    task = f"Review progress and plan next steps for: {goal}"
                else:
                    task = f"Continue working on: {goal}"
                
                week_tasks.append({"day": day, "task": task})
            
            plan["weeks"].append({"week": week_num, "tasks": week_tasks})
        
        return plan
    
    def _create_error_plan(self, goal_context: Dict, error_message: str) -> Dict:
        """Create an error plan when generation fails"""
        goal = goal_context.get("goal", "your goal")
        
        return {
            "weeks": [
                {
                    "week": 1,
                    "tasks": [
                        {"day": "Monday", "task": f"Start working on: {goal}"},
                        {"day": "Tuesday", "task": f"Continue working on: {goal}"},
                        {"day": "Wednesday", "task": f"Make progress on: {goal}"},
                        {"day": "Thursday", "task": f"Keep working on: {goal}"},
                        {"day": "Friday", "task": f"Review progress on: {goal}"}
                    ]
                }
            ],
            "metadata": {
                "goal": goal,
                "error": error_message,
                "created_at": datetime.now().isoformat(),
                "note": "This is a simplified plan due to an error in generation."
            }
        }
    
    def get_plan_summary(self, plan: Dict) -> str:
        """Generate a human-readable summary of the plan"""
        if not plan or "weeks" not in plan:
            return "No plan available."
        
        total_weeks = len(plan["weeks"])
        total_tasks = sum(len(week.get("tasks", [])) for week in plan["weeks"])
        
        metadata = plan.get("metadata", {})
        goal = metadata.get("goal", "your goal")
        timeline = metadata.get("timeline", "medium_term")
        seriousness = metadata.get("seriousness", "medium")
        
        summary = f"""
## 📋 Your Personalized Plan

**Goal:** {goal}
**Timeline:** {total_weeks} weeks
**Total Tasks:** {total_tasks} tasks
**Commitment Level:** {seriousness.title()}

### What's included:
✅ Weekly breakdown with daily tasks
✅ Time scheduling for each task
✅ Priority levels and energy requirements
✅ Helpful resources and links
✅ Progress tracking recommendations

Ready to get started with your plan!
        """
        
        return summary.strip()
    
    def validate_goal_context(self, goal_context: Dict) -> Dict:
        """Validate and clean goal context data"""
        validated = {}
        
        # Validate goal
        goal = goal_context.get("goal", "").strip()
        if goal:
            validated["goal"] = goal
        else:
            validated["goal"] = "Improve productivity"
        
        # Validate timeline
        timeline = goal_context.get("timeline", "medium_term")
        if timeline in ["short_term", "medium_term", "long_term"]:
            validated["timeline"] = timeline
        else:
            validated["timeline"] = "medium_term"
        
        # Validate seriousness
        seriousness = goal_context.get("seriousness", "medium")
        if seriousness in ["low", "medium", "high"]:
            validated["seriousness"] = seriousness
        else:
            validated["seriousness"] = "medium"
        
        # Validate reminders
        reminders = goal_context.get("reminders", "weekly")
        if reminders in ["daily", "weekly"]:
            validated["reminders"] = reminders
        else:
            validated["reminders"] = "weekly"
        
        return validated 