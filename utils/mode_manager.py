#!/usr/bin/env python3
"""
Mode Manager for Leo AI Assistant
Handles switching between Agent Mode and Assistant Mode
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from enum import Enum

class OperationMode(Enum):
    AGENT = "agent"
    ASSISTANT = "assistant"

class ModeManager:
    def __init__(self):
        """Initialize mode manager"""
        self.current_mode = OperationMode.AGENT
        self.mode_history = []
        self.agent_metrics = {
            "tasks_processed": 0,
            "efficiency_score": 85,
            "active_processes": 3,
            "insights_generated": 0,
            "uptime_start": datetime.now(),
            "last_activity": datetime.now()
        }
        
        # Mode persistence file
        self.mode_file = "mode_state.json"
        
        # Load persistent state
        self._load_mode_state()
        
        print(f"✅ Mode Manager initialized in {self.current_mode.value} mode")
    
    def _load_mode_state(self):
        """Load mode state from persistence"""
        try:
            if os.path.exists(self.mode_file):
                with open(self.mode_file, 'r') as f:
                    data = json.load(f)
                    
                # Load current mode
                mode_str = data.get('current_mode', 'agent')
                try:
                    self.current_mode = OperationMode(mode_str)
                except ValueError:
                    self.current_mode = OperationMode.AGENT
                
                # Load mode history
                self.mode_history = data.get('mode_history', [])
                
                # Load agent metrics
                saved_metrics = data.get('agent_metrics', {})
                self.agent_metrics.update(saved_metrics)
                
                # Update uptime start if needed
                if 'uptime_start' in saved_metrics:
                    self.agent_metrics['uptime_start'] = datetime.fromisoformat(
                        saved_metrics['uptime_start']
                    )
                
                print(f"📚 Loaded mode state: {self.current_mode.value}")
                
        except Exception as e:
            print(f"⚠️ Error loading mode state: {e}")
    
    def _save_mode_state(self):
        """Save mode state to persistence"""
        try:
            data = {
                'current_mode': self.current_mode.value,
                'mode_history': self.mode_history,
                'agent_metrics': {
                    **self.agent_metrics,
                    'uptime_start': self.agent_metrics['uptime_start'].isoformat(),
                    'last_activity': self.agent_metrics['last_activity'].isoformat()
                },
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.mode_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving mode state: {e}")
    
    def get_current_mode(self) -> str:
        """Get current operation mode"""
        return self.current_mode.value
    
    def switch_mode(self, new_mode: str) -> bool:
        """Switch to a new operation mode"""
        try:
            # Validate new mode
            try:
                target_mode = OperationMode(new_mode.lower())
            except ValueError:
                print(f"❌ Invalid mode: {new_mode}")
                return False
            
            # Check if already in target mode
            if self.current_mode == target_mode:
                print(f"ℹ️ Already in {target_mode.value} mode")
                return True
            
            # Record mode change
            old_mode = self.current_mode.value
            self.current_mode = target_mode
            
            # Add to history
            self.mode_history.append({
                'from_mode': old_mode,
                'to_mode': target_mode.value,
                'timestamp': datetime.now().isoformat(),
                'reason': 'user_request'
            })
            
            # Update metrics based on mode change
            if target_mode == OperationMode.AGENT:
                self._activate_agent_mode()
            else:
                self._activate_assistant_mode()
            
            # Save state
            self._save_mode_state()
            
            print(f"🔄 Switched from {old_mode} to {target_mode.value} mode")
            return True
            
        except Exception as e:
            print(f"❌ Error switching mode: {e}")
            return False
    
    def _activate_agent_mode(self):
        """Activate agent mode - background monitoring and automation"""
        self.agent_metrics.update({
            'last_activity': datetime.now(),
            'active_processes': 3,
            'efficiency_score': min(self.agent_metrics['efficiency_score'] + 5, 100)
        })
        print("🤖 Agent mode activated - monitoring and automation enabled")
    
    def _activate_assistant_mode(self):
        """Activate assistant mode - direct conversation focus"""
        self.agent_metrics.update({
            'last_activity': datetime.now(),
            'active_processes': 1  # Focused on conversation
        })
        print("💬 Assistant mode activated - conversation focus enabled")
    
    def get_agent_status(self) -> Dict:
        """Get detailed agent status"""
        try:
            uptime_minutes = (datetime.now() - self.agent_metrics['uptime_start']).total_seconds() / 60
            
            status = {
                'is_active': self.current_mode == OperationMode.AGENT,
                'current_mode': self.current_mode.value,
                'uptime_minutes': round(uptime_minutes, 1),
                'last_activity': self.agent_metrics['last_activity'].isoformat(),
                'tasks_processed': self.agent_metrics['tasks_processed'],
                'efficiency_score': self.agent_metrics['efficiency_score'],
                'active_processes': self.agent_metrics['active_processes'],
                'insights_generated': self.agent_metrics['insights_generated']
            }
            
            return status
            
        except Exception as e:
            print(f"Error getting agent status: {e}")
            return {
                'is_active': False,
                'current_mode': 'unknown',
                'error': str(e)
            }
    
    def get_agent_metrics(self) -> Dict:
        """Get agent performance metrics"""
        try:
            uptime_minutes = (datetime.now() - self.agent_metrics['uptime_start']).total_seconds() / 60
            
            # Calculate productivity metrics
            avg_tasks_per_hour = (self.agent_metrics['tasks_processed'] / max(uptime_minutes / 60, 1))
            
            return {
                'tasks_processed': self.agent_metrics['tasks_processed'],
                'efficiency_score': self.agent_metrics['efficiency_score'],
                'active_processes': self.agent_metrics['active_processes'],
                'insights_generated': self.agent_metrics['insights_generated'],
                'uptime_minutes': round(uptime_minutes, 1),
                'avg_tasks_per_hour': round(avg_tasks_per_hour, 1),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting agent metrics: {e}")
            return {
                'tasks_processed': 0,
                'efficiency_score': 0,
                'active_processes': 0,
                'insights_generated': 0,
                'uptime_minutes': 0,
                'avg_tasks_per_hour': 0,
                'error': str(e)
            }
    
    def update_agent_metrics(self, **updates):
        """Update agent metrics"""
        try:
            self.agent_metrics.update(updates)
            self.agent_metrics['last_activity'] = datetime.now()
            self._save_mode_state()
            
        except Exception as e:
            print(f"Error updating agent metrics: {e}")
    
    def increment_tasks_processed(self, count: int = 1):
        """Increment tasks processed counter"""
        try:
            self.agent_metrics['tasks_processed'] += count
            self.agent_metrics['last_activity'] = datetime.now()
            
            # Slight efficiency boost for activity
            self.agent_metrics['efficiency_score'] = min(
                self.agent_metrics['efficiency_score'] + 1, 100
            )
            
            self._save_mode_state()
            
        except Exception as e:
            print(f"Error incrementing tasks: {e}")
    
    def increment_insights_generated(self, count: int = 1):
        """Increment insights generated counter"""
        try:
            self.agent_metrics['insights_generated'] += count
            self.agent_metrics['last_activity'] = datetime.now()
            self._save_mode_state()
            
        except Exception as e:
            print(f"Error incrementing insights: {e}")
    
    def get_mode_history(self, limit: int = 10) -> List[Dict]:
        """Get recent mode change history"""
        try:
            return self.mode_history[-limit:] if limit > 0 else self.mode_history
        except Exception as e:
            print(f"Error getting mode history: {e}")
            return []
    
    def get_mode_stats(self) -> Dict:
        """Get mode usage statistics"""
        try:
            total_switches = len(self.mode_history)
            
            # Count time in each mode
            agent_time = 0
            assistant_time = 0
            current_session_start = self.agent_metrics['uptime_start']
            
            if self.mode_history:
                # Calculate time in each mode based on history
                for i, change in enumerate(self.mode_history):
                    if i == 0:
                        continue  # Skip first entry
                    
                    prev_change = self.mode_history[i-1]
                    change_time = datetime.fromisoformat(change['timestamp'])
                    prev_time = datetime.fromisoformat(prev_change['timestamp'])
                    
                    duration = (change_time - prev_time).total_seconds() / 60  # minutes
                    
                    if prev_change['to_mode'] == 'agent':
                        agent_time += duration
                    else:
                        assistant_time += duration
            
            # Add current session time
            current_duration = (datetime.now() - current_session_start).total_seconds() / 60
            if self.current_mode == OperationMode.AGENT:
                agent_time += current_duration
            else:
                assistant_time += current_duration
            
            total_time = agent_time + assistant_time
            
            return {
                'total_mode_switches': total_switches,
                'current_mode': self.current_mode.value,
                'agent_time_minutes': round(agent_time, 1),
                'assistant_time_minutes': round(assistant_time, 1),
                'agent_percentage': round((agent_time / max(total_time, 1)) * 100, 1),
                'assistant_percentage': round((assistant_time / max(total_time, 1)) * 100, 1),
                'session_start': current_session_start.isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting mode stats: {e}")
            return {
                'total_mode_switches': 0,
                'current_mode': self.current_mode.value,
                'error': str(e)
            }
    
    def reset_metrics(self):
        """Reset agent metrics (for testing or fresh start)"""
        try:
            self.agent_metrics = {
                "tasks_processed": 0,
                "efficiency_score": 85,
                "active_processes": 3 if self.current_mode == OperationMode.AGENT else 1,
                "insights_generated": 0,
                "uptime_start": datetime.now(),
                "last_activity": datetime.now()
            }
            
            self._save_mode_state()
            print("🔄 Agent metrics reset")
            
        except Exception as e:
            print(f"Error resetting metrics: {e}")