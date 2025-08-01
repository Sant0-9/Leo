import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ConversationState(Enum):
    GREETING = "greeting"
    ASKING_INTENT = "asking_intent"
    GOAL_PLANNING = "goal_planning"
    SCHEDULING = "scheduling"
    PRODUCTIVITY_COACHING = "productivity_coaching"
    CASUAL_CHAT = "casual_chat"
    PLAN_GENERATION = "plan_generation"

class ChatAgent:
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
        self.conversation_state = ConversationState.GREETING
        self.chat_history = []
        self.user_data = {}
        self.goal_context = {}
        
        # Intent detection keywords
        self.intent_keywords = {
            "goal_planning": ["goal", "achieve", "plan", "create", "work on", "learn", "improve", "get better", "start", "master", "study", "develop", "build", "lose weight", "gain muscle", "learn python", "learn machine learning", "want to", "need to"],
            "scheduling": ["schedule", "time", "organize", "plan my day", "routine", "calendar"],
            "productivity_coaching": ["productive", "efficient", "focus", "motivation", "habits", "routine", "work better", "productivity tips", "study habits", "work habits"],
            "casual_chat": ["chat", "talk", "just", "hello", "hi", "how are you", "what's up", "tell me about", "what are", "how do i", "can you help", "help me", "assist"]
        }
        
        # Goal planning flow questions
        self.goal_questions = [
            "timeline",
            "seriousness", 
            "reminders",
            "confirmation"
        ]
        
        self.current_question_index = 0
        
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
            "goal_habits": [
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
        
        # Add AI response to history
        self.chat_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now()
        })
        
        return response

    def _generate_response(self, user_message: str) -> str:
        """Generate contextual response based on conversation state"""
        user_lower = user_message.lower()
        
        if self.conversation_state == ConversationState.GREETING:
            return self._handle_greeting(user_message)
        
        elif self.conversation_state == ConversationState.ASKING_INTENT:
            return self._handle_intent_detection(user_message)
        
        elif self.conversation_state == ConversationState.GOAL_PLANNING:
            return self._handle_goal_planning(user_message)
        
        elif self.conversation_state == ConversationState.SCHEDULING:
            return self._handle_scheduling(user_message)
        
        elif self.conversation_state == ConversationState.PRODUCTIVITY_COACHING:
            return self._handle_productivity_coaching(user_message)
        
        elif self.conversation_state == ConversationState.CASUAL_CHAT:
            return self._handle_casual_chat(user_message)
        
        elif self.conversation_state == ConversationState.PLAN_GENERATION:
            return self._handle_plan_generation(user_message)
        
        return "I'm here to help! What would you like to work on?"

    def _handle_greeting(self, user_message: str) -> str:
        """Handle initial greeting and ask about intent"""
        # Check if user already provided a goal in their first message
        user_lower = user_message.lower()
        
        # Handle greetings
        if any(word in user_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            self.conversation_state = ConversationState.ASKING_INTENT
            return self._get_random_response("asking_intent")
        
        # Check for productivity coaching questions first
        elif any(keyword in user_lower for keyword in self.intent_keywords["productivity_coaching"]):
            self.conversation_state = ConversationState.PRODUCTIVITY_COACHING
            return self._generate_ai_response(user_message, "productivity_coaching")
        
        # Check for help requests first
        elif any(keyword in user_lower for keyword in ["can you help", "help me", "assist", "support"]):
            self.conversation_state = ConversationState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
        
        # Check for casual chat questions
        elif any(keyword in user_lower for keyword in self.intent_keywords["casual_chat"]):
            self.conversation_state = ConversationState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
        
        # If user gives a detailed response with goal keywords, treat it as a goal
        elif len(user_message.strip()) > 5 and any(keyword in user_lower for keyword in self.intent_keywords["goal_planning"]):
            self.conversation_state = ConversationState.GOAL_PLANNING
            self.goal_context["goal"] = user_message
            return self._get_random_response("goal_timeline")
        else:
            self.conversation_state = ConversationState.ASKING_INTENT
            return self._get_random_response("asking_intent")

    def _handle_intent_detection(self, user_message: str) -> str:
        """Detect user intent and route accordingly"""
        user_lower = user_message.lower()
        
        # Check for casual chat intent first
        if any(keyword in user_lower for keyword in self.intent_keywords["casual_chat"]):
            self.conversation_state = ConversationState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
        
        # Check for goal creation requests
        elif any(phrase in user_lower for phrase in ["create a goal", "make a goal", "set a goal", "create goal", "make goal", "set goal", "goal for me", "create for me", "with this agent"]):
            self.conversation_state = ConversationState.GOAL_PLANNING
            # Try to extract goal from context or use a default
            if "dsa" in user_lower or "data structures" in user_lower or "algorithms" in user_lower:
                self.goal_context["goal"] = "Learn Data Structures and Algorithms"
            else:
                self.goal_context["goal"] = "your goal"
            return self._get_random_response("goal_timeline")
        
        # Check for goal planning intent
        elif any(keyword in user_lower for keyword in self.intent_keywords["goal_planning"]):
            self.conversation_state = ConversationState.GOAL_PLANNING
            self.goal_context["goal"] = user_message
            return self._get_random_response("goal_timeline")
        
        # Check for scheduling intent
        elif any(keyword in user_lower for keyword in self.intent_keywords["scheduling"]):
            self.conversation_state = ConversationState.SCHEDULING
            return self._generate_ai_response(user_message, "scheduling")
        
        # Check for productivity coaching intent
        elif any(keyword in user_lower for keyword in self.intent_keywords["productivity_coaching"]):
            self.conversation_state = ConversationState.PRODUCTIVITY_COACHING
            return self._generate_ai_response(user_message, "productivity_coaching")
        
        # Default to goal planning if user gives a detailed response
        elif len(user_message.strip()) > 5:
            self.conversation_state = ConversationState.GOAL_PLANNING
            self.goal_context["goal"] = user_message
            return self._get_random_response("goal_timeline")
        
        # Handle short responses like "what", "wtf", etc.
        elif len(user_message.strip()) <= 3 or user_lower in ["wtf", "what", "h", "l", "o", "wait", "stop", "no", "yes"]:
            self.conversation_state = ConversationState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")
        
        # Default to casual chat for general questions and requests
        else:
            self.conversation_state = ConversationState.CASUAL_CHAT
            return self._generate_ai_response(user_message, "casual_chat")

    def _handle_goal_planning(self, user_message: str) -> str:
        """Handle goal planning flow with follow-up questions"""
        user_lower = user_message.lower()
        
        # Handle stop/exit commands
        if user_lower in ["stop", "wait", "exit", "cancel", "no", "nevermind"]:
            self.conversation_state = ConversationState.CASUAL_CHAT
            return "No problem! Let's chat about something else. What's on your mind?"
        
        # Handle unclear or repeated responses
        if len(user_message.strip()) <= 3 or user_message.lower() in ["same", "repeating", "repeat", "again"]:
            return self._get_clarification_response()
        
        if self.current_question_index == 0:  # Goal question
            # Store the goal
            self.goal_context["goal"] = user_message
            self.current_question_index = 1
            return self._get_random_response("goal_importance")
        
        elif self.current_question_index == 1:  # Importance question
            # Store the importance/reason
            self.goal_context["importance"] = user_message
            self.current_question_index = 2
            return self._get_random_response("goal_timeline")
        
        elif self.current_question_index == 2:  # Timeline question
            # Check if user is providing importance instead of timeline
            if len(user_message.strip()) > 10 and not any(word in user_lower for word in ["7", "14", "1 month", "6 month", "week", "month", "day"]):
                # User might be providing importance instead of timeline
                self.goal_context["importance"] = user_message
                return self._get_random_response("goal_timeline")
            
            # Extract timeline information
            if any(word in user_lower for word in ["7 day", "7 days", "week", "1 week"]):
                self.goal_context["timeline"] = "7_days"
            elif any(word in user_lower for word in ["14 day", "14 days", "2 week", "2 weeks"]):
                self.goal_context["timeline"] = "14_days"
            elif any(word in user_lower for word in ["1 month", "month", "30 day", "30 days"]):
                self.goal_context["timeline"] = "1_month"
            elif any(word in user_lower for word in ["6 month", "6 months", "half year"]):
                self.goal_context["timeline"] = "6_months"
            else:
                self.goal_context["timeline"] = "1_month"  # Default to 1 month
            
            self.current_question_index = 3
            return self._get_random_response("goal_habits")
        

        
        elif self.current_question_index == 3:  # Habits/Preferences question
            # Store the habits/preferences
            self.goal_context["habits"] = user_message
            self.current_question_index = 4
            return self._get_random_response("goal_confirmation")
        
        elif self.current_question_index == 4:  # Confirmation question
            if any(word in user_lower for word in ["yes", "sure", "okay", "create", "generate", "plan", "ready", "go"]):
                self.conversation_state = ConversationState.PLAN_GENERATION
                return self._generate_plan_summary()
            else:
                # Reset to ask more questions
                self.current_question_index = 0
                return "No problem! Let me ask you a few more questions to better understand your goal."

    def _handle_scheduling(self, user_message: str) -> str:
        """Handle scheduling-related conversations using AI"""
        return self._generate_ai_response(user_message, "scheduling")

    def _handle_productivity_coaching(self, user_message: str) -> str:
        """Handle productivity coaching conversations using AI"""
        return self._generate_ai_response(user_message, "productivity_coaching")

    def _handle_casual_chat(self, user_message: str) -> str:
        """Handle casual conversation using AI"""
        user_lower = user_message.lower()
        
        # Handle short responses
        if len(user_message.strip()) <= 3:
            return "I'm here to help you achieve your goals! What would you like to work on? You can tell me about a goal you want to achieve, ask for help with productivity, or just chat."
        
        # Handle goal creation requests in casual chat
        if any(phrase in user_lower for phrase in ["create a goal", "make a goal", "set a goal", "create goal", "make goal", "set goal", "goal for me", "create for me", "with this agent"]):
            self.conversation_state = ConversationState.GOAL_PLANNING
            # Try to extract goal from context or use a default
            if "dsa" in user_lower or "data structures" in user_lower or "algorithms" in user_lower:
                self.goal_context["goal"] = "Learn Data Structures and Algorithms"
            else:
                self.goal_context["goal"] = "your goal"
            return self._get_random_response("goal_timeline")
        
        # Handle questions about the assistant
        if any(word in user_lower for word in ["what", "who", "how", "why"]):
            return "I'm your AI productivity assistant! I can help you create personalized plans for your goals, improve your productivity, or just have a friendly chat. What would you like to work on?"
        
        # Handle greetings
        if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return "Hello! I'm here to help you achieve your goals and improve your productivity. What would you like to work on today?"
        
        # Use AI for other responses
        return self._generate_ai_response(user_message, "casual_chat")

    def _handle_plan_generation(self, user_message: str) -> str:
        """Handle plan generation confirmation"""
        if any(word in user_message.lower() for word in ["yes", "sure", "okay", "create", "generate"]):
            return "Perfect! I'm generating your personalized plan now. This will include specific steps, timeline, and resources tailored to your goal."
        else:
            self.conversation_state = ConversationState.GOAL_PLANNING
            self.current_question_index = 0
            return "No problem! Let me ask you a few more questions to better understand your goal."

    def _generate_plan_summary(self) -> str:
        """Generate a summary of collected goal information"""
        goal = self.goal_context.get("goal", "your goal")
        importance = self.goal_context.get("importance", "personal growth")
        timeline = self.goal_context.get("timeline", "1_month")
        habits = self.goal_context.get("habits", "flexible schedule")
        
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
📅 **Your style:** {habits}

Ready to build your personalized plan?"""

    def _get_random_response(self, response_type: str) -> str:
        """Get a random response from the templates"""
        import random
        templates = self.response_templates.get(response_type, ["I'm here to help!"])
        return random.choice(templates)
    
    def _get_clarification_response(self) -> str:
        """Get a clarification response when user gives unclear input"""
        goal = self.goal_context.get("goal", "your goal")
        
        if self.current_question_index == 0:
            return f"What's your main goal right now? Just tell me what you want to achieve."
        elif self.current_question_index == 1:
            return f"Why is '{goal}' important to you right now? What's driving you?"
        elif self.current_question_index == 2:
            return f"Got it. What's your timeline - 7 days, 14 days, 1 month, or 6 months?"
        elif self.current_question_index == 3:
            return f"Anything I should know about your schedule or preferences?"
        else:
            return f"Ready to build your plan for '{goal}'? Just say yes!"

    def get_chat_history(self) -> List[Dict]:
        """Get full chat history"""
        return self.chat_history

    def get_goal_context(self) -> Dict:
        """Get collected goal information"""
        return self.goal_context.copy()

    def reset_conversation(self) -> None:
        """Reset conversation state and data"""
        self.conversation_state = ConversationState.GREETING
        self.chat_history = []
        self.user_data = {}
        self.goal_context = {}
        self.current_question_index = 0

    def is_ready_for_planning(self) -> bool:
        """Check if enough information is collected for plan generation"""
        return (
            self.conversation_state == ConversationState.PLAN_GENERATION and
            "goal" in self.goal_context and
            "importance" in self.goal_context and
            "timeline" in self.goal_context and
            "habits" in self.goal_context
        )

    def get_conversation_state(self) -> str:
        """Get current conversation state"""
        return self.conversation_state.value
    
    def _generate_ai_response(self, user_message: str, context: str = "general") -> str:
        """Generate AI response using OpenAI"""
        # Check if API key is available
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            # Use fallback responses when API key is not set
            if context == "casual_chat":
                if len(user_message.strip()) <= 3:
                    return "I'm here to help! What would you like to work on today? You can tell me about a goal, ask for productivity tips, or just chat."
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
                "goal_planning": "You are a productivity coach helping users create personalized goal plans. Ask relevant follow-up questions to understand their timeline, commitment level, and preferences. Be encouraging and professional.",
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
                    return "I'm here to help! What would you like to work on today? You can tell me about a goal, ask for productivity tips, or just chat."
                else:
                    return "That's interesting! Tell me more about what you'd like to work on or how I can help you."
            elif context == "productivity_coaching":
                return "I'd be happy to help with productivity! What specific area would you like to improve - time management, focus, habits, or something else?"
            elif context == "scheduling":
                return "I can help you with scheduling and time management! What kind of schedule are you looking to create?"
            else:
                return "I'm here to help you achieve your goals! What would you like to work on?" 