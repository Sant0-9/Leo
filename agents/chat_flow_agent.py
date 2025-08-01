#!/usr/bin/env python3
"""
ChatFlowAgent - Manages conversation state and user data for goal planning
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatFlowState(Enum):
    GREETING = "greeting"
    AWAITING_INTENT = "awaiting_intent"
    AWAITING_GOAL = "awaiting_goal"
    AWAITING_IMPORTANCE = "awaiting_importance"
    AWAITING_TIMELINE = "awaiting_timeline"
    AWAITING_PREFERENCES = "awaiting_preferences"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    READY_TO_GENERATE_PLAN = "ready_to_generate_plan"
    CASUAL_CHAT = "casual_chat"
    PRODUCTIVITY_COACHING = "productivity_coaching"
    SCHEDULING = "scheduling"

class ChatFlowAgent:
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
        
        # Conversation state management
        self.current_state = ChatFlowState.GREETING
        self.chat_history = []
        
        # User data storage
        self.user_data = {
            "goal": "",
            "importance": "",
            "timeline": "",
            "preferences": "",
            "confirmed": False
        }
        
        # Intent detection keywords
        self.intent_keywords = {
            "goal_planning": ["goal", "achieve", "plan", "create", "work on", "learn", "improve", "get better", "start", "master", "study", "develop", "build", "lose weight", "gain muscle", "learn python", "learn machine learning", "want to", "need to"],
            "scheduling": ["schedule", "time", "organize", "plan my day", "routine", "calendar"],
            "productivity_coaching": ["productive", "efficient", "focus", "motivation", "habits", "routine", "work better", "productivity tips", "study habits", "work habits"],
            "casual_chat": ["chat", "talk", "just", "hello", "hi", "how are you", "what's up", "tell me about", "what are", "how do i", "can you help", "help me", "assist"]
        }
        
        # Response templates
        self.response_templates = {
            "greeting": [
                "Hey there! 👋 What's on your mind today?",
                "Hi! Ready to crush some goals or just chat? 💪",
                "Hello! What would you like to work on?"
            ],
            "asking_intent": [
                "Are you looking to achieve a goal or just chat for now?",
                "Want to set a goal or just explore some productivity tips?",
                "Are you here to plan something or just have a conversation?"
            ],
            "goal_question": [
                "What's your main goal right now?",
                "What are you looking to achieve?",
                "What's the big thing you want to work on?"
            ],
            "goal_importance": [
                "Love that. Why is this important to you right now?",
                "Cool goal. What's driving you to work on this?",
                "Nice. What makes this meaningful to you?"
            ],
            "goal_timeline": [
                "Totally get that. Want a 7-day, 14-day, 1-month, or 6-month plan for it?",
                "Got it. What's your timeline - quick sprint or longer journey?",
                "Cool. How long do you want to work on this - weeks or months?"
            ],
            "goal_preferences": [
                "Anything I should know — like your schedule or what you enjoy?",
                "Tell me about your current routine or what works for you.",
                "What's your typical day like? Any preferences I should know?"
            ],
            "goal_confirmation": [
                "Awesome! Ready to build your plan?",
                "Perfect! Want me to create a personalized plan for this?",
                "Great! Should I put together your plan now?"
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
        if self.current_state == ChatFlowState.GREETING:
            return self._handle_greeting(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_INTENT:
            return self._handle_intent_detection(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_GOAL:
            return self._handle_goal_input(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_IMPORTANCE:
            return self._handle_importance_input(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_TIMELINE:
            return self._handle_timeline_input(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_PREFERENCES:
            return self._handle_preferences_input(user_message)
        
        elif self.current_state == ChatFlowState.AWAITING_CONFIRMATION:
            return self._handle_confirmation_input(user_message)
        
        elif self.current_state == ChatFlowState.READY_TO_GENERATE_PLAN:
            return self._handle_plan_generation(user_message)
        
        elif self.current_state == ChatFlowState.CASUAL_CHAT:
            return self._handle_casual_chat(user_message)
        
        elif self.current_state == ChatFlowState.PRODUCTIVITY_COACHING:
            return self._handle_productivity_coaching(user_message)
        
        elif self.current_state == ChatFlowState.SCHEDULING:
            return self._handle_scheduling(user_message)
        
        else:
            # Default to casual chat
            self.current_state = ChatFlowState.CASUAL_CHAT
            return self._handle_casual_chat(user_message)
    
    def _handle_greeting(self, user_message: str) -> str:
        """Handle initial greeting"""
        user_lower = user_message.lower()
        
        # Check for direct goal statements
        if any(keyword in user_lower for keyword in self.intent_keywords["goal_planning"]):
            self.current_state = ChatFlowState.AWAITING_GOAL
            self.user_data["goal"] = user_message
            return self._get_random_response("goal_importance")
        
        # Check for other intents
        elif any(keyword in user_lower for keyword in self.intent_keywords["productivity_coaching"]):
            self.current_state = ChatFlowState.PRODUCTIVITY_COACHING
            return self._generate_ai_response(user_message, "productivity_coaching")
        
        elif any(keyword in user_lower for keyword in self.intent_keywords["casual_chat"]):
            self.current_state = ChatFlowState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
        
        else:
            self.current_state = ChatFlowState.AWAITING_INTENT
            return self._get_random_response("asking_intent")
    
    def _handle_intent_detection(self, user_message: str) -> str:
        """Handle intent detection"""
        user_lower = user_message.lower()
        
        # Check for goal planning intent
        if any(keyword in user_lower for keyword in self.intent_keywords["goal_planning"]):
            self.current_state = ChatFlowState.AWAITING_GOAL
            self.user_data["goal"] = user_message
            return self._get_random_response("goal_importance")
        
        # Check for other intents
        elif any(keyword in user_lower for keyword in self.intent_keywords["productivity_coaching"]):
            self.current_state = ChatFlowState.PRODUCTIVITY_COACHING
            return self._generate_ai_response(user_message, "productivity_coaching")
        
        elif any(keyword in user_lower for keyword in self.intent_keywords["scheduling"]):
            self.current_state = ChatFlowState.SCHEDULING
            return self._generate_ai_response(user_message, "scheduling")
        
        else:
            self.current_state = ChatFlowState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
    
    def _handle_goal_input(self, user_message: str) -> str:
        """Handle goal input"""
        self.user_data["goal"] = user_message
        self.current_state = ChatFlowState.AWAITING_IMPORTANCE
        return self._get_random_response("goal_importance")
    
    def _handle_importance_input(self, user_message: str) -> str:
        """Handle importance input"""
        self.user_data["importance"] = user_message
        self.current_state = ChatFlowState.AWAITING_TIMELINE
        return self._get_random_response("goal_timeline")
    
    def _handle_timeline_input(self, user_message: str) -> str:
        """Handle timeline input"""
        user_lower = user_message.lower()
        
        # Extract timeline
        if any(word in user_lower for word in ["7 day", "7 days", "week", "1 week"]):
            self.user_data["timeline"] = "7_days"
        elif any(word in user_lower for word in ["14 day", "14 days", "2 week", "2 weeks"]):
            self.user_data["timeline"] = "14_days"
        elif any(word in user_lower for word in ["1 month", "month", "30 day", "30 days"]):
            self.user_data["timeline"] = "1_month"
        elif any(word in user_lower for word in ["6 month", "6 months", "half year"]):
            self.user_data["timeline"] = "6_months"
        else:
            self.user_data["timeline"] = "1_month"  # Default
        
        self.current_state = ChatFlowState.AWAITING_PREFERENCES
        return self._get_random_response("goal_preferences")
    
    def _handle_preferences_input(self, user_message: str) -> str:
        """Handle preferences input"""
        self.user_data["preferences"] = user_message
        self.current_state = ChatFlowState.AWAITING_CONFIRMATION
        return self._get_random_response("goal_confirmation")
    
    def _handle_confirmation_input(self, user_message: str) -> str:
        """Handle confirmation input"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["yes", "sure", "okay", "create", "generate", "plan", "ready", "go"]):
            self.user_data["confirmed"] = True
            self.current_state = ChatFlowState.READY_TO_GENERATE_PLAN
            return self._generate_plan_summary()
        else:
            # Reset to ask more questions
            self.current_state = ChatFlowState.AWAITING_GOAL
            return "No problem! Let me ask you a few more questions to better understand your goal."
    
    def _handle_plan_generation(self, user_message: str) -> str:
        """Handle plan generation state"""
        return "Perfect! I'm ready to generate your personalized plan. The system will now create a detailed plan based on your inputs."
    
    def _handle_casual_chat(self, user_message: str) -> str:
        """Handle casual chat"""
        return self._generate_ai_response(user_message, "casual_chat")
    
    def _handle_productivity_coaching(self, user_message: str) -> str:
        """Handle productivity coaching"""
        return self._generate_ai_response(user_message, "productivity_coaching")
    
    def _handle_scheduling(self, user_message: str) -> str:
        """Handle scheduling"""
        return self._generate_ai_response(user_message, "scheduling")
    
    def _generate_plan_summary(self) -> str:
        """Generate a summary of collected goal information"""
        goal = self.user_data.get("goal", "your goal")
        importance = self.user_data.get("importance", "personal growth")
        timeline = self.user_data.get("timeline", "1_month")
        preferences = self.user_data.get("preferences", "flexible schedule")
        
        # Convert timeline to readable text
        timeline_text = {
            "7_days": "7 days",
            "14_days": "14 days", 
            "1_month": "1 month",
            "6_months": "6 months"
        }.get(timeline, "1 month")
        
        return f"""Perfect! Here's what I understand:

🎯 **Goal:** {goal}
💪 **Why it matters:** {importance}
⏰ **Timeline:** {timeline_text}
📅 **Your style:** {preferences}

Ready to build your personalized plan?"""
    
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
                if len(user_message.strip()) <= 3:
                    return "I'm here to help! What would you like to work on today? You can tell me about a goal you want to achieve, ask for productivity tips, or just chat."
                else:
                    return "That's interesting! Tell me more about what you'd like to work on or how I can help you."
            elif context == "productivity_coaching":
                return "I'd be happy to help with productivity! What specific area would you like to improve - time management, focus, habits, or something else?"
            elif context == "scheduling":
                return "I can help you with scheduling and time management! What kind of schedule are you looking to create?"
            else:
                return "I'm here to help you achieve your goals! What would you like to work on?"
        
        try:
            # Create system prompt based on context
            system_prompts = {
                "casual_chat": "You are a helpful, friendly AI productivity assistant. Have natural conversations with users. Be conversational, supportive, and engaging. Help with productivity tips, goal planning, and general questions. Keep responses concise but helpful.",
                "productivity_coaching": "You are a productivity expert helping users improve their efficiency, focus, and work habits. Provide practical advice and actionable tips.",
                "scheduling": "You are a time management expert helping users organize their schedules and routines. Provide practical scheduling advice.",
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
                if len(user_message.strip()) <= 3:
                    return "I'm here to help! What would you like to work on today? You can tell me about a goal you want to achieve, ask for productivity tips, or just chat."
                else:
                    return "That's interesting! Tell me more about what you'd like to work on or how I can help you."
            elif context == "productivity_coaching":
                return "I'd be happy to help with productivity! What specific area would you like to improve - time management, focus, habits, or something else?"
            elif context == "scheduling":
                return "I can help you with scheduling and time management! What kind of schedule are you looking to create?"
            else:
                return "I'm here to help you achieve your goals! What would you like to work on?"
    
    def get_chat_history(self) -> List[Dict]:
        """Get full chat history"""
        return self.chat_history
    
    def get_user_data(self) -> Dict:
        """Get collected user data"""
        return self.user_data.copy()
    
    def get_current_state(self) -> str:
        """Get current conversation state"""
        return self.current_state.value
    
    def is_ready_for_planning(self) -> bool:
        """Check if ready to generate plan"""
        return (
            self.current_state == ChatFlowState.READY_TO_GENERATE_PLAN and
            self.user_data["confirmed"] == True
        )
    
    def reset_conversation(self) -> None:
        """Reset conversation state and data"""
        self.current_state = ChatFlowState.GREETING
        self.chat_history = []
        self.user_data = {
            "goal": "",
            "importance": "",
            "timeline": "",
            "preferences": "",
            "confirmed": False
        } 