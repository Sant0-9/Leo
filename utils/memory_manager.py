#!/usr/bin/env python3
"""
Memory Manager for Leo AI Assistant
Handles short-term memory, session management, and memory persistence
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from collections import defaultdict, deque

class MemoryManager:
    def __init__(self, max_session_messages: int = 100):
        """Initialize memory manager"""
        self.max_session_messages = max_session_messages
        
        # Short-term memory (in-memory, per session)
        self.session_memory = defaultdict(lambda: deque(maxlen=max_session_messages))
        
        # User sessions tracking
        self.user_sessions = defaultdict(dict)
        
        # Memory persistence file
        self.memory_file = "memory_persistence.json"
        
        # Load persistent memory if exists
        self._load_persistent_memory()
        
        print("✅ Memory Manager initialized")
    
    def _load_persistent_memory(self):
        """Load persistent memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    
                # Load user sessions
                self.user_sessions = defaultdict(dict, data.get('user_sessions', {}))
                
                # Load recent messages (limited amount)
                recent_messages = data.get('recent_messages', {})
                for user_id, messages in recent_messages.items():
                    self.session_memory[user_id] = deque(
                        messages[-20:],  # Only load last 20 messages
                        maxlen=self.max_session_messages
                    )
                
                print(f"📚 Loaded persistent memory for {len(self.user_sessions)} users")
        except Exception as e:
            print(f"⚠️ Error loading persistent memory: {e}")
    
    def _save_persistent_memory(self):
        """Save important memory to file"""
        try:
            # Prepare data for persistence
            data = {
                'user_sessions': dict(self.user_sessions),
                'recent_messages': {},
                'last_saved': datetime.now().isoformat()
            }
            
            # Save only recent messages to avoid large files
            for user_id, messages in self.session_memory.items():
                data['recent_messages'][user_id] = list(messages)[-10:]  # Last 10 messages
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving persistent memory: {e}")
    
    def health_check(self) -> bool:
        """Check if memory manager is healthy"""
        try:
            # Basic health checks
            return (
                hasattr(self, 'session_memory') and
                hasattr(self, 'user_sessions') and
                len(self.session_memory) >= 0  # Always true but tests attribute exists
            )
        except Exception:
            return False
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to short-term memory"""
        try:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add to session memory
            self.session_memory[user_id].append(message)
            
            # Update user session info
            self._update_user_session(user_id)
            
            # Periodically save to persistence
            if len(self.session_memory[user_id]) % 10 == 0:
                self._save_persistent_memory()
                
        except Exception as e:
            print(f"Error adding message to memory: {e}")
    
    def get_recent_messages(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get recent messages for a user"""
        try:
            messages = list(self.session_memory[user_id])
            return messages[-limit:] if limit > 0 else messages
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
    
    def get_conversation_context(self, user_id: str, include_metadata: bool = False) -> List[Dict]:
        """Get conversation context for AI processing"""
        try:
            messages = list(self.session_memory[user_id])
            
            if include_metadata:
                return messages
            else:
                # Return just role and content for AI
                return [
                    {'role': msg['role'], 'content': msg['content']}
                    for msg in messages
                ]
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return []
    
    def clear_memory(self, user_id: str):
        """Clear memory for a user"""
        try:
            if user_id in self.session_memory:
                self.session_memory[user_id].clear()
            
            if user_id in self.user_sessions:
                self.user_sessions[user_id] = {
                    'last_activity': datetime.now().isoformat(),
                    'session_start': datetime.now().isoformat(),
                    'messages_count': 0
                }
            
            self._save_persistent_memory()
            
        except Exception as e:
            print(f"Error clearing memory: {e}")
    
    def get_memory_stats(self, user_id: str) -> Dict:
        """Get memory statistics for a user"""
        try:
            messages = list(self.session_memory[user_id])
            session_info = self.user_sessions.get(user_id, {})
            
            # Calculate session duration
            session_start = session_info.get('session_start')
            duration_minutes = 0
            if session_start:
                start_time = datetime.fromisoformat(session_start.replace('Z', '+00:00'))
                duration_minutes = (datetime.now() - start_time).seconds // 60
            
            # Calculate memory usage (rough estimate)
            memory_usage = len(json.dumps(messages)) / 1024  # KB
            memory_percent = min((memory_usage / 100) * 100, 100)  # Rough percentage
            
            return {
                'total_messages': len(messages),
                'session_duration_minutes': duration_minutes,
                'memory_usage_percent': round(memory_percent, 1),
                'last_activity': session_info.get('last_activity', ''),
                'session_start': session_info.get('session_start', ''),
                'messages_today': self._count_messages_today(user_id)
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {
                'total_messages': 0,
                'session_duration_minutes': 0,
                'memory_usage_percent': 0,
                'last_activity': '',
                'session_start': '',
                'messages_today': 0
            }
    
    def get_recent_context(self, user_id: str = None) -> str:
        """Get recent context summary across all users or specific user"""
        try:
            if user_id:
                messages = list(self.session_memory[user_id])
                recent_messages = messages[-5:]  # Last 5 messages
            else:
                # Get recent activity across all users
                all_recent = []
                for uid, messages in self.session_memory.items():
                    recent = list(messages)[-3:]  # Last 3 per user
                    all_recent.extend(recent)
                
                # Sort by timestamp
                all_recent.sort(key=lambda x: x.get('timestamp', ''))
                recent_messages = all_recent[-10:]  # Last 10 overall
            
            # Create context summary
            context_parts = []
            for msg in recent_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # First 100 chars
                context_parts.append(f"{role}: {content}")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            print(f"Error getting recent context: {e}")
            return "No recent context available"
    
    def _update_user_session(self, user_id: str):
        """Update user session information"""
        try:
            now = datetime.now().isoformat()
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    'session_start': now,
                    'first_seen': now
                }
            
            self.user_sessions[user_id].update({
                'last_activity': now,
                'messages_count': len(self.session_memory[user_id])
            })
            
        except Exception as e:
            print(f"Error updating user session: {e}")
    
    def _count_messages_today(self, user_id: str) -> int:
        """Count messages sent today by user"""
        try:
            today = datetime.now().date()
            count = 0
            
            for message in self.session_memory[user_id]:
                msg_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                if msg_time.date() == today:
                    count += 1
            
            return count
            
        except Exception as e:
            print(f"Error counting today's messages: {e}")
            return 0
    
    def cleanup_old_sessions(self, max_age_days: int = 7):
        """Clean up old inactive sessions"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            users_to_remove = []
            
            for user_id, session_info in self.user_sessions.items():
                last_activity = session_info.get('last_activity')
                if last_activity:
                    activity_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    if activity_time < cutoff_date:
                        users_to_remove.append(user_id)
            
            # Remove old sessions
            for user_id in users_to_remove:
                if user_id in self.session_memory:
                    del self.session_memory[user_id]
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
            
            if users_to_remove:
                print(f"🧹 Cleaned up {len(users_to_remove)} old sessions")
                self._save_persistent_memory()
            
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
    
    def get_all_users_summary(self) -> Dict:
        """Get summary of all user activity"""
        try:
            total_users = len(self.user_sessions)
            total_messages = sum(len(messages) for messages in self.session_memory.values())
            
            # Active users (activity in last 24 hours)
            active_users = 0
            yesterday = datetime.now() - timedelta(days=1)
            
            for session_info in self.user_sessions.values():
                last_activity = session_info.get('last_activity')
                if last_activity:
                    activity_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    if activity_time > yesterday:
                        active_users += 1
            
            return {
                'total_users': total_users,
                'active_users_24h': active_users,
                'total_messages': total_messages,
                'average_messages_per_user': round(total_messages / max(total_users, 1), 1),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting users summary: {e}")
            return {
                'total_users': 0,
                'active_users_24h': 0,
                'total_messages': 0,
                'average_messages_per_user': 0,
                'last_updated': datetime.now().isoformat()
            }