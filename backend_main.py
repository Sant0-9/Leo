#!/usr/bin/env python3
"""
FastAPI Backend for Leo AI Assistant
Provides RESTful APIs and WebSocket connections for the React frontend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import uvicorn
from datetime import datetime
import json
import os
from typing import List, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our modules
from agents.smart_assistant import SmartAssistant
from utils.memory_manager import MemoryManager
from utils.mode_manager import ModeManager
from backend.services.google_services import GoogleServices
from backend.services.chroma_service import ChromaService

load_dotenv()

app = FastAPI(
    title="Leo AI Assistant Backend",
    description="FastAPI backend for Leo AI Assistant with Agent Mode and Assistant Mode",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
assistant = SmartAssistant()
memory_manager = MemoryManager()
mode_manager = ModeManager()
google_services = GoogleServices()
chroma_service = ChromaService()

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class ModeSwitch(BaseModel):
    mode: str  # "agent" or "assistant"

class MemoryQuery(BaseModel):
    query: str
    limit: int = 10

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Leo AI Assistant Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check with service status"""
    try:
        # Check all services
        services = {
            "memory": memory_manager.health_check(),
            "chroma": chroma_service.health_check(),
            "google_services": google_services.health_check(),
            "websocket_connections": len(manager.active_connections)
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": services
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

# Mode management endpoints
@app.get("/api/mode/current")
async def get_current_mode():
    """Get current mode (agent/assistant)"""
    return {"mode": mode_manager.get_current_mode()}

@app.post("/api/mode/switch")
async def switch_mode(mode_data: ModeSwitch):
    """Switch between agent and assistant modes"""
    try:
        success = mode_manager.switch_mode(mode_data.mode)
        if success:
            # Broadcast mode change to all connected clients
            await manager.broadcast({
                "type": "mode_changed",
                "mode": mode_data.mode,
                "timestamp": datetime.now().isoformat()
            })
            return {"status": "success", "mode": mode_data.mode}
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoints
@app.post("/api/chat/send")
async def send_message(message_data: ChatMessage):
    """Send message to AI assistant"""
    try:
        # Get recent conversation context from memory
        recent_context = memory_manager.get_conversation_context(message_data.user_id, include_metadata=False)
        
        # Load conversation context into assistant
        assistant.chat_history = []
        for msg in recent_context:
            assistant.chat_history.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": datetime.now()
            })
        
        # Store current message in memory
        memory_manager.add_message(message_data.user_id, "user", message_data.message)
        
        # Store in long-term memory (ChromaDB)
        chroma_service.add_message(message_data.user_id, "user", message_data.message)
        
        # Get AI response with context
        response = assistant.handle_message(message_data.message)
        
        # Store response in memory
        memory_manager.add_message(message_data.user_id, "assistant", response)
        chroma_service.add_message(message_data.user_id, "assistant", response)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "chat_message",
            "user_message": message_data.message,
            "assistant_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message_id": f"msg_{datetime.now().timestamp()}",
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "user_id": message_data.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history(user_id: str = "default_user", limit: int = 20):
    """Get chat history"""
    try:
        messages = memory_manager.get_recent_messages(user_id, limit)
        return {
            "messages": messages,
            "total": len(messages),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/memory/clear")
async def clear_memory(user_id: str = "default_user"):
    """Clear chat memory"""
    try:
        memory_manager.clear_memory(user_id)
        return {"status": "cleared", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/memory/stats")
async def get_memory_stats(user_id: str = "default_user"):
    """Get memory statistics"""
    try:
        stats = memory_manager.get_memory_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/context")
async def get_context(query_data: MemoryQuery, user_id: str = "default_user"):
    """Get relevant context from long-term memory"""
    try:
        context = chroma_service.search_similar(user_id, query_data.query, query_data.limit)
        return {
            "context": context,
            "query": query_data.query,
            "relevant_memories": len(context),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent mode endpoints
@app.get("/api/agent/status")
async def get_agent_status():
    """Get agent status and metrics"""
    try:
        status = mode_manager.get_agent_status()
        return {
            "is_active": mode_manager.get_current_mode() == "agent",
            "status": "active" if mode_manager.get_current_mode() == "agent" else "inactive",
            "update_interval": 45,
            "connected_clients": len(manager.active_connections),
            "last_update": datetime.now().isoformat(),
            **status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/trigger-update")
async def trigger_agent_update():
    """Manually trigger agent update"""
    try:
        # Get latest data from Google services
        google_data = google_services.get_all_data()
        
        # Broadcast update to connected clients
        await manager.broadcast({
            "type": "agent_status",
            "message": "Manual update triggered",
            "timestamp": datetime.now().isoformat(),
            "data": google_data
        })
        
        return {"status": "triggered", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/generate-insight")
async def generate_insight():
    """Generate AI insight based on recent data"""
    try:
        # Get recent context
        recent_data = memory_manager.get_recent_context()
        
        # Generate insight using assistant
        insight = assistant._generate_ai_response(
            "Based on my recent activity, what insights do you have?",
            "insight_generation"
        )
        
        # Broadcast insight to connected clients
        await manager.broadcast({
            "type": "insight_generated",
            "insight": insight,
            "confidence": 85,
            "category": "productivity",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "insight": insight,
            "confidence": 85,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/metrics")
async def get_agent_metrics():
    """Get agent performance metrics"""
    try:
        return mode_manager.get_agent_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Google Services endpoints
@app.get("/api/google/calendar")
async def get_calendar_events():
    """Get Google Calendar events"""
    try:
        events = google_services.get_calendar_events()
        return {"events": events, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google/gmail")
async def get_gmail_data():
    """Get Gmail data"""
    try:
        gmail_data = google_services.get_gmail_data()
        return {"gmail": gmail_data, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google/tasks")
async def get_tasks():
    """Get Google Tasks"""
    try:
        tasks = google_services.get_tasks()
        return {"tasks": tasks, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google/all")
async def get_all_google_data():
    """Get all Google services data"""
    try:
        all_data = google_services.get_all_data()
        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send initial connection message
    await websocket.send_json({
        "type": "connection",
        "message": "Connected to Leo Assistant",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Start periodic updates for agent mode
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            # Only send updates if in agent mode
            if mode_manager.get_current_mode() == "agent":
                try:
                    # Get fresh data from Google services
                    google_data = google_services.get_all_data()
                    
                    await websocket.send_json({
                        "type": "api_data_updated",
                        "message": "API data refreshed",
                        "timestamp": datetime.now().isoformat(),
                        "data": google_data
                    })
                except Exception as e:
                    print(f"Error getting Google data: {e}")
                    # Send mock data as fallback
                    await websocket.send_json({
                        "type": "api_data_updated",
                        "message": "API data refreshed (mock)",
                        "timestamp": datetime.now().isoformat(),
                        "data": {
                            "calendar": {"status": "healthy", "total_count": 5},
                            "gmail": {"status": "healthy", "unread_count": 8},
                            "tasks": {"status": "healthy", "total_count": 12}
                        }
                    })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🧠 Starting Leo AI Assistant Backend...")
    print("📡 Frontend should connect to: http://localhost:8000")
    print("🔌 WebSocket available at: ws://localhost:8000/ws")
    print("🎯 Backend provides full Phase 1-3 functionality")
    print("⚡ Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")