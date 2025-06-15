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
    page_title="Espyr AI Coach", 
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
            st.markdown("### 🧠 Espyr AI Coach")
        
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
            current_state = st.session_state.orchestrator.get_current_state()
            status_class = f"status-{current_state.lower()}"
            st.markdown(f'<span class="status-indicator {status_class}">📍 {current_state.title()}</span>', 
                       unsafe_allow_html=True)
        
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
                st.session_state.orchestrator.transition_to_coding()
                st.rerun()
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
            st.session_state.orchestrator.transition_to_mentoring()
            st.session_state.approach_approved = False
            st.rerun()
    
    with col3:
        if st.button("📊 Get Evaluation", use_container_width=True):
            st.session_state.orchestrator.transition_to_evaluation()
            st.rerun()
    
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
    st.markdown("### 📊 Performance Evaluation")
    
    with st.spinner("🤖 Generating comprehensive evaluation..."):
        selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
        evaluation = st.session_state.evaluation_agent.generate_evaluation(
            skill_level=st.session_state.skill_level,
            hints_used=st.session_state.hints_used,
            final_code=st.session_state.user_code,
            problem=selected_problem,
            conversation_history=st.session_state.mentor_conversation + st.session_state.code_conversation
        )
        
        # Performance summary
        st.markdown("#### 🎯 Performance Summary")
        st.info(evaluation["summary"])
        
        # Detailed analysis
        st.markdown("#### 🔍 Detailed Analysis")
        st.markdown(evaluation["detailed_analysis"])
        
        # Recommendations
        st.markdown("#### 🚀 Next Steps & Recommendations")
        st.markdown(evaluation["recommendations"])
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Try Another Problem", type="primary", use_container_width=True):
                # Reset for new problem
                st.session_state.orchestrator.reset()
                st.session_state.mentor_conversation = []
                st.session_state.code_conversation = []
                st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
                st.session_state.approach_approved = False
                st.session_state.skill_level = None
                st.session_state.hints_used = 0
                st.rerun()
        
        with col2:
            if st.button("💻 Back to Coding", use_container_width=True):
                st.session_state.orchestrator.transition_to_coding()
                st.rerun()
        
        with col3:
            if st.button("🧠 Back to Discussion", use_container_width=True):
                st.session_state.orchestrator.transition_to_mentoring()
                st.rerun()
        
        # Additional info section
        st.markdown("---")
        if st.button("📈 View Session Summary", use_container_width=True):
            st.markdown("### 📈 Session Progress")
            st.markdown(f"**Problem:** {st.session_state.current_problem}")
            st.markdown(f"**Language:** {st.session_state.selected_language}")
            st.markdown(f"**Skill Level:** {st.session_state.skill_level or 'Not determined'}")
            st.markdown(f"**Hints Used:** {st.session_state.hints_used}")
            st.markdown(f"**Approach Approved:** {'✅ Yes' if st.session_state.approach_approved else '❌ No'}")
            
            # Show conversation stats
            mentor_msgs = len([m for m in st.session_state.mentor_conversation if m["role"] == "user"])
            code_msgs = len([m for m in st.session_state.code_conversation if m["role"] == "user"])
            st.markdown(f"**Mentor Interactions:** {mentor_msgs}")
            st.markdown(f"**Code Discussions:** {code_msgs}")

# Helper functions
def process_mentor_input(user_input):
    with st.spinner("🤖 AI Mentor is analyzing your approach..."):
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

# Main App
def main():
    # Render top navigation
    render_top_nav()
    
    # Set current problem if not set
    if not st.session_state.current_problem:
        st.session_state.current_problem = problems[0]["title"]
        st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
    
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


# import streamlit as st
# import json
# import time
# import logging
# from datetime import datetime
# from agents.mentor_agent import MentorAgent
# from agents.code_agent import CodeAgent
# from agents.evaluation_agent import EvaluationAgent
# from agents.persona_agent import PersonaAgent
# from agents.orchestrator import AgentOrchestrator
# from utils.gemini_client import get_gemini_model

# # Configure logging
# logging.basicConfig(filename="app.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# # Page configuration
# st.set_page_config(
#     page_title="DSA Coach",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # CSS for LeetCode-like styling
# st.markdown("""
# <style>
#     .main-container {
#         background: #ffffff;
#         font-family: 'Inter', sans-serif;
#     }
#     .top-nav {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 15px 20px;
#         border-radius: 10px;
#         margin-bottom: 20px;
#         color: white;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.1);
#         position: sticky;
#         top: 0;
#         z-index: 1000;
#     }
#     .problem-card {
#         background: #f8fafc;
#         border: 1px solid #e2e8f0;
#         border-radius: 12px;
#         padding: 24px;
#         margin-bottom: 20px;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.05);
#         max-height: 70vh;
#         overflow-y: auto;
#     }
#     .problem-title {
#         font-size: 24px;
#         font-weight: 700;
#         color: #1a202c;
#         margin-bottom: 16px;
#     }
#     .difficulty-badge {
#         padding: 4px 12px;
#         border-radius: 16px;
#         font-size: 12px;
#         font-weight: 600;
#         text-transform: uppercase;
#         margin-bottom: 16px;
#     }
#     .difficulty-easy { background: #d4edda; color: #155724; }
#     .difficulty-medium { background: #fff3cd; color: #856404; }
#     .difficulty-hard { background: #f8d7da; color: #721c24; }
#     .chat-container {
#         height: 350px;
#         overflow-y: auto;
#         border: 1px solid #e2e8f0;
#         border-radius: 8px;
#         padding: 16px;
#         background: #fafafa;
#         scroll-behavior: smooth;
#     }
#     .chat-message {
#         margin-bottom: 12px;
#         padding: 12px;
#         border-radius: 8px;
#         max-width: 100%;
#         word-wrap: break-word;
#         animation: fadeIn 0.3s ease-in;
#     }
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(10px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
#     .user-message { background: #e3f2fd; border-left: 3px solid #2196f3; color: #1a202c; }
#     .mentor-message { background: #f3e5f5; border-left: 3px solid #9c27b0; color: #1a202c; }
#     .agent-message { background: #e8f5e8; border-left: 3px solid #4caf50; color: #1a202c; }
#     .system-message { background: #fff3e0; border-left: 3px solid #ff9800; color: #1a202c; font-style: italic; }
#     .code-editor-container {
#         background: #1e1e1e;
#         border-radius: 8px;
#         margin-bottom: 20px;
#         border: 1px solid #333;
#         max-height: 500px;
#         overflow-y: auto;
#     }
#     .code-header {
#         background: #2d2d2d;
#         padding: 12px 16px;
#         border-radius: 8px 8px 0 0;
#         border-bottom: 1px solid #333;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         position: sticky;
#         top: 0;
#         z-index: 10;
#     }
#     .status-indicator {
#         padding: 6px 12px;
#         border-radius: 20px;
#         font-size: 12px;
#         font-weight: 600;
#         margin-right: 8px;
#     }
#     .status-mentoring { background: #fef7e0; color: #92400e; }
#     .status-coding { background: #e0f2fe; color: #0d47a1; }
#     .status-evaluation { background: #e8f5e8; color: #2e7d32; }
#     .status-completed { background: #f3e5f5; color: #7b1fa2; }
#     .progress-container {
#         background: #e0e0e0;
#         border-radius: 10px;
#         height: 8px;
#         margin: 10px 0;
#         overflow: hidden;
#     }
#     .progress-bar {
#         height: 100%;
#         background: linear-gradient(90deg, #667eea, #764ba2);
#         border-radius: 10px;
#         transition: width 0.3s ease;
#     }
#     .persona-indicator {
#         background: rgba(255,255,255,0.2);
#         border-radius: 8px;
#         padding: 8px 12px;
#         font-size: 12px;
#         backdrop-filter: blur(10px);
#     }
#     .chat-container::-webkit-scrollbar {
#         width: 6px;
#     }
#     .chat-container::-webkit-scrollbar-track {
#         background: #f1f1f1;
#         border-radius: 3px;
#     }
#     .chat-container::-webkit-scrollbar-thumb {
#         background: #888;
#         border-radius: 3px;
#     }
#     .chat-container::-webkit-scrollbar-thumb:hover {
#         background: #555;
#     }
#     @media (max-width: 768px) {
#         .top-nav { padding: 10px 15px; }
#         .problem-card { padding: 16px; }
#         .chat-container { height: 250px; }
#     }
# </style>
# """, unsafe_allow_html=True)

# # Language templates
# LANGUAGE_TEMPLATES = {
#     "Python": """def solution():
#     # Write your solution here
#     pass

# if __name__ == "__main__":
#     pass""",
#     "Java": """public class Solution {
#     public void solution() {
#     }
    
#     public static void main(String[] args) {
#     }
# }""",
#     "C++": """#include <iostream>
# #include <vector>
# #include <string>
# using namespace std;

# class Solution {
# public:
#     void solution() {
#     }
# };

# int main() {
#     return 0;
# }""",
#     "JavaScript": """function solution() {
# }

# console.log(solution());""",
#     "Go": """package main

# import "fmt"

# func solution() {
# }

# func main() {
# }"""
# }

# # Load problems
# @st.cache_data
# def load_problems():
#     try:
#         with open("data/problems.json", "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return [
#             {
#                 "title": "Two Sum",
#                 "difficulty": "Easy",
#                 "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
#                 "examples": [
#                     {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
#                     {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
#                 ]
#             },
#             {
#                 "title": "Reverse Linked List",
#                 "difficulty": "Easy",
#                 "description": "Given the head of a singly linked list, reverse the list and return the reversed list.",
#                 "examples": [
#                     {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"},
#                     {"input": "head = [1,2]", "output": "[2,1]"}
#                 ]
#             },
#             {
#                 "title": "Valid Parentheses",
#                 "difficulty": "Easy",
#                 "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
#                 "examples": [
#                     {"input": "s = \"()\"", "output": "true"},
#                     {"input": "s = \"()[]{}\"", "output": "true"},
#                     {"input": "s = \"(]\"", "output": "false"}
#                 ]
#             }
#         ]

# problems = load_problems()

# # Session state initialization
# def initialize_session_state():
#     defaults = {
#         "orchestrator": AgentOrchestrator(),
#         "mentor_agent": MentorAgent(),
#         "code_agent": CodeAgent(),
#         "evaluation_agent": EvaluationAgent(),
#         "persona_agent": PersonaAgent(),
#         "current_problem": problems[0]["title"],
#         "selected_language": "Python",
#         "skill_level": None,
#         "mentor_conversation": [],
#         "code_conversation": [],
#         "user_code": LANGUAGE_TEMPLATES["Python"],
#         "hints_used": 0,
#         "session_start_time": time.time(),
#         "approach_approved": False,
#         "last_activity": time.time(),
#         "max_chat_messages": 20
#     }
    
#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value

# initialize_session_state()

# # Top navigation
# def render_top_nav():
#     problem_titles = [p["title"] for p in problems]
    
#     with st.container():
#         st.markdown('<div class="top-nav">', unsafe_allow_html=True)
        
#         col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
#         with col1:
#             st.markdown("### 🧠 DSA Coach")
#             active_agent = st.session_state.orchestrator.get_active_agent()
#             st.markdown(f'<div class="persona-indicator">🤖 Active: {active_agent}</div>', unsafe_allow_html=True)
        
#         with col2:
#             selected_title = st.selectbox(
#                 "Problem:",
#                 problem_titles,
#                 index=problem_titles.index(st.session_state.current_problem),
#                 key="problem_selector",
#                 label_visibility="collapsed"
#             )
            
#             if st.session_state.current_problem != selected_title:
#                 reset_session(selected_title)
        
#         with col3:
#             selected_lang = st.selectbox(
#                 "Language:",
#                 list(LANGUAGE_TEMPLATES.keys()),
#                 index=list(LANGUAGE_TEMPLATES.keys()).index(st.session_state.selected_language),
#                 key="lang_selector",
#                 label_visibility="collapsed"
#             )
            
#             if st.session_state.selected_language != selected_lang:
#                 st.session_state.selected_language = selected_lang
#                 if not st.session_state.user_code.strip():
#                     st.session_state.user_code = LANGUAGE_TEMPLATES[selected_lang]
        
#         with col4:
#             current_state = st.session_state.orchestrator.get_current_state()
#             progress = st.session_state.orchestrator.get_progress_summary()
#             status_class = f"status-{current_state.lower()}"
            
#             st.markdown(f'<span class="status-indicator {status_class}">📍 {current_state.title()}</span>',
#                        unsafe_allow_html=True)
            
#             progress_pct = progress.get("progress_percentage", 0)
#             st.markdown(f"""
#             <div class="progress-container">
#                 <div class="progress-bar" style="width: {progress_pct}%"></div>
#             </div>
#             <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Progress: {progress_pct}%</div>
#             """, unsafe_allow_html=True)
        
#         with col5:
#             if st.session_state.skill_level:
#                 skill_colors = {"Beginner": "#ff9800", "Intermediate": "#2196f3", "Advanced": "#4caf50"}
#                 color = skill_colors.get(st.session_state.skill_level, "#666")
#                 st.markdown(f"""
#                 <div style="background:{color};color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;margin-bottom:4px;">
#                     🎯 {st.session_state.skill_level}
#                 </div>
#                 <div style="font-size:9px;color:rgba(255,255,255,0.8);text-align:center;">
#                     Hints: {st.session_state.hints_used}
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown('<span style="background:#666;color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;">🎯 Detecting...</span>',
#                            unsafe_allow_html=True)
        
#         st.markdown('</div>', unsafe_allow_html=True)

# def reset_session(selected_title):
#     st.session_state.current_problem = selected_title
#     st.session_state.orchestrator.reset()
#     st.session_state.mentor_conversation = []
#     st.session_state.code_conversation = []
#     st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
#     st.session_state.approach_approved = False
#     st.session_state.skill_level = None
#     st.session_state.hints_used = 0
#     st.session_state.session_start_time = time.time()
#     st.session_state.last_activity = time.time()
    
#     st.session_state.orchestrator.log_user_interaction("session_reset", {
#         "problem": selected_title,
#         "language": st.session_state.selected_language
#     })

# def manage_chat_history(conversation_list, max_messages=20):
#     if len(conversation_list) > max_messages:
#         return [conversation_list[0]] + conversation_list[-(max_messages-1):]
#     return conversation_list

# def render_problem_panel():
#     selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
    
#     difficulty_class = f"difficulty-{selected_problem['difficulty'].lower()}"
    
#     st.markdown(f"""
#     <div class="problem-card">
#         <div class="problem-title">{selected_problem['title']}</div>
#         <div class="difficulty-badge {difficulty_class}">{selected_problem['difficulty']}</div>
#         <div class="problem-description">{selected_problem['description']}</div>
#     """, unsafe_allow_html=True)
    
#     if "examples" in selected_problem and selected_problem["examples"]:
#         st.markdown("### 📋 Examples")
#         for i, example in enumerate(selected_problem["examples"], 1):
#             st.markdown(f"""
#             <div style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin: 8px 0;">
#                 <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">Example {i}:</div>
#                 <div style="background: #2d3748; color: #e2e8f0; padding: 6px 10px; border-radius: 4px; font-family: monospace; margin: 4px 0;">
#                     Input: {example['input']}
#                 </div>
#                 <div style="background: #2d3748; color: #2e8f0; padding: 6px 10px; border-radius: 4px; font-family: monospace; margin: 4px 0;">
#                     Output: {example['output']}
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown('</div>', unsafe_allow_html=True)

# def render_mentor_panel():
#     st.markdown("### 🧠 Approach Discussion")
    
#     if st.session_state.skill_level:
#         persona_profile = st.session_state.persona_agent.get_user_profile(
#             st.session_state.skill_level,
#             st.session_state.orchestrator.get_session_analytics()
#         )
#         if persona_profile.get("persona_message"):
#             st.info(f"💡 {persona_profile['persona_message']}")
    
#     if st.session_state.mentor_conversation:
#         st.markdown('<div class="chat-container" id="mentor-chat">', unsafe_allow_html=True)
        
#         managed_conversation = manage_chat_history(st.session_state.mentor_conversation)
        
#         for msg in managed_conversation:
#             timestamp = datetime.now().strftime("%H:%M")
#             msg_class = "user-message" if msg["role"] == "user" else "mentor-message"
#             role_emoji = "🧑" if msg["role"] == "user" else "🤖"
#             role_name = "You" if msg["role"] == "user" else "AI Mentor"
            
#             st.markdown(f"""
#             <div class="chat-message {msg_class}">
#                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
#                     <strong>{role_emoji} {role_name}</strong>
#                     <span style="font-size: 10px; color: #666;">{timestamp}</span>
#                 </div>
#                 <div>{msg['content']}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         st.markdown('</div>', unsafe_allow_html=True)
        
#         st.markdown("""
#         <script>
#         const chatContainer = document.getElementById('mentor-chat');
#         if (chatContainer) {
#             chatContainer.scrollTop = chatContainer.scrollHeight;
#         }
#         </script>
#         """, unsafe_allow_html=True)
    
#     st.markdown("### 💭 Describe Your Approach")
#     user_input = st.text_area(
#         "How would you solve this problem?",
#         height=120,
#         placeholder="Think step by step...",
#         key="mentor_input"
#     )
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if st.button("💬 Submit Approach", type="primary", use_container_width=True):
#             if user_input.strip():
#                 process_mentor_input(user_input)
    
#     with col2:
#         if st.button("💡 Get Hint", use_container_width=True):
#             get_hint()
    
#     with col3:
#         if st.button("📊 Skip to Coding", use_container_width=True):
#             if st.session_state.orchestrator.can_transition_to("coding"):
#                 st.session_state.orchestrator.transition_to_coding()
#                 st.rerun()
#             else:
#                 st.error("❌ Discuss your approach first!")
    
#     if st.session_state.approach_approved:
#         st.success("✅ Excellent approach! Ready to code.")
#         next_action = st.session_state.orchestrator.get_next_recommended_action()
#         st.info(f"🎯 **Next:** {next_action}")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("🚀 Start Coding", type="primary", use_container_width=True):
#                 st.session_state.orchestrator.transition_to_coding()
#                 st.rerun()
#         with col2:
#             if st.button("📊 Skip to Evaluation", use_container_width=True):
#                 st.session_state.orchestrator.transition_to_evaluation()
#                 st.rerun()

# def render_code_panel():
#     st.markdown("### 💻 Code Implementation")
    
#     st.markdown(f"""
#     <div class="code-editor-container">
#         <div class="code-header">
#             <span style="color: #ffffff; font-weight: 600;">Solution.{st.session_state.selected_language.lower()}</span>
#             <div>
#                 <span style="color: #888; font-size: 12px;">💡 Hints: {st.session_state.hints_used}</span>
#                 <span style="color: #888; font-size: 12px; margin-left: 10px;">⏱️ {int((time.time() - st.session_state.session_start_time) / 60)}min</span>
#             </div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
    
#     user_code = st.text_area(
#         "",
#         value=st.session_state.user_code,
#         height=400,
#         key="code_editor",
#         label_visibility="collapsed"
#     )
#     st.session_state.user_code = user_code
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         if st.button("🧪 Run & Test", type="primary", use_container_width=True):
#             test_code()
    
#     with col2:
#         if st.button("🔄 Back to Discussion", use_container_width=True):
#             if st.session_state.orchestrator.transition_to_mentoring():
#                 st.session_state.approach_approved = False
#                 st.rerun()
    
#     with col3:
#         if st.button("📊 Get Evaluation", use_container_width=True):
#             if st.session_state.orchestrator.transition_to_evaluation():
#                 st.rerun()
    
#     with col4:
#         if st.button("🔄 Reset Code", use_container_width=True):
#             st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
#             st.rerun()
    
#     st.markdown("### 🤖 Code Assistant")
#     code_question = st.text_input(
#         "Ask about your code, optimizations, or debugging:",
#         placeholder="e.g., How can I optimize this solution?",
#         key="code_question"
#     )
    
#     if st.button("💬 Ask Assistant") and code_question:
#         process_code_question(code_question)
    
#     if st.session_state.code_conversation:
#         st.markdown("### 💬 Discussion History")
#         st.markdown('<div class="chat-container" id="code-chat">', unsafe_allow_html=True)
        
#         managed_conversation = manage_chat_history(st.session_state.code_conversation)
        
#         for msg in managed_conversation:
#             timestamp = datetime.now().strftime("%H:%M")
#             if msg["role"] == "user":
#                 st.markdown(f"""
#                 <div class="chat-message user-message">
#                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
#                         <strong>🧑 You</strong>
#                         <span style="font-size: 10px; color: #666;">{timestamp}</span>
#                     </div>
#                     <div>{msg['content']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#             elif msg["role"] == "code_agent":
#                 st.markdown(f"""
#                 <div class="chat-message agent-message">
#                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
#                         <strong>🤖 Code Assistant</strong>
#                         <span style="font-size: 10px; color: #666;">{timestamp}</span>
#                     </div>
#                     <div>{msg['content']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown(f"""
#                 <div class="chat-message system-message">
#                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
#                         <strong>🔍 System</strong>
#                         <span style="font-size: 10px; color: #666;">{timestamp}</span>
#                     </div>
#                     <div>{msg['content']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
        
#         st.markdown('</div>', unsafe_allow_html=True)

# def render_evaluation_panel():
#     st.markdown("### 📊 Performance Evaluation")
    
#     with st.spinner("🤖 Generating evaluation..."):
#         selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
#         session_analytics = st.session_state.orchestrator.get_session_analytics()
        
#         persona_summary = st.session_state.persona_agent.get_session_summary(
#             session_analytics,
#             st.session_state.skill_level or "Intermediate"
#         )
        
#         evaluation = st.session_state.evaluation_agent.generate_evaluation(
#             skill_level=st.session_state.skill_level or "Intermediate",
#             hints_used=st.session_state.hints_used,
#             final_code=st.session_state.user_code,
#             problem=selected_problem,
#             conversation_history=st.session_state.mentor_conversation + st.session_state.code_conversation
#         )
        
#         st.markdown("#### 🎯 Performance Summary")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Time Spent", f"{int(session_analytics.get('total_duration', 0) / 60)}min")
#         with col2:
#             st.metric("Hints Used", st.session_state.hints_used)
#         with col3:
#             st.metric("Interactions", session_analytics.get('user_interactions', 0))
        
#         st.info(evaluation["summary"])
        
#         st.markdown("#### 🧠 Personalized Insights")
#         for insight in persona_summary.get("insights", []):
#             st.success(f"✅ {insight}")
        
#         st.markdown("#### 🔍 Detailed Analysis")
#         st.markdown(evaluation["detailed_analysis"])
        
#         st.markdown("#### 🚀 Next Steps")
#         st.markdown(evaluation["recommendations"])
        
#         st.markdown("#### 📈 Session Analytics")
#         st.write(f"**Total Duration**: {int(session_analytics.get('total_duration', 0) / 60)} minutes")
#         st.write(f"**States Visited**: {session_analytics.get('states_visited', '')}")
#         st.write(f"**Total Transitions**: {session_analytics.get('total_transitions', 0)}")
#         st.write(f"**Interaction Frequency**: {session_analytics.get('interaction_frequency', 0):.2f} interactions/min")
        
#         st.markdown("##### ⏱️ Time Distribution")
#         for state, duration in session_analytics.get('time_per_state', {}).items():
#             st.write(f"{state.title()}: {int(duration / 60)} min {int(duration % 60)} sec")
        
#         st.markdown("#### 🎯 Next Difficulty")
#         difficulty_rec = st.session_state.persona_agent.get_difficulty_adjustment(
#             st.session_state.skill_level or "Intermediate",
#             [session_analytics]
#         )
#         st.info(f"Recommended: **{difficulty_rec}** the difficulty level.")
        
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button("🔄 Try Another Problem", type="primary", use_container_width=True):
#                 st.session_state.orchestrator.complete_session()
#                 reset_session(problems[0]["title"])
#                 st.rerun()
#         with col2:
#             if st.button("💻 Back to Coding", use_container_width=True):
#                 if st.session_state.orchestrator.transition_to_coding():
#                     st.rerun()
#         with col3:
#             if st.button("🧠 Back to Discussion", use_container_width=True):
#                 if st.session_state.orchestrator.transition_to_mentoring():
#                     st.rerun()

# def process_mentor_input(user_input):
#     try:
#         selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
#         st.session_state.orchestrator.log_user_interaction("approach_submitted", {
#             "input": user_input,
#             "problem": st.session_state.current_problem
#         })
        
#         st.session_state.persona_agent.update_performance_indicators(
#             st.session_state.orchestrator.get_session_analytics()
#         )
        
#         response = st.session_state.mentor_agent.analyze_approach(
#             user_input=user_input,
#             problem=selected_problem,
#             current_skill_level=st.session_state.skill_level or "Intermediate"
#         )
        
#         st.session_state.mentor_conversation.append({"role": "user", "content": user_input})
#         st.session_state.mentor_conversation.append({"role": "mentor", "content": response["message"]})
        
#         if response.get("skill_level") and not st.session_state.skill_level:
#             st.session_state.skill_level = response["skill_level"]
        
#         st.session_state.approach_approved = response.get("approved", False)
        
#         persona_profile = st.session_state.persona_agent.get_user_profile(
#             st.session_state.skill_level or "Intermediate",
#             st.session_state.orchestrator.get_session_analytics()
#         )
#         if persona_profile.get("motivation_message"):
#             st.session_state.mentor_conversation.append({
#                 "role": "mentor",
#                 "content": persona_profile["motivation_message"]
#             })
        
#         if st.session_state.orchestrator.get_hint_suggestions():
#             hint = st.session_state.mentor_agent.give_hint(
#                 skill_level=st.session_state.skill_level or "Intermediate",
#                 problem=selected_problem
#             )
#             st.session_state.mentor_conversation.append({"role": "mentor", "content": f"💡 Hint: {hint}"})
#             st.session_state.hints_used += 1
#             st.session_state.orchestrator.log_user_interaction("hint_provided", {"hint": hint})
        
#         st.session_state.mentor_conversation = manage_chat_history(st.session_state.mentor_conversation)
#         st.rerun()
#     except Exception as e:
#         logging.error(f"Mentor input processing failed: {e}")
#         st.error("Error processing approach. Please try again.")
#         st.session_state.mentor_conversation.append({
#             "role": "system",
#             "content": "⚠️ Sorry, something went wrong. Please try again."
#         })

# def get_hint():
#     try:
#         selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
#         st.session_state.persona_agent.update_performance_indicators(
#             st.session_state.orchestrator.get_session_analytics()
#         )
        
#         hint = st.session_state.mentor_agent.give_hint(
#             skill_level=st.session_state.skill_level or "Intermediate",
#             problem=selected_problem
#         )
        
#         st.session_state.mentor_conversation.append({
#             "role": "mentor",
#             "content": f"💡 Hint: {hint}"
#         })
        
#         st.session_state.hints_used += 1
#         st.session_state.orchestrator.log_user_interaction("hint_requested", {
#             "hint_count": st.session_state.hints_used,
#             "problem": st.session_state.current_problem
#         })
        
#         st.session_state.mentor_conversation = manage_chat_history(st.session_state.mentor_conversation)
#         st.rerun()
#     except Exception as e:
#         logging.error(f"Hint generation failed: {e}")
#         st.error("Error generating hint. Please try again.")

# def test_code():
#     try:
#         selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
#         st.session_state.orchestrator.log_user_interaction("code_submitted", {
#             "code": st.session_state.user_code,
#             "language": st.session_state.selected_language
#         })
        
#         st.session_state.persona_agent.update_performance_indicators(
#             st.session_state.orchestrator.get_session_analytics()
#         )
        
#         result = st.session_state.code_agent.evaluate_code(
#             user_code=st.session_state.user_code,
#             problem=selected_problem,
#             skill_level=st.session_state.skill_level or "Intermediate"
#         )
        
#         st.session_state.code_conversation.append({
#             "role": "user",
#             "content": "Submitted code for testing"
#         })
#         st.session_state.code_conversation.append({
#             "role": "code_agent",
#             "content": result["feedback"]
#         })
        
#         test_cases = st.session_state.code_agent.suggest_test_cases(
#             problem=selected_problem,
#             user_code=st.session_state.user_code
#         )
#         if test_cases:
#             st.session_state.code_conversation.append({
#                 "role": "system",
#                 "content": "**Test Cases:**\n" + "\n".join([f"Test {i+1}: Input: {tc['input']}, Expected: {tc['expected_output']}" for i, tc in enumerate(test_cases)])
#             })
        
#         if not result["passed"]:
#             encouragement = st.session_state.persona_agent.generate_encouragement_message(
#                 context="multiple_attempts",
#                 skill_level=st.session_state.skill_level or "Intermediate"
#             )
#             st.session_state.code_conversation.append({
#                 "role": "code_agent",
#                 "content": encouragement + "\nConsider discussing your approach again."
#             })
        
#         st.session_state.orchestrator.log_user_interaction("test_result", {
#             "passed": result["passed"],
#             "bugs": result.get("bugs", [])
#         })
        
#         st.session_state.code_conversation = manage_chat_history(st.session_state.code_conversation)
#         st.rerun()
#     except Exception as e:
#         logging.error(f"Code testing failed: {e}")
#         st.error("Failed to test code. Please check and try again.")
#         st.session_state.code_conversation.append({
#             "role": "system",
#             "content": "⚠️ Error testing code."
#         })

# def process_code_question(question):
#     try:
#         selected_problem = next(p for p in problems if p["title"] == st.session_state.current_problem)
        
#         st.session_state.orchestrator.log_user_interaction("code_question", {
#             "question": question,
#             "problem": st.session_state.current_problem
#         })
        
#         st.session_state.persona_agent.update_performance_indicators(
#             st.session_state.orchestrator.get_session_analytics()
#         )
        
#         persona_profile = st.session_state.persona_agent.get_user_profile(
#             st.session_state.skill_level or "Intermediate",
#             st.session_state.orchestrator.get_session_analytics()
#         )
        
#         response = st.session_state.code_agent.chat_assistance(
#             user_question=question,
#             user_code=st.session_state.user_code,
#             problem=selected_problem,
#             skill_level=st.session_state.skill_level or "Intermediate"
#         )
        
#         st.session_state.code_conversation.append({
#             "role": "user",
#             "content": question
#         })
#         st.session_state.code_conversation.append({
#             "role": "code_agent",
#             "content": response
#         })
        
#         encouragement = st.session_state.persona_agent.generate_encouragement_message(
#             context="hint_request",
#             skill_level=st.session_state.skill_level or "Intermediate"
#         )
#         st.session_state.code_conversation.append({
#             "role": "code_agent",
#             "content": encouragement
#         })
        
#         st.session_state.code_conversation = manage_chat_history(st.session_state.code_conversation)
#         st.rerun()
#     except Exception as e:
#         logging.error(f"Code question processing failed: {e}")
#         st.error("Error answering question. Please try again.")
#         st.session_state.code_conversation.append({
#             "role": "system",
#             "content": "⚠️ Error processing question."
#         })

# def render_app():
#     render_top_nav()
    
#     get_gemini_model()
    
#     if not st.session_state.skill_level:
#         st.markdown("### 🎓 Select Your Skill Level")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button("Beginner", use_container_width=True):
#                 st.session_state.skill_level = "Beginner"
#                 st.session_state.orchestrator.log_user_interaction("skill_level_selected", {"level": "Beginner"})
#                 st.rerun()
#         with col2:
#             if st.button("Intermediate", use_container_width=True):
#                 st.session_state.skill_level = "Intermediate"
#                 st.session_state.orchestrator.log_user_interaction("skill_level_selected", {"level": "Intermediate"})
#                 st.rerun()
#         with col3:
#             if st.button("Advanced", use_container_width=True):
#                 st.session_state.skill_level = "Advanced"
#                 st.session_state.orchestrator.log_user_interaction("skill_level_selected", {"level": "Advanced"})
#                 st.rerun()
#         return
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         render_problem_panel()
    
#     with col2:
#         current_state = st.session_state.orchestrator.get_current_state()
#         if current_state == "mentoring":
#             render_mentor_panel()
#         elif current_state == "coding":
#             render_code_panel()
#         elif current_state == "evaluation":
#             render_evaluation_panel()

# if __name__ == "__main__":
#     render_app()