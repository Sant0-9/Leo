#!/usr/bin/env python3
"""
Leo AI Assistant - Smart Assistant Core
Simplified and optimized for production use
"""

import os
from typing import Dict, List
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SmartAssistant:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.api_available = False
        self.chat_history = []
        
        # Initialize OpenAI client
        if self.api_key and len(self.api_key) > 20:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.api_available = True
                print("✅ OpenAI API client initialized")
            except Exception as e:
                print(f"⚠️ OpenAI API initialization failed: {e}")
        else:
            print("⚠️ OpenAI API key not configured")

    def handle_message(self, user_message: str) -> str:
        """Handle user message and return AI response"""
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now()
        })
        
        # Generate response
        response = self._generate_response(user_message)
        
        # Add response to history
        self.chat_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return response

    def _generate_response(self, user_message: str) -> str:
        """Generate AI response using OpenAI or fallback"""
        if not self.api_available or not self.client:
            return self._fallback_response(user_message)
        
        try:
            # Prepare conversation context
            messages = [
                {"role": "system", "content": "You are Leo, a helpful AI assistant focused on productivity and goal planning. Be conversational, supportive, and concise."}
            ]
            
            # Add recent conversation history (last 10 messages)
            recent_history = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            # Get OpenAI response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_response(user_message)

    def _fallback_response(self, user_message: str) -> str:
        """Fallback responses when API is unavailable"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return "Hi! I'm Leo, your AI assistant. I'm here to help with productivity, planning, and any questions you have!"
        
        if any(word in user_lower for word in ["goal", "plan", "achieve"]):
            return "I'd love to help you with goal planning! What would you like to accomplish?"
        
        if any(word in user_lower for word in ["how", "what", "why", "when", "where"]):
            return "That's a great question! I'm currently running in demo mode. With a proper OpenAI API key, I can provide detailed answers and assistance."
        
        return "I understand! I'm here to help with productivity, goal planning, and general assistance. What would you like to work on?"

    def get_chat_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.chat_history.copy()

    def clear_history(self):
        """Clear conversation history"""
        self.chat_history = []

    def health_check(self) -> Dict:
        """Check assistant health status"""
        return {
            "api_available": self.api_available,
            "history_length": len(self.chat_history),
            "status": "healthy" if self.api_available else "limited"
        }