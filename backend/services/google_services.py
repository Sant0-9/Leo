#!/usr/bin/env python3
"""
Google Services Integration for Leo AI Assistant
Handles Google Calendar, Gmail, and Tasks APIs
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

class GoogleServices:
    def __init__(self):
        self.credentials_file = "credentials.json"
        self.token_file = "token.json"
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/tasks.readonly'
        ]
        
        self.calendar_service = None
        self.gmail_service = None
        self.tasks_service = None
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services"""
        try:
            creds = self._get_credentials()
            if creds:
                self.calendar_service = build('calendar', 'v3', credentials=creds)
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                self.tasks_service = build('tasks', 'v1', credentials=creds)
                print("✅ Google services initialized successfully")
            else:
                print("⚠️ Google credentials not available - using mock data")
        except Exception as e:
            print(f"⚠️ Failed to initialize Google services: {e}")
            print("📝 Using mock data for demonstration")
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get Google API credentials"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If credentials are not valid, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    return None
            else:
                # Need to get new credentials
                if os.path.exists(self.credentials_file):
                    try:
                        flow = Flow.from_client_secrets_file(
                            self.credentials_file, self.scopes)
                        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                        
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        print(f"Please visit this URL to authorize: {auth_url}")
                        
                        # In a real implementation, you'd handle this flow properly
                        # For now, return None to use mock data
                        return None
                    except Exception as e:
                        print(f"Error setting up OAuth flow: {e}")
                        return None
                else:
                    print(f"Credentials file {self.credentials_file} not found")
                    return None
        
        return creds
    
    def health_check(self) -> Dict:
        """Check if Google services are healthy"""
        services_status = {
            "calendar": "disconnected",
            "gmail": "disconnected", 
            "tasks": "disconnected"
        }
        
        if self.calendar_service:
            services_status["calendar"] = "connected"
        if self.gmail_service:
            services_status["gmail"] = "connected"
        if self.tasks_service:
            services_status["tasks"] = "connected"
            
        return services_status
    
    def get_calendar_events(self, max_results: int = 10) -> List[Dict]:
        """Get upcoming calendar events"""
        if not self.calendar_service:
            return self._get_mock_calendar_events()
        
        try:
            # Get events from primary calendar
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event.get('id'),
                    'title': event.get('summary', 'No Title'),
                    'start': start,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', []))
                })
            
            return formatted_events
            
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return self._get_mock_calendar_events()
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return self._get_mock_calendar_events()
    
    def get_gmail_data(self) -> Dict:
        """Get Gmail data summary"""
        if not self.gmail_service:
            return self._get_mock_gmail_data()
        
        try:
            # Get unread messages count
            unread_query = 'is:unread'
            unread_result = self.gmail_service.users().messages().list(
                userId='me', q=unread_query
            ).execute()
            
            unread_count = len(unread_result.get('messages', []))
            
            # Get today's messages count  
            today = datetime.now().strftime('%Y/%m/%d')
            today_query = f'after:{today}'
            today_result = self.gmail_service.users().messages().list(
                userId='me', q=today_query
            ).execute()
            
            today_count = len(today_result.get('messages', []))
            
            return {
                'status': 'healthy',
                'unread_count': unread_count,
                'today_count': today_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return self._get_mock_gmail_data()
        except Exception as e:
            print(f"Error getting Gmail data: {e}")
            return self._get_mock_gmail_data()
    
    def get_tasks(self) -> List[Dict]:
        """Get Google Tasks"""
        if not self.tasks_service:
            return self._get_mock_tasks()
        
        try:
            # Get task lists
            tasklists = self.tasks_service.tasklists().list().execute()
            
            all_tasks = []
            for tasklist in tasklists.get('items', []):
                # Get tasks from each list
                tasks = self.tasks_service.tasks().list(
                    tasklist=tasklist['id']
                ).execute()
                
                for task in tasks.get('items', []):
                    all_tasks.append({
                        'id': task.get('id'),
                        'title': task.get('title'),
                        'status': task.get('status'),
                        'due': task.get('due'),
                        'notes': task.get('notes', ''),
                        'list_name': tasklist.get('title')
                    })
            
            return all_tasks
            
        except HttpError as error:
            print(f"Tasks API error: {error}")
            return self._get_mock_tasks()
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return self._get_mock_tasks()
    
    def get_all_data(self) -> Dict:
        """Get all Google services data"""
        return {
            'calendar': {
                'status': 'healthy' if self.calendar_service else 'disconnected',
                'events': self.get_calendar_events(),
                'total_count': len(self.get_calendar_events())
            },
            'gmail': self.get_gmail_data(),
            'tasks': {
                'status': 'healthy' if self.tasks_service else 'disconnected',
                'tasks': self.get_tasks(),
                'total_count': len(self.get_tasks())
            },
            'last_updated': datetime.now().isoformat()
        }
    
    # Mock data methods for when APIs are not available
    def _get_mock_calendar_events(self) -> List[Dict]:
        """Get mock calendar events for demo"""
        base_time = datetime.now()
        return [
            {
                'id': 'mock1',
                'title': 'Team Standup',
                'start': (base_time + timedelta(hours=1)).isoformat(),
                'description': 'Daily team sync meeting',
                'location': 'Conference Room A',
                'attendees': 5
            },
            {
                'id': 'mock2', 
                'title': 'Project Review',
                'start': (base_time + timedelta(hours=3)).isoformat(),
                'description': 'Review Q4 project progress',
                'location': 'Virtual Meeting',
                'attendees': 8
            },
            {
                'id': 'mock3',
                'title': 'Leo Development Session',
                'start': (base_time + timedelta(days=1)).isoformat(),
                'description': 'Continue building Leo features',
                'location': 'Home Office',
                'attendees': 1
            }
        ]
    
    def _get_mock_gmail_data(self) -> Dict:
        """Get mock Gmail data for demo"""
        import random
        return {
            'status': 'healthy',
            'unread_count': random.randint(5, 25),
            'today_count': random.randint(10, 40),
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_mock_tasks(self) -> List[Dict]:
        """Get mock tasks for demo"""
        return [
            {
                'id': 'task1',
                'title': 'Complete Leo frontend rebuild',
                'status': 'needsAction',
                'due': (datetime.now() + timedelta(days=1)).isoformat(),
                'notes': 'Focus on modern React components',
                'list_name': 'Work Tasks'
            },
            {
                'id': 'task2',
                'title': 'Set up ChromaDB integration',
                'status': 'needsAction', 
                'due': (datetime.now() + timedelta(days=2)).isoformat(),
                'notes': 'Long-term memory for Leo',
                'list_name': 'Work Tasks'
            },
            {
                'id': 'task3',
                'title': 'Test Google API integrations',
                'status': 'completed',
                'due': datetime.now().isoformat(),
                'notes': 'Verify all services work correctly',
                'list_name': 'Work Tasks'
            }
        ]