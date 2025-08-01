import random

class ResearchAgent:
    def __init__(self):
        self.resource_templates = {
            "career": [
                {"title": "LinkedIn Profile Optimization Guide", "url": "https://www.linkedin.com/learning/"},
                {"title": "Resume Writing Best Practices", "url": "https://www.indeed.com/career-advice/resumes-cover-letters"},
                {"title": "Interview Preparation Tips", "url": "https://www.glassdoor.com/blog/interview-questions/"},
                {"title": "Networking Strategies", "url": "https://www.forbes.com/sites/networking/"},
                {"title": "Job Search Techniques", "url": "https://www.monster.com/career-advice/"}
            ],
            "health": [
                {"title": "Fitness Fundamentals", "url": "https://www.acefitness.org/education-and-resources/"},
                {"title": "Nutrition Basics", "url": "https://www.nutrition.gov/"},
                {"title": "Workout Routines", "url": "https://www.bodybuilding.com/workouts/"},
                {"title": "Mental Health Resources", "url": "https://www.nami.org/help"},
                {"title": "Sleep Optimization", "url": "https://www.sleepfoundation.org/"}
            ],
            "learning": [
                {"title": "Online Learning Platforms", "url": "https://www.coursera.org/"},
                {"title": "Skill Development Resources", "url": "https://www.skillshare.com/"},
                {"title": "Study Techniques", "url": "https://www.khanacademy.org/"},
                {"title": "Programming Tutorials", "url": "https://www.freecodecamp.org/"},
                {"title": "Language Learning Apps", "url": "https://www.duolingo.com/"}
            ],
            "personal": [
                {"title": "Goal Setting Framework", "url": "https://www.mindtools.com/pages/main/newMN_HTE.htm"},
                {"title": "Time Management Tips", "url": "https://www.mindtools.com/pages/main/newMN_HTE.htm"},
                {"title": "Productivity Hacks", "url": "https://www.lifehack.org/"},
                {"title": "Mindfulness Practices", "url": "https://www.headspace.com/"},
                {"title": "Personal Development Books", "url": "https://www.goodreads.com/shelf/show/personal-development"}
            ],
            "financial": [
                {"title": "Budgeting Basics", "url": "https://www.mint.com/"},
                {"title": "Investment Guide", "url": "https://www.investopedia.com/"},
                {"title": "Saving Strategies", "url": "https://www.nerdwallet.com/"},
                {"title": "Financial Planning", "url": "https://www.financialplanningassociation.org/"},
                {"title": "Debt Management", "url": "https://www.debt.org/"}
            ],
            "relationships": [
                {"title": "Communication Skills", "url": "https://www.psychologytoday.com/us/topics/communication"},
                {"title": "Conflict Resolution", "url": "https://www.helpguide.org/articles/relationships-communication/"},
                {"title": "Building Trust", "url": "https://www.mindtools.com/pages/article/building-trust.htm"},
                {"title": "Active Listening", "url": "https://www.skillsyouneed.com/ips/active-listening.html"},
                {"title": "Relationship Advice", "url": "https://www.gottman.com/"}
            ]
        }

    def _get_task_category(self, task_description, goal_category):
        """Determine the most relevant category for resource selection"""
        task_lower = task_description.lower()
        
        # If we have a specific goal category, use it
        if goal_category and goal_category.lower() in self.resource_templates:
            return goal_category.lower()
        
        # Otherwise, try to infer from task description
        if any(word in task_lower for word in ["job", "career", "resume", "interview", "internship"]):
            return "career"
        elif any(word in task_lower for word in ["exercise", "workout", "fitness", "health", "diet"]):
            return "health"
        elif any(word in task_lower for word in ["learn", "study", "course", "skill", "programming"]):
            return "learning"
        elif any(word in task_lower for word in ["budget", "money", "invest", "save", "financial"]):
            return "financial"
        elif any(word in task_lower for word in ["relationship", "communication", "friend", "family"]):
            return "relationships"
        else:
            return "personal"

    def enrich(self, plan: dict) -> dict:
        """Add relevant resources to each task based on its content and goal category"""
        goal_category = plan.get('metadata', {}).get('category', 'Personal')
        
        for week in plan.get("weeks", []):
            for task in week.get("tasks", []):
                category = self._get_task_category(task['task'], goal_category)
                available_resources = self.resource_templates.get(category, self.resource_templates["personal"])
                
                # Select 1-3 random resources for each task
                num_resources = random.randint(1, 3)
                selected_resources = random.sample(available_resources, min(num_resources, len(available_resources)))
                
                task["resources"] = selected_resources
                
                # Add some additional helpful metadata
                task["resource_category"] = category
                task["helpful_tip"] = self._get_helpful_tip(category)
                
        return plan
    
    def _get_helpful_tip(self, category):
        """Provide a helpful tip based on the task category"""
        tips = {
            "career": "💡 Pro tip: Network with professionals in your field on LinkedIn",
            "health": "💡 Pro tip: Start with small, sustainable changes for lasting results",
            "learning": "💡 Pro tip: Use the Pomodoro technique for focused study sessions",
            "personal": "💡 Pro tip: Break big goals into smaller, manageable tasks",
            "financial": "💡 Pro tip: Track your expenses to identify spending patterns",
            "relationships": "💡 Pro tip: Practice active listening to improve communication"
        }
        return tips.get(category, "💡 Pro tip: Consistency is key to achieving your goals")