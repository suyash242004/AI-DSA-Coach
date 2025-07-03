import streamlit as st
import json
from agents.mentor_agent import MentorAgent
from agents.code_agent import CodeAgent
from agents.evaluation_agent import EvaluationAgent
from agents.persona_agent import PersonaAgent
from agents.orchestrator import AgentOrchestrator
from utils.gemini_client import get_gemini_model

# Page configuration
st.set_page_config(
    page_title="AI DSA Coach", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for LeetCode-like styling
st.markdown("""
<style>
    /* Hide default sidebar */
    .css-1d391kg {display: none;}
    
    /* Main container styling */
    .main-container {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top navigation bar */
    .top-nav {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Problem card styling */
    .problem-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .problem-title {
        font-size: 24px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 16px;
    }
    
    .difficulty-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    
    .difficulty-easy { background-color: #d4edda; color: #155724; }
    .difficulty-medium { background-color: #fff3cd; color: #856404; }
    .difficulty-hard { background-color: #f8d7da; color: #721c24; }
    
    .problem-description {
        line-height: 1.6;
        color: #4a5568;
        font-size: 16px;
        margin-bottom: 20px;
    }
    
    /* Code editor styling */
    .code-editor-container {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 0;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    .code-header {
        background: #2d2d2d;
        padding: 12px 16px;
        border-radius: 8px 8px 0 0;
        border-bottom: 1px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .language-selector {
        background: #3a3a3a;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
    }
    
    .chat-message {
        margin-bottom: 12px;
        padding: 12px;
        border-radius: 8px;
    }
    
    .user-message {
        background: #e3f2fd;
        border-left: 3px solid #2196f3;
        color: #1a202c;
    }
    
    .mentor-message {
        background: #f3e5f5;
        border-left: 3px solid #9c27b0;
        color: #1a202c;
    }
    
    .agent-message {
        background: #e8f5e8;
        border-left: 3px solid #4caf50;
        color: #1a202c;
    }
    
    /* Button styling */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .status-mentoring { background: #fef7e0; color: #92400e; }
    .status-coding { background: #e0f2fe; color: #0d47a1; }
    .status-evaluation { background: #e8f5e8; color: #2e7d32; }
    
    /* Examples styling */
    .example-container {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .example-title {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
    }
    
    .example-code {
        background: #2d3748;
        color: #e2e8f0;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# Programming language templates
LANGUAGE_TEMPLATES = {
    "Python": """def solution():
    # Write your solution here
    pass

# Test your solution
if __name__ == "__main__":
    # Add test cases
    pass""",
    
    "Java": """public class Solution {
    public void solution() {
        // Write your solution here
    }
    
    public static void main(String[] args) {
        // Add test cases
    }
}""",
    
    "C++": """#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Solution {
public:
    void solution() {
        // Write your solution here
    }
};

int main() {
    // Add test cases
    return 0;
}""",
    
    "JavaScript": """function solution() {
    // Write your solution here
}

// Test your solution
console.log(solution());""",
    
    "Go": """package main

import "fmt"

func solution() {
    // Write your solution here
}

func main() {
    // Add test cases
}"""
}

# Load problems
@st.cache_data
def load_problems():
    try:
        with open("data/problems.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return sample problems if file doesn't exist
        return [
            {
                "title": "Two Sum",
                "difficulty": "Easy",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "examples": [
                    {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
                    {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
                ]
            }
        ]

problems = load_problems()

# Initialize session state
def initialize_session_state():
    defaults = {
        "orchestrator": AgentOrchestrator(),
        "mentor_agent": MentorAgent(),
        "code_agent": CodeAgent(),
        "evaluation_agent": EvaluationAgent(),
        "persona_agent": PersonaAgent(),
        "current_problem": None,
        "selected_language": "Python",
        "skill_level": None,
        "user_approach": "",
        "mentor_conversation": [],
        "code_conversation": [],
        "user_code": "",
        "hints_used": 0,
        "session_data": {},
        "approach_approved": False,
        "active_tab": "problem"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Top Navigation Bar
def render_top_nav():
    problem_titles = [p["title"] for p in problems]
    
    with st.container():
        st.markdown('<div class="top-nav">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.markdown("### 🧠 AI DSA Coach")
        
        with col2:
            selected_title = st.selectbox(
                "Problem:", 
                problem_titles, 
                key="problem_selector",
                label_visibility="collapsed"
            )
            
            if st.session_state.current_problem != selected_title:
                reset_session(selected_title)
        
        with col3:
            selected_lang = st.selectbox(
                "Language:",
                list(LANGUAGE_TEMPLATES.keys()),
                index=list(LANGUAGE_TEMPLATES.keys()).index(st.session_state.selected_language),
                key="lang_selector",
                label_visibility="collapsed"
            )
            
            if st.session_state.selected_language != selected_lang:
                st.session_state.selected_language = selected_lang
                if not st.session_state.user_code.strip():
                    st.session_state.user_code = LANGUAGE_TEMPLATES[selected_lang]
        
        with col4:
            # Show progress instead of just status
            progress = st.session_state.orchestrator.get_progress_summary()
            st.progress(progress["progress_percentage"] / 100, 
                        text=f"📍 {progress['current_phase']} ({progress['progress_percentage']}%)")
        
        with col5:
            if st.session_state.skill_level:
                skill_colors = {"Beginner": "#ff9800", "Intermediate": "#2196f3", "Advanced": "#4caf50"}
                color = skill_colors.get(st.session_state.skill_level, "#666")
                st.markdown(f'<span style="background:{color};color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;">🎯 {st.session_state.skill_level}</span>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<span style="background:#666;color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;">🎯 Detecting...</span>', 
                           unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def reset_session(selected_title):
    st.session_state.current_problem = selected_title
    st.session_state.orchestrator.reset()
    st.session_state.mentor_conversation = []
    st.session_state.code_conversation = []
    st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
    st.session_state.approach_approved = False
    st.session_state.skill_level = None
    st.session_state.hints_used = 0

def render_problem_panel():
    selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
    
    # Problem card
    difficulty_class = f"difficulty-{selected_problem['difficulty'].lower()}"
    
    st.markdown(f"""
    <div class="problem-card">
        <div class="problem-title">{selected_problem['title']}</div>
        <div class="difficulty-badge {difficulty_class}">{selected_problem['difficulty']}</div>
        <div class="problem-description">{selected_problem['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Examples
    if "examples" in selected_problem and selected_problem["examples"]:
        st.markdown("### 📋 Examples")
        for i, example in enumerate(selected_problem["examples"], 1):
            st.markdown(f"""
            <div class="example-container">
                <div class="example-title">Example {i}:</div>
                <div class="example-code">Input: {example['input']}</div>
                <div class="example-code">Output: {example['output']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Constraints (if available)
    if "constraints" in selected_problem:
        st.markdown("### 📏 Constraints")
        for constraint in selected_problem["constraints"]:
            st.markdown(f"• {constraint}")

def render_mentor_panel():
    st.markdown("### 🧠 Approach Discussion")
    
    # Chat history
    if st.session_state.mentor_conversation:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.mentor_conversation:
            msg_class = "user-message" if msg["role"] == "user" else "mentor-message"
            role_emoji = "🧑" if msg["role"] == "user" else "🤖"
            role_name = "You" if msg["role"] == "user" else "AI Mentor"
            st.markdown(f"""
            <div class="chat-message {msg_class}">
                <strong>{role_emoji} {role_name}:</strong><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Auto-suggest hint if user is stuck
    if st.session_state.orchestrator.should_suggest_hint():
        st.info("💡 You've been thinking for a while. Would you like a hint to get unstuck?")
    
    # Input area
    st.markdown("### 💭 Describe Your Approach")
    user_input = st.text_area(
        "How would you solve this problem? Walk through your thought process:",
        height=120,
        placeholder="Think about the problem step by step...",
        key="mentor_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 Submit Approach", type="primary", use_container_width=True):
            if user_input.strip():
                process_mentor_input(user_input)
    
    with col2:
        if st.button("💡 Get Hint", use_container_width=True):
            get_hint()
    
    # Show progress to coding phase
    if st.session_state.approach_approved:
        st.success("✅ Excellent approach! You're ready to implement your solution.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Coding", type="primary", use_container_width=True):
                safe_transition(st.session_state.orchestrator.transition_to_coding)
        with col2:
            if st.button("📊 Skip to Evaluation", use_container_width=True):
                st.session_state.orchestrator.transition_to_evaluation()
                st.rerun()



def render_code_panel():
    st.markdown("### 💻 Code Implementation")
    
    # Code editor with header
    st.markdown(f"""
    <div class="code-editor-container">
        <div class="code-header">
            <span style="color: #ffffff; font-weight: 600;">Solution.{st.session_state.selected_language.lower()}</span>
            <span style="color: #888; font-size: 12px;">💡 Hints used: {st.session_state.hints_used}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Code editor
    user_code = st.text_area(
        "",
        value=st.session_state.user_code,
        height=400,
        key="code_editor",
        label_visibility="collapsed"
    )
    st.session_state.user_code = user_code
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🧪 Run & Test", type="primary", use_container_width=True):
            test_code()
    
    with col2:
        if st.button("🔄 Back to Discussion", use_container_width=True):
            st.session_state.approach_approved = False
            safe_transition(st.session_state.orchestrator.transition_to_mentoring)
    
    with col3:
        if st.button("📊 Get Evaluation", use_container_width=True):
            safe_transition(st.session_state.orchestrator.transition_to_evaluation)
    
    with col4:
        if st.button("🔄 Reset Code", use_container_width=True):
            st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
            st.rerun()
    
    # Code assistant
    st.markdown("### 🤖 Code Assistant")
    code_question = st.text_input(
        "Ask about your code, optimizations, or debugging:",
        placeholder="e.g., How can I optimize this solution?",
        key="code_question"
    )
    
    if st.button("💬 Ask Assistant") and code_question:
        process_code_question(code_question)
    
    # Code discussion history
    if st.session_state.code_conversation:
        st.markdown("### 💬 Discussion History")
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.code_conversation[-6:]:  # Show last 6 messages
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🧑 You:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)
            elif msg["role"] == "code_agent":
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 Code Assistant:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message">
                    <strong>🔍 System:</strong><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_evaluation_panel():
    st.markdown("## 📊 Solution Analysis")
    
    with st.spinner("🤖 Analyzing your solution..."):
        # Define the missing variables
        mentor_msgs = len([m for m in st.session_state.mentor_conversation if m["role"] == "user"])
        code_msgs = len([m for m in st.session_state.code_conversation if m["role"] == "user"])
        selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
        evaluation = st.session_state.evaluation_agent.generate_evaluation(
            skill_level=st.session_state.skill_level,
            hints_used=st.session_state.hints_used,
            final_code=st.session_state.user_code,
            problem=selected_problem,
            conversation_history=st.session_state.mentor_conversation + st.session_state.code_conversation
        )
        
        # Mark session as complete
        #st.session_state.orchestrator.complete_session()

        # Get detailed analytics
        analytics = st.session_state.orchestrator.get_session_analytics()
        
        
        # Performance summary - compact for RHS
        st.markdown(evaluation["summary"])
        
        # Technical scores in compact format
        raw_data = evaluation.get("raw_data", {})
        tech_score = raw_data.get("technical_score", 0)
        approach_score = raw_data.get("approach_score", 0)
        
        # Progress bars for scores
        st.progress(tech_score / 10, text=f"🔧 Technical: {tech_score}/10")
        st.progress(approach_score / 10, text=f"🧠 Approach: {approach_score}/10")
        
        # Complexity analysis - key technical focus
        st.markdown("---")
        st.markdown(evaluation["complexity_analysis"])
        
        # Enhanced session summary with orchestrator analytics
        st.markdown("### 📈 Session Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Time", f"{analytics['total_duration']:.1f}s")
            st.metric("Interactions", analytics['user_interactions'])

        with col2:
            st.metric("Hints Used", analytics['hints_requested'])
            st.metric("Code Runs", analytics['code_submissions'])

        with col3:
            st.metric("State Changes", analytics['total_transitions'])
            st.metric("Frequency", f"{analytics['interaction_frequency']:.1f}/min")
        
        # Actionable feedback - condensed
        st.markdown("---")
        st.markdown(evaluation["actionable_feedback"])
        
        # Action buttons - vertical layout for RHS
        st.markdown("---")
        st.markdown("### 🎯 Next Actions")
        
        if st.button("🔄 Try New Problem", type="primary", use_container_width=True):
            # Reset for new problem
            st.session_state.orchestrator.complete_session()
            st.session_state.orchestrator.reset()
            st.session_state.mentor_conversation = []
            st.session_state.code_conversation = []
            st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
            st.session_state.approach_approved = False
            st.session_state.skill_level = None
            st.session_state.hints_used = 0
            st.rerun()
        
        # Use this pattern (like in code panel):
        if st.button("🧠 Discuss Approach", use_container_width=True):
            st.session_state.approach_approved = False
            safe_transition(st.session_state.orchestrator.transition_to_mentoring)

        if st.button("💻 Back to Coding", use_container_width=True):
            #safe_transition(st.session_state.orchestrator.transition_to_coding)  
            st.session_state.orchestrator.transition_to_coding()
            st.rerun()
        
        # Expandable detailed session info
        with st.expander("📊 Detailed Technical Analysis"):
            if raw_data:
                st.markdown("**Complexity Details**")
                st.write(f"⏱️ **Time:** {raw_data.get('time_complexity', 'Not analyzed')}")
                st.write(f"💾 **Space:** {raw_data.get('space_complexity', 'Not analyzed')}")
                st.write(f"⚡ **Optimal:** {'✅ Yes' if raw_data.get('is_optimal') else '⚠️ Can improve'}")
                st.write(f"✅ **Correctness:** {raw_data.get('correctness', 'Unknown')}")
                
                st.markdown("**Session Timeline**")
                st.write(f"🎯 **Problem:** {st.session_state.current_problem}")
                st.write(f"📝 **Approach Approved:** {'✅ Yes' if st.session_state.approach_approved else '❌ No'}")
                st.write(f"💬 **Mentor Chats:** {mentor_msgs}")
                st.write(f"🔧 **Code Reviews:** {code_msgs}")
            else:
                st.info("Detailed analysis not available")

# Optional: Add a quick comparison function for skill level assessment
def render_skill_progression():
    """Show skill progression if multiple problems solved"""
    if 'problem_history' not in st.session_state:
        st.session_state.problem_history = []
    
    if len(st.session_state.problem_history) > 1:
        st.markdown("### 📈 Skill Progression")
        
        # Simple progression chart
        problems = [p['problem'] for p in st.session_state.problem_history]
        scores = [p['technical_score'] for p in st.session_state.problem_history]
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=problems,
            y=scores,
            mode='lines+markers',
            name='Technical Score',
            line=dict(color='#00D4AA', width=3)
        ))
        
        fig.update_layout(
            title="Your DSA Journey",
            xaxis_title="Problems Solved",
            yaxis_title="Technical Score (1-10)",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)



# Helper functions
def process_mentor_input(user_input):
    with st.spinner("🤖 AI Mentor is analyzing your approach..."):
        # Log the user interaction
        st.session_state.orchestrator.log_user_interaction("approach_submitted", {
            "approach_length": len(user_input),
            "skill_level": st.session_state.skill_level
        })
        
        selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
        st.session_state.mentor_conversation.append({
            "role": "user",
            "content": user_input
        })
        
        response = st.session_state.mentor_agent.analyze_approach(
            user_input, 
            selected_problem,
            st.session_state.skill_level
        )
        
        # Update skill level if detected
        if response.get("skill_level"):
            st.session_state.skill_level = response["skill_level"]
            st.success(f"🎯 Skill level detected: {response['skill_level']}")
        
        st.session_state.mentor_conversation.append({
            "role": "mentor",
            "content": response["message"]
        })
        
        if response.get("approved", False):
            st.session_state.approach_approved = True
            st.session_state.orchestrator.transition_to_coding()
        
        if response.get("hint"):
            st.session_state.hints_used += 1
        
        st.rerun()



def get_hint():
    with st.spinner("🤖 Generating helpful hint..."):
        selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
        hint = st.session_state.mentor_agent.give_hint(
            st.session_state.skill_level or "Intermediate",
            selected_problem
        )
        
        st.session_state.mentor_conversation.append({
            "role": "mentor",
            "content": f"💡 **Hint:** {hint}"
        })
        st.session_state.hints_used += 1
        
        # Log hint request
        st.session_state.orchestrator.log_user_interaction("hint_requested", {
        "hint_number": st.session_state.hints_used + 1,
        "current_state": st.session_state.orchestrator.get_current_state()
        })
        
        st.rerun()

def test_code():
    if st.session_state.user_code.strip():
        with st.spinner("🤖 Testing your code..."):
            selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
            
            result = st.session_state.code_agent.evaluate_code(
                st.session_state.user_code,
                selected_problem,
                st.session_state.skill_level
            )
            
            # Log code submission
            st.session_state.orchestrator.log_user_interaction("code_submitted", {
            "code_length": len(st.session_state.user_code),
            "test_passed": result.get("passed", False)
        })
            
            st.session_state.code_conversation.append({
                "role": "system",
                "content": f"**Code Test Results:**\n{result['feedback']}"
            })
            
            if result.get("passed", False):
                st.success("✅ All tests passed! Great job!")
            else:
                st.error("❌ Some tests failed. Check the feedback for details.")
            
            st.rerun()

def process_code_question(question):
    with st.spinner("🤖 Code assistant is thinking..."):
        selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
        response = st.session_state.code_agent.chat_assistance(
            question,
            st.session_state.user_code,
            selected_problem,
            st.session_state.skill_level
        )
        
        st.session_state.code_conversation.append({
            "role": "user",
            "content": question
        })
        st.session_state.code_conversation.append({
            "role": "code_agent",
            "content": response
        })
        st.rerun()

def render_guidance_panel():
    """Show contextual guidance based on orchestrator state"""
    if st.session_state.orchestrator.get_current_state() == "mentoring":
        recommendation = st.session_state.orchestrator.get_next_recommended_action()
        st.info(f"💡 **Guidance:** {recommendation}")
        
        # Show time spent in current state
        analytics = st.session_state.orchestrator.get_session_analytics()
        time_in_state = analytics['time_per_state'].get('mentoring', 0)
        if time_in_state > 180:  # 3 minutes
            st.warning("⏰ You've been in discussion phase for a while. Consider asking for a hint or moving to coding!")

def safe_transition(target_state_func):
    """Safely transition between states with validation"""
    current_state = st.session_state.orchestrator.get_current_state()
    if target_state_func():
        st.success(f"✅ Moved to {st.session_state.orchestrator.get_current_state().title()} phase")
        st.rerun()
    else:
        st.error(f"❌ Cannot transition from {current_state} to requested state")

# Main App
def main():
    # Render top navigation
    render_top_nav()
    
    # Set current problem if not set
    if not st.session_state.current_problem:
        st.session_state.current_problem = problems[0]["title"]
        st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
        # Show guidance panel
        render_guidance_panel()
    
    # Create main layout with tabs
    tab1, tab2 = st.columns([1, 1])
    
    with tab1:
        st.markdown("## 📖 Problem")
        render_problem_panel()
    
    with tab2:
        current_state = st.session_state.orchestrator.get_current_state()
        
        if current_state == "mentoring":
            render_mentor_panel()
        elif current_state == "coding":
            render_code_panel()
        elif current_state == "evaluation":
            render_evaluation_panel()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; padding: 20px;">'
        '🤖 <strong>Espyr AI Coach</strong> - Your intelligent DSA preparation companion | '
        f'Current Phase: {current_state.title()} | '
        f'Language: {st.session_state.selected_language}'
        '</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()




