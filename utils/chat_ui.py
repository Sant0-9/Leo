import streamlit as st
from typing import List, Dict, Optional
from agents.smart_assistant import SmartAssistant, AssistantState
from agents.goal_flow import GoalFlow

class ChatUI:
    def __init__(self, ai_model: str = "GPT-3.5 Turbo"):
        self.ai_model = ai_model
        self.chat_agent = SmartAssistant(ai_model)
        self.goal_flow = GoalFlow(ai_model)
    
    def render_chat_interface(self) -> None:
        """Render the full-page chat interface"""
        # Add custom CSS for better styling
        st.markdown("""
        <style>
        .chat-input-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            border: 1px solid #e9ecef;
        }
        .stTextArea textarea {
            border-radius: 8px !important;
            border: 2px solid #e9ecef !important;
            transition: border-color 0.3s ease;
        }
        .stTextArea textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Chat header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 2rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2>💬 AI Assistant</h2>
            <p>Your productivity companion - ask me anything!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat history directly
        self._display_chat_history()
        
        # Chat input and controls
        st.markdown("---")
        self._render_chat_controls()
    
    def _display_chat_history(self) -> None:
        """Display the chat history using Streamlit's chat components"""
        chat_history = self.chat_agent.get_chat_history()
        
        if not chat_history:
            # Show initial greeting
            with st.chat_message("assistant", avatar="🤖"):
                st.write("Hey there! 👋 What's on your mind today?")
        
        else:
            # Display all messages in chat history
            for message in chat_history:
                if message["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(message["content"])
                else:
                    with st.chat_message("user", avatar="👤"):
                        st.write(message["content"])
    
    def _render_chat_controls(self) -> None:
        """Render chat input and control buttons"""
        # Initialize session state for input
        if 'chat_input_key' not in st.session_state:
            st.session_state.chat_input_key = 0
        
        # Create a form for better input handling
        with st.form(key=f"chat_form_{st.session_state.chat_input_key}", clear_on_submit=True):
            # Input area
            user_input = st.text_area(
                "Type your message here...",
                placeholder="Ask me anything or create a goal...",
                height=60,
                key=f"chat_input_{st.session_state.chat_input_key}",
                label_visibility="collapsed"
            )
            
            # Button row
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # Send button (primary)
                send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
            
            with col2:
                # Clear button
                clear_button = st.form_submit_button("🗑️ Clear", use_container_width=True)
            
            with col3:
                # Back button
                back_button = st.form_submit_button("🔙 Back", use_container_width=True)
            
            with col4:
                # Enter key hint
                st.markdown("""
                <div style="text-align: center; color: #6c757d; font-size: 0.8em; padding: 0.5rem;">
                    Press Enter to send
                </div>
                """, unsafe_allow_html=True)
            
            # Handle form submission
            if send_button and user_input.strip():
                self._handle_user_input(user_input.strip())
                # Increment key to force re-render and maintain focus
                st.session_state.chat_input_key += 1
                st.rerun()
            
            # Handle clear button
            if clear_button:
                self.chat_agent.reset_conversation()
                st.session_state.chat_input_key += 1
                st.rerun()
            
            # Handle back button
            if back_button:
                st.session_state.chat_mode = False
                st.rerun()
    
    def _handle_user_input(self, user_message: str) -> None:
        """Handle user input and generate response"""
        # Get response from chat agent
        response = self.chat_agent.handle_message(user_message)
        
        # Check if ready for plan generation
        if self.chat_agent.is_ready_for_planning():
            self._handle_plan_generation()
        
        st.rerun()
    
    def _handle_plan_generation(self) -> None:
        """Handle plan generation when chat agent is ready"""
        user_data = self.chat_agent.get_user_data()
        
        # Convert user_data to goal_context format for compatibility
        goal_context = {
            "goal": user_data.get("goal", ""),
            "importance": user_data.get("importance", ""),
            "timeline": user_data.get("timeline", "1_month"),
            "preferences": user_data.get("preferences", ""),
            "seriousness": "high" if user_data.get("confirmed") else "medium",
            "reminders": "daily"
        }
        
        # Validate goal context
        validated_context = self.goal_flow.validate_goal_context(goal_context)
        
        # Generate plan
        with st.spinner("🤖 Generating your personalized plan..."):
            plan = self.goal_flow.generate_plan_from_context(validated_context)
            
            # Store plan in session state
            st.session_state.current_plan = plan
            st.session_state.completed_tasks = set()
            
            # Add to goal history
            if 'goal_history' not in st.session_state:
                st.session_state.goal_history = []
            
            st.session_state.goal_history.append({
                'goal': validated_context.get("goal", ""),
                'category': 'Personal',  # Default category
                'created_at': plan.get('metadata', {}).get('created_at', ''),
                'plan': plan
            })
            
            # Add success message to chat
            success_message = f"""🎉 Perfect! I've created your personalized plan for: "{validated_context.get('goal', 'your goal')}"

You can view your plan in the 'Current Plan' section. What would you like to work on next?"""
            
            self.chat_agent.chat_history.append({
                "role": "assistant",
                "content": success_message,
                "timestamp": None
            })
            
            # Reset conversation state but keep context
            self.chat_agent.current_state = AssistantState.CASUAL_CHAT
    
    def render_sidebar_chat(self) -> None:
        """Render a compact chat interface in the sidebar"""
        st.markdown("### 💬 AI Assistant")
        
        # Display recent messages (last 5)
        chat_history = self.chat_agent.get_chat_history()
        recent_messages = chat_history[-10:] if len(chat_history) > 10 else chat_history
        
        for message in recent_messages:
            if message["role"] == "assistant":
                st.markdown(f"""
                <div style="margin: 5px 0; padding: 8px; background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; border-radius: 6px; font-size: 0.8em;">
                    <strong>🤖 AI:</strong><br>
                    {message["content"][:100]}{"..." if len(message["content"]) > 100 else ""}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin: 5px 0; padding: 8px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; font-size: 0.8em;">
                    <strong>👤 You:</strong><br>
                    {message["content"][:100]}{"..." if len(message["content"]) > 100 else ""}
                </div>
                """, unsafe_allow_html=True)
        
        # Compact input
        with st.form(key="sidebar_chat_form", clear_on_submit=True):
            user_input = st.text_area("Message:", placeholder="Type here...", height=60, key="sidebar_input")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                send_button = st.form_submit_button("Send", type="primary")
            
            with col2:
                clear_button = st.form_submit_button("Clear")
        
        # Handle form submissions
        if send_button and user_input:
            self._handle_user_input(user_input)
            st.rerun()
        
        elif clear_button:
            self.chat_agent.reset_conversation()
            st.rerun()
    
    def get_chat_agent(self) -> SmartAssistant:
        """Get the chat agent instance"""
        return self.chat_agent
    
    def get_goal_flow(self) -> GoalFlow:
        """Get the goal flow instance"""
        return self.goal_flow
    
    def reset_chat(self) -> None:
        """Reset the chat agent"""
        self.chat_agent.reset_conversation()
    
    def is_ready_for_planning(self) -> bool:
        """Check if ready for plan generation"""
        return self.chat_agent.is_ready_for_planning()
    
    def get_user_data(self) -> Dict:
        """Get current user data"""
        return self.chat_agent.get_user_data() 