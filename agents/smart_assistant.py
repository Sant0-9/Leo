#!/usr/bin/env python3
"""
SmartAssistant - Interactive Goal Planning System
Handles natural conversation flow and agent integration
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv
from .planner_agent import PlannerAgent
from .scheduler_agent import SchedulerAgent
from .research_agent import ResearchAgent
from .reminder_agent import ReminderAgent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AssistantState(Enum):
    GREETING = "greeting"
    AWAITING_INTENT = "awaiting_intent"
    CLARIFYING_GOAL = "clarifying_goal"
    AWAITING_TIMEFRAME = "awaiting_timeframe"
    AWAITING_FEATURES = "awaiting_features"
    CREATING_SMART_GOAL = "creating_smart_goal"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    GENERATING_PLAN = "generating_plan"
    CASUAL_CHAT = "casual_chat"

class SmartAssistant:
    def __init__(self, ai_model: str = "GPT-3.5 Turbo"):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.ai_model = ai_model
        
        # Map friendly model names to actual API model names
        self.model_mapping = {
            "GPT-3.5 Turbo": "gpt-3.5-turbo",
            "GPT-4": "gpt-4",
            "GPT-4 Turbo": "gpt-4-turbo-preview",
        }
        
        # Initialize agents
        self.planner_agent = PlannerAgent(OPENAI_API_KEY, ai_model)
        self.scheduler_agent = SchedulerAgent()
        self.research_agent = ResearchAgent()
        self.reminder_agent = ReminderAgent()
        
        # Conversation state
        self.current_state = AssistantState.GREETING
        self.chat_history = []
        
        # Goal data
        self.goal_data = {
            "raw_goal": "",
            "timeframe": "",
            "features": [],
            "smart_goal": "",
            "confirmed": False
        }
        
        # Response templates
        self.response_templates = {
            "greeting": [
                "Hi! I'm here to help you with anything — productivity tips, goals, or just to chat. What would you like to work on today?",
                "Hello! I'm your productivity assistant. I can help you create goals, plan your time, or just chat. What's on your mind?",
                "Hey there! Ready to crush some goals or just explore productivity tips? What would you like to work on?"
            ],
            "clarifying": [
                "What are you aiming to achieve with that?",
                "Would you like to create a goal for this?",
                "Tell me more about what you want to accomplish."
            ],
            "goal_mentioned": [
                "Awesome! Let's build a personalized plan.",
                "Great goal! I can help you create a structured plan for that.",
                "Perfect! Let's turn that into an actionable plan."
            ],
            "timeframe_question": [
                "Do you want this to be a 7-day, 30-day, or 6-month plan?",
                "What's your timeline — quick sprint (7 days), focused month (30 days), or longer journey (6 months)?",
                "How long do you want to work on this — 7 days, 30 days, or 6 months?"
            ],
            "features_question": [
                "Do you want reminders, research support, or scheduling help with this?",
                "What would help you most — daily reminders, research resources, or calendar scheduling?",
                "Would you like reminders, research tips, or help scheduling this into your calendar?"
            ],
            "smart_goal_created": [
                "Perfect! Here's your SMART goal:",
                "Great! I've created a SMART goal for you:",
                "Excellent! Here's your structured goal:"
            ],
            "confirmation_question": [
                "Would you like to save this goal and let our agents build a full plan for you with 1 click?",
                "Ready to create a detailed plan with tasks, schedule, and resources?",
                "Should I generate a complete action plan with timeline and reminders?"
            ]
        }
    
    def handle_message(self, user_message: str) -> str:
        """Main entry point for handling user messages"""
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now()
        })
        
        # Generate response based on current state
        response = self._generate_response(user_message)
        
        # Add response to history
        self.chat_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return response
    
    def _generate_response(self, user_message: str) -> str:
        """Generate response based on current state"""
        user_lower = user_message.lower()
        
        # Handle state transitions
        if self.current_state == AssistantState.GREETING:
            return self._handle_greeting(user_message)
        
        elif self.current_state == AssistantState.AWAITING_INTENT:
            return self._handle_intent_detection(user_message)
        
        elif self.current_state == AssistantState.CLARIFYING_GOAL:
            return self._handle_goal_clarification(user_message)
        
        elif self.current_state == AssistantState.AWAITING_TIMEFRAME:
            return self._handle_timeframe_input(user_message)
        
        elif self.current_state == AssistantState.AWAITING_FEATURES:
            return self._handle_features_input(user_message)
        
        elif self.current_state == AssistantState.CREATING_SMART_GOAL:
            return self._handle_smart_goal_creation(user_message)
        
        elif self.current_state == AssistantState.AWAITING_CONFIRMATION:
            return self._handle_confirmation_input(user_message)
        
        elif self.current_state == AssistantState.GENERATING_PLAN:
            return self._handle_plan_generation(user_message)
        
        elif self.current_state == AssistantState.CASUAL_CHAT:
            return self._handle_casual_chat(user_message)
        
        else:
            # Default to casual chat
            self.current_state = AssistantState.CASUAL_CHAT
            return self._handle_casual_chat(user_message)
    
    def _handle_greeting(self, user_message: str) -> str:
        """Handle initial greeting"""
        user_lower = user_message.lower()
        
        # Check for greetings
        if any(word in user_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            self.current_state = AssistantState.AWAITING_INTENT
            return self._get_random_response("greeting")
        
        # Check for help requests
        elif any(word in user_lower for word in ["help", "can you help", "assist"]):
            self.current_state = AssistantState.AWAITING_INTENT
            return self._get_random_response("greeting")
        
        # Check for broad topics
        elif any(word in user_lower for word in ["gym", "study", "job", "work", "learn", "exercise", "diet"]):
            self.current_state = AssistantState.CLARIFYING_GOAL
            self.goal_data["raw_goal"] = user_message
            return self._get_random_response("clarifying")
        
        # Check for specific goals
        elif any(word in user_lower for word in ["lose weight", "get a job", "learn dsa", "learn python", "get fit", "study", "workout"]):
            self.current_state = AssistantState.AWAITING_TIMEFRAME
            self.goal_data["raw_goal"] = user_message
            return self._get_random_response("goal_mentioned") + "\n\n" + self._get_random_response("timeframe_question")
        
        else:
            self.current_state = AssistantState.AWAITING_INTENT
            return self._get_random_response("greeting")
    
    def _handle_intent_detection(self, user_message: str) -> str:
        """Handle intent detection"""
        user_lower = user_message.lower()
        
        # Check for goal-related responses
        if any(word in user_lower for word in ["goal", "plan", "achieve", "work on", "create", "build"]):
            self.current_state = AssistantState.CLARIFYING_GOAL
            return self._get_random_response("clarifying")
        
        # Check for specific goals
        elif any(word in user_lower for word in ["lose weight", "get a job", "learn dsa", "learn python", "get fit", "study", "workout", "learn machine learning", "internship", "intern"]):
            self.current_state = AssistantState.AWAITING_TIMEFRAME
            self.goal_data["raw_goal"] = user_message
            return self._get_random_response("goal_mentioned") + "\n\n" + self._get_random_response("timeframe_question")
        
        # Check for learning-related keywords
        elif any(word in user_lower for word in ["learn", "study", "master", "understand", "practice"]):
            self.current_state = AssistantState.AWAITING_TIMEFRAME
            self.goal_data["raw_goal"] = user_message
            return self._get_random_response("goal_mentioned") + "\n\n" + self._get_random_response("timeframe_question")
        
        else:
            self.current_state = AssistantState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
    
    def _handle_goal_clarification(self, user_message: str) -> str:
        """Handle goal clarification"""
        self.goal_data["raw_goal"] = user_message
        self.current_state = AssistantState.AWAITING_TIMEFRAME
        return self._get_random_response("goal_mentioned") + "\n\n" + self._get_random_response("timeframe_question")
    
    def _handle_timeframe_input(self, user_message: str) -> str:
        """Handle timeframe input"""
        user_lower = user_message.lower()
        
        # Extract timeframe
        if any(word in user_lower for word in ["7 day", "7 days", "week", "1 week"]):
            self.goal_data["timeframe"] = "7_days"
        elif any(word in user_lower for word in ["30 day", "30 days", "month", "1 month"]):
            self.goal_data["timeframe"] = "30_days"
        elif any(word in user_lower for word in ["6 month", "6 months", "half year"]):
            self.goal_data["timeframe"] = "6_months"
        else:
            self.goal_data["timeframe"] = "30_days"  # Default to 30 days
        
        self.current_state = AssistantState.AWAITING_FEATURES
        return self._get_random_response("features_question")
    
    def _handle_features_input(self, user_message: str) -> str:
        """Handle features input"""
        user_lower = user_message.lower()
        
        # Extract features
        features = []
        if any(word in user_lower for word in ["reminder", "reminders", "notify"]):
            features.append("reminders")
        if any(word in user_lower for word in ["research", "resources", "tips", "help"]):
            features.append("research")
        if any(word in user_lower for word in ["schedule", "calendar", "timeline"]):
            features.append("scheduling")
        
        # Handle "all features" or "all"
        if any(word in user_lower for word in ["all", "everything", "all features"]):
            features = ["reminders", "research", "scheduling"]
        
        # If no specific features mentioned, include all
        if not features:
            features = ["reminders", "research", "scheduling"]
        
        self.goal_data["features"] = features
        self.current_state = AssistantState.CREATING_SMART_GOAL
        return self._create_smart_goal()
    
    def _handle_smart_goal_creation(self, user_message: str) -> str:
        """Handle smart goal creation"""
        self.current_state = AssistantState.AWAITING_CONFIRMATION
        return self._get_random_response("confirmation_question")
    
    def _handle_confirmation_input(self, user_message: str) -> str:
        """Handle confirmation input"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["yes", "sure", "okay", "create", "generate", "plan", "ready", "go"]):
            self.goal_data["confirmed"] = True
            self.current_state = AssistantState.GENERATING_PLAN
            return self._generate_complete_plan()
        else:
            # Reset to ask more questions
            self.current_state = AssistantState.CLARIFYING_GOAL
            return "No problem! Let me ask you a few more questions to better understand your goal."
    
    def _handle_plan_generation(self, user_message: str) -> str:
        """Handle plan generation state"""
        return "Perfect! Your plan has been generated and is ready to view. You can find it in the 'Current Plan' section."
    
    def _handle_casual_chat(self, user_message: str) -> str:
        """Handle casual chat"""
        return self._generate_ai_response(user_message, "casual_chat")
    
    def _create_smart_goal(self) -> str:
        """Create a SMART goal from collected data"""
        goal = self.goal_data["raw_goal"]
        timeframe = self.goal_data["timeframe"]
        
        # Convert timeframe to readable text
        timeframe_text = {
            "7_days": "7 days",
            "30_days": "30 days",
            "6_months": "6 months"
        }.get(timeframe, "30 days")
        
        # Create SMART goal based on the type of goal
        if any(word in goal.lower() for word in ["lose weight", "get fit", "exercise", "workout", "fitness"]):
            smart_goal = f"I will improve my fitness in {timeframe_text} by exercising 4 times per week and maintaining a healthy diet."
        elif any(word in goal.lower() for word in ["learn", "study", "dsa", "python", "programming"]):
            # Extract the actual learning goal
            if "learn" in goal.lower():
                learning_target = goal.lower().replace("learn", "").replace("i want to", "").strip()
                smart_goal = f"I will learn {learning_target} in {timeframe_text} by dedicating 2 hours daily to practice and study."
            else:
                smart_goal = f"I will learn {goal} in {timeframe_text} by dedicating 2 hours daily to practice and study."
        elif any(word in goal.lower() for word in ["job", "career", "intern", "employment"]):
            smart_goal = f"I will secure a job in {timeframe_text} by networking, improving my skills, and applying to relevant positions."
        else:
            smart_goal = f"I will achieve {goal} in {timeframe_text} by creating a structured plan and working consistently toward this goal."
        
        self.goal_data["smart_goal"] = smart_goal
        
        return self._get_random_response("smart_goal_created") + f"\n\n**{smart_goal}**\n\n" + self._get_random_response("confirmation_question")
    
    def _generate_complete_plan(self) -> str:
        """Generate a complete plan using all agents"""
        try:
            # Create goal context for agents
            goal_context = {
                "goal": self.goal_data["smart_goal"],
                "raw_goal": self.goal_data["raw_goal"],
                "timeline": self.goal_data["timeframe"],
                "features": self.goal_data["features"],
                "seriousness": "high",
                "reminders": "daily" if "reminders" in self.goal_data["features"] else "weekly"
            }
            
            # Generate plan using PlannerAgent
            plan = self.planner_agent.plan(self.goal_data["smart_goal"])
            
            # Enhance with scheduling if requested
            if "scheduling" in self.goal_data["features"]:
                plan = self.scheduler_agent.schedule(plan)
            
            # Enhance with research if requested
            if "research" in self.goal_data["features"]:
                plan = self.research_agent.enrich(plan)
            
            # Add reminders if requested
            if "reminders" in self.goal_data["features"]:
                plan = self.reminder_agent.add_reminders(plan)
            
            # Add metadata
            plan['metadata'] = {
                'goal': self.goal_data["smart_goal"],
                'raw_goal': self.goal_data["raw_goal"],
                'timeline': self.goal_data["timeframe"],
                'features': self.goal_data["features"],
                'created_at': datetime.now().isoformat(),
                'ai_model': self.ai_model
            }
            
            # Store plan in assistant for UI to access
            self._last_generated_plan = plan
            
            return f"""🎉 **Plan Generated Successfully!**

Your personalized plan for **"{self.goal_data['raw_goal']}"** is ready!

**SMART Goal:** {self.goal_data['smart_goal']}
**Timeline:** {self.goal_data['timeframe']}
**Features:** {', '.join(self.goal_data['features'])}

You can view your complete plan in the 'Current Plan' section with:
✅ Structured tasks and timeline
✅ Calendar scheduling
✅ Research resources
✅ Reminder system

What would you like to work on next?"""
            
        except Exception as e:
            return f"Sorry, there was an issue generating your plan: {str(e)}. Let's try again!"
            
        except Exception as e:
            return f"Sorry, there was an issue generating your plan: {str(e)}. Let's try again!"
    
    def _get_random_response(self, response_type: str) -> str:
        """Get a random response from the templates"""
        import random
        templates = self.response_templates.get(response_type, ["I'm here to help!"])
        return random.choice(templates)
    
    def _generate_ai_response(self, user_message: str, context: str = "general") -> str:
        """Generate AI response using OpenAI"""
        # Check if API key is available
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            # Use fallback responses when API key is not set
            if context == "casual_chat":
                return "I'm here to help you with productivity and goal planning! What would you like to work on?"
            else:
                return "I'm here to help you achieve your goals! What would you like to work on?"
        
        try:
            # Create system prompt based on context
            system_prompts = {
                "casual_chat": "You are a helpful, friendly AI productivity assistant. Have natural conversations with users. Be conversational, supportive, and engaging. Help with productivity tips, goal planning, and general questions. Keep responses concise but helpful.",
                "general": "You are a helpful, friendly AI productivity assistant. Have natural conversations with users. Be conversational, supportive, and engaging."
            }
            
            system_prompt = system_prompts.get(context, system_prompts["general"])
            
            # Prepare messages for API call
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 messages to stay within token limits)
            recent_history = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get actual model name
            actual_model = self.model_mapping.get(self.ai_model, "gpt-3.5-turbo")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=actual_model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to context-aware responses
            if context == "casual_chat":
                return "I'm here to help you with productivity and goal planning! What would you like to work on?"
            else:
                return "I'm here to help you achieve your goals! What would you like to work on?"
    
    def get_chat_history(self) -> List[Dict]:
        """Get full chat history"""
        return self.chat_history
    
    def get_goal_data(self) -> Dict:
        """Get collected goal data"""
        return self.goal_data.copy()
    
    def get_current_state(self) -> str:
        """Get current conversation state"""
        return self.current_state.value
    
    def is_ready_for_planning(self) -> bool:
        """Check if ready to generate plan"""
        return (
            self.current_state == AssistantState.GENERATING_PLAN and
            self.goal_data["confirmed"] == True
        )
    
    def reset_conversation(self) -> None:
        """Reset conversation state and data"""
        self.current_state = AssistantState.GREETING
        self.chat_history = []
        self.goal_data = {
            "raw_goal": "",
            "timeframe": "",
            "features": [],
            "smart_goal": "",
            "confirmed": False
        } 