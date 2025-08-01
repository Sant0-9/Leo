import streamlit as st
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.research_agent import ResearchAgent
from utils.chat_ui import ChatUI
from utils.formatter import format_plan

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="LifeOS - AI Productivity Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .goal-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .progress-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px 10px 0 0;
        margin-bottom: 0;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 0 0 10px 10px;
        padding: 1rem;
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = set()
if 'goal_history' not in st.session_state:
    st.session_state.goal_history = []
if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 0
if 'last_completion_date' not in st.session_state:
    st.session_state.last_completion_date = None
if 'ai_insights' not in st.session_state:
    st.session_state.ai_insights = []
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = "GPT-3.5 Turbo"
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = False
if 'chat_ui' not in st.session_state:
    st.session_state.chat_ui = ChatUI(st.session_state.ai_model)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧠 LifeOS: Your AI Productivity Assistant</h1>
    <p>Transform your goals into actionable plans with AI-powered productivity</p>
</div>
""", unsafe_allow_html=True)

# Left sidebar navigation
with st.sidebar:
    st.title("🧠 LifeOS")
    st.markdown("Your AI Productivity Assistant")
    
    # Navigation
    page = st.selectbox(
        "Navigation:",
        ["Create New Goal", "Current Plan", "Progress Dashboard", "AI Insights", "Goal History", "Settings"]
    )
    
    # Quick Stats
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    if st.session_state.current_plan:
        total_tasks = sum(len(week.get("tasks", [])) for week in st.session_state.current_plan.get("weeks", []))
        completed_count = len(st.session_state.completed_tasks)
        progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        st.metric("Tasks Completed", f"{completed_count}/{total_tasks}")
        st.progress(progress / 100)
        st.metric("Streak Days", st.session_state.streak_days)
    
    # AI Assistant toggle
    st.markdown("---")
    if st.button("💬 Open AI Assistant"):
        st.session_state.chat_mode = not st.session_state.chat_mode
        st.rerun()

# Main content area
if st.session_state.chat_mode:
    # Full-page chat interface using ChatUI
    st.session_state.chat_ui.render_chat_interface()

else:
    # Regular LifeOS content based on selected page
    if page == "Create New Goal":
        st.header("🎯 Create Your Goal")
        
        # Goal creation form
        with st.form(key="goal_form"):
            st.subheader("📝 Goal Details")
            
            # Goal input
            goal = st.text_area(
                "What's your main goal?",
                placeholder="e.g. I want to get a summer internship and lose weight in 30 days",
                height=100
            )
            
            # Goal parameters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                goal_category = st.selectbox(
                    "Goal Category:",
                    ["Career", "Health & Fitness", "Learning", "Personal", "Financial", "Relationships"]
                )
            
            with col2:
                priority = st.selectbox(
                    "Priority Level:",
                    ["High", "Medium", "Low"]
                )
            
            with col3:
                timeline = st.selectbox(
                    "Timeline:",
                    ["1 week", "2 weeks", "1 month", "3 months", "6 months", "1 year"]
                )
            
            # Generate plan button
            if st.form_submit_button("🚀 Generate My Plan", type="primary"):
                if goal:
                    with st.spinner("🤖 Creating your personalized plan..."):
                        try:
                            # Create enhanced prompt
                            enhanced_prompt = f"""
                            Create a detailed, personalized plan for this goal: "{goal}"
                            
                            Context:
                            - Category: {goal_category}
                            - Timeline: {timeline}
                            - Priority: {priority}
                            
                            Please create a plan that:
                            1. Fits their timeline
                            2. Is realistic and achievable
                            3. Provides clear, actionable steps
                            4. Breaks down into weekly and daily tasks
                            
                            Return a Python dict with this structure:
                            {{'weeks': [{{'week': 1, 'tasks': [{{'day': 'Monday', 'task': '...'}}, ...]}}, ...]}}
                            """
                            
                            # Generate plan using agents with proper model mapping
                            planner = PlannerAgent(OPENAI_API_KEY, st.session_state.ai_model)
                            scheduler = SchedulerAgent()
                            researcher = ResearchAgent()
                            
                            # Map friendly model names to actual API model names
                            model_mapping = {
                                "GPT-3.5 Turbo": "gpt-3.5-turbo",
                                "GPT-4": "gpt-4",
                                "GPT-4 Turbo": "gpt-4-turbo-preview",
                                "Claude-3": "gpt-4"  # Fallback to GPT-4 for Claude-3 for now
                            }
                            
                            actual_model = model_mapping.get(st.session_state.ai_model, "gpt-3.5-turbo")
                            
                            response = planner.client.chat.completions.create(
                                model=actual_model,
                                messages=[
                                    {"role": "system", "content": enhanced_prompt},
                                    {"role": "user", "content": goal}
                                ],
                                max_tokens=800,
                                temperature=0.7
                            )
                            
                            # Safely parse the response without using eval()
                            import json
                            try:
                                plan = json.loads(response.choices[0].message.content)
                            except json.JSONDecodeError:
                                # Fallback to a safe default plan
                                plan = {
                                    "weeks": [
                                        {
                                            "week": 1,
                                            "tasks": [
                                                {"day": "Monday", "task": "Start working on your goal"},
                                                {"day": "Tuesday", "task": "Continue progress"},
                                                {"day": "Wednesday", "task": "Review and adjust"},
                                                {"day": "Thursday", "task": "Deep work session"},
                                                {"day": "Friday", "task": "Weekly review and planning"}
                                            ]
                                        }
                                    ]
                                }
                            
                            # Enhance plan with scheduling and resources
                            plan = scheduler.schedule(plan)
                            plan = researcher.enrich(plan)
                            
                            # Add metadata
                            plan['metadata'] = {
                                'goal': goal,
                                'category': goal_category,
                                'priority': priority,
                                'timeline': timeline,
                                'created_at': datetime.now().isoformat()
                            }
                            
                            st.session_state.current_plan = plan
                            st.session_state.completed_tasks = set()
                            
                            # Add to history
                            st.session_state.goal_history.append({
                                'goal': goal,
                                'category': goal_category,
                                'created_at': datetime.now().isoformat(),
                                'plan': plan
                            })
                            
                            st.success("🎉 Your personalized plan has been created!")
                            st.balloons()
                            
                            # Show plan preview
                            st.subheader("📋 Plan Preview")
                            st.markdown(format_plan(plan))
                            
                        except Exception as e:
                            st.error(f"❌ Error generating plan: {str(e)}")
                else:
                    st.warning("Please enter your goal to continue.")

    elif page == "Current Plan":
        st.header("📋 Current Plan")
        
        if st.session_state.current_plan:
            # Display plan metadata
            metadata = st.session_state.current_plan.get('metadata', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 Goal</h3>
                    <p>{metadata.get('goal', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📂 Category</h3>
                    <p>{metadata.get('category', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⏰ Timeline</h3>
                    <p>{metadata.get('timeline', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display weekly plan
            for week in st.session_state.current_plan.get("weeks", []):
                st.subheader(f"📅 Week {week['week']}")
                
                for task in week.get("tasks", []):
                    task_id = f"{week['week']}_{task['day']}_{task['task']}"
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        completed = st.checkbox(
                            task['task'],
                            value=task_id in st.session_state.completed_tasks,
                            key=task_id,
                            label_visibility="collapsed"
                        )
                        
                        # Update completed tasks
                        if completed and task_id not in st.session_state.completed_tasks:
                            st.session_state.completed_tasks.add(task_id)
                            # Update streak
                            today = datetime.now().date()
                            if st.session_state.last_completion_date != today:
                                st.session_state.streak_days += 1
                                st.session_state.last_completion_date = today
                        elif not completed and task_id in st.session_state.completed_tasks:
                            st.session_state.completed_tasks.remove(task_id)
                    
                    with col2:
                        st.write(f"📅 {task['day']}")
                    
                    with col3:
                        st.write(f"⏰ {task.get('time_block', 'N/A')}")
                    
                    with col4:
                        st.write(f"⭐ {task.get('priority', 'N/A')}")
                    
                    # Display resources if available
                    if task.get('resources'):
                        with st.expander("📚 Resources"):
                            for resource in task['resources']:
                                st.markdown(f"- [{resource['title']}]({resource['url']})")
                    
                    st.markdown("---")
        else:
            st.info("No active plan. Create a new goal to get started!")

    elif page == "Progress Dashboard":
        st.header("📊 Progress Dashboard")
        
        if st.session_state.current_plan:
            # Calculate progress metrics
            total_tasks = sum(len(week.get("tasks", [])) for week in st.session_state.current_plan.get("weeks", []))
            completed_count = len(st.session_state.completed_tasks)
            progress_percentage = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
            
            # Progress overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tasks", total_tasks)
            
            with col2:
                st.metric("Completed", completed_count)
            
            with col3:
                st.metric("Progress", f"{progress_percentage:.1f}%")
            
            with col4:
                st.metric("Streak Days", st.session_state.streak_days)
            
            # Progress bar
            st.progress(progress_percentage / 100)
            
            # Progress chart
            if total_tasks > 0:
                fig = go.Figure(data=[
                    go.Bar(name='Completed', x=['Tasks'], y=[completed_count], marker_color='#4facfe'),
                    go.Bar(name='Remaining', x=['Tasks'], y=[total_tasks - completed_count], marker_color='#f093fb')
                ])
                fig.update_layout(title="Task Completion Progress", barmode='stack')
                st.plotly_chart(fig, use_container_width=True)
            
            # Weekly breakdown
            st.subheader("📅 Weekly Breakdown")
            
            weekly_data = []
            for week in st.session_state.current_plan.get("weeks", []):
                week_tasks = week.get("tasks", [])
                week_completed = sum(1 for task in week_tasks 
                                   if f"{week['week']}_{task['day']}_{task['task']}" in st.session_state.completed_tasks)
                weekly_data.append({
                    'Week': f"Week {week['week']}",
                    'Total Tasks': len(week_tasks),
                    'Completed': week_completed,
                    'Progress': (week_completed / len(week_tasks) * 100) if week_tasks else 0
                })
            
            if weekly_data:
                fig = px.bar(weekly_data, x='Week', y=['Completed', 'Total Tasks'], 
                            title="Weekly Task Progress", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active plan to display progress for.")

    elif page == "AI Insights":
        st.header("🧠 AI Insights")
        
        if st.session_state.current_plan:
            # Generate insights based on current progress
            total_tasks = sum(len(week.get("tasks", [])) for week in st.session_state.current_plan.get("weeks", []))
            completed_count = len(st.session_state.completed_tasks)
            progress_percentage = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
            
            # Insight cards
            col1, col2 = st.columns(2)
            
            with col1:
                if progress_percentage >= 80:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>🎉 Amazing Progress!</h3>
                        <p>You're crushing it! You've completed over 80% of your tasks. Keep up the momentum!</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif progress_percentage >= 50:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>🚀 Great Work!</h3>
                        <p>You're halfway there! You've made solid progress on your goals. Keep pushing forward!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>💪 Getting Started!</h3>
                        <p>Every journey begins with a single step. You're building momentum - keep going!</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if st.session_state.streak_days >= 7:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>🔥 Streak Master!</h3>
                        <p>You've maintained a {}-day streak! Consistency is the key to success.</p>
                    </div>
                    """.format(st.session_state.streak_days), unsafe_allow_html=True)
                elif st.session_state.streak_days >= 3:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>⭐ Building Habits!</h3>
                        <p>You're building a {}-day streak! Great habits are forming.</p>
                    </div>
                    """.format(st.session_state.streak_days), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="insight-card">
                        <h3>🌟 New Beginning!</h3>
                        <p>You're starting your productivity journey. Every day counts!</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            
            if progress_percentage < 30:
                st.markdown("""
                <div class="goal-card">
                    <h3>🎯 Focus on Small Wins</h3>
                    <p>Start with the easiest tasks to build momentum. Even completing one small task can boost your motivation!</p>
                </div>
                """, unsafe_allow_html=True)
            elif progress_percentage < 70:
                st.markdown("""
                <div class="goal-card">
                    <h3>⚡ Maintain Momentum</h3>
                    <p>You're making good progress! Try to tackle one challenging task each day to keep moving forward.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="goal-card">
                    <h3>🏆 Final Push</h3>
                    <p>You're so close to your goal! Focus on the remaining tasks and celebrate your achievements.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Create a plan to see personalized AI insights!")

    elif page == "Goal History":
        st.header("📚 Goal History")
        
        if st.session_state.goal_history:
            for i, goal in enumerate(reversed(st.session_state.goal_history)):
                with st.expander(f"🎯 {goal['goal']} ({goal['category']}) - {goal['created_at'][:10]}"):
                    st.write(f"**Category:** {goal['category']}")
                    st.write(f"**Created:** {goal['created_at']}")
                    
                    if st.button(f"View Plan {i+1}", key=f"view_plan_{i}"):
                        st.session_state.current_plan = goal['plan']
                        st.session_state.completed_tasks = set()
                        st.success("Plan loaded! Check the 'Current Plan' tab.")
        else:
            st.info("No goal history yet. Create your first goal to get started!")

    elif page == "Settings":
        st.header("⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 AI Configuration")
            
            # AI Model Selection
            ai_model = st.selectbox(
                "AI Model:",
                ["GPT-3.5 Turbo", "GPT-4", "GPT-4 Turbo"],
                index=0
            )
            
            # Update AI model if changed
            if ai_model != st.session_state.ai_model:
                st.session_state.ai_model = ai_model
                st.session_state.chat_ui = ChatUI(ai_model)
            
            st.subheader("🎨 Appearance")
            theme = st.selectbox("Theme:", ["Light", "Dark", "Default"], index=0)
            st.session_state.theme = theme
            
            st.subheader("📊 Data Management")
            
            # Export functionality
            if st.button("Export Data"):
                if st.session_state.current_plan or st.session_state.goal_history:
                    export_data = {
                        'current_plan': st.session_state.current_plan,
                        'goal_history': st.session_state.goal_history,
                        'completed_tasks': list(st.session_state.completed_tasks),
                        'streak_days': st.session_state.streak_days,
                        'export_date': datetime.now().isoformat()
                    }
                    
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"lifeos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No data to export")
            
            # Import functionality
            uploaded_file = st.file_uploader("Import Data", type=['json'])
            if uploaded_file:
                try:
                    data = json.load(uploaded_file)
                    st.session_state.current_plan = data.get('current_plan')
                    st.session_state.completed_tasks = set(data.get('completed_tasks', []))
                    st.session_state.goal_history = data.get('goal_history', [])
                    st.session_state.streak_days = data.get('streak_days', 0)
                    st.success("Data imported successfully!")
                except Exception as e:
                    st.error(f"Error importing data: {str(e)}")
        
        with col2:
            st.subheader("🔄 Reset")
            if st.button("Clear All Data", type="primary"):
                st.session_state.current_plan = None
                st.session_state.completed_tasks = set()
                st.session_state.goal_history = []
                st.session_state.streak_days = 0
                st.session_state.last_completion_date = None
                st.session_state.ai_insights = []
                st.session_state.chat_ui.reset_chat()
                st.success("All data cleared!")
            
            st.subheader("ℹ️ About")
            st.write("**LifeOS v1.0**")
            st.write("Your AI-powered productivity assistant")
            st.write("Built with Streamlit and OpenAI")
            
            st.subheader("📈 Current Stats")
            if st.session_state.current_plan:
                total_tasks = sum(len(week.get("tasks", [])) for week in st.session_state.current_plan.get("weeks", []))
                completed_count = len(st.session_state.completed_tasks)
                st.write(f"**Active Plan:** {st.session_state.current_plan.get('metadata', {}).get('goal', 'N/A')}")
                st.write(f"**Tasks Completed:** {completed_count}/{total_tasks}")
                st.write(f"**Streak Days:** {st.session_state.streak_days}")
                st.write(f"**Total Goals:** {len(st.session_state.goal_history)}")
            else:
                st.write("No active plan")
                st.write(f"**Total Goals:** {len(st.session_state.goal_history)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧠 LifeOS - Powered by AI Agents | Built with ❤️ for productivity</p>
</div>
""", unsafe_allow_html=True)
