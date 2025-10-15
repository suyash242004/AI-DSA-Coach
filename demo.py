import streamlit as st
import json
from agents.mentor_agent import MentorAgent
from agents.code_agent import CodeAgent
from agents.evaluation_agent import EvaluationAgent
from agents.orchestrator import AgentOrchestrator
from datetime import datetime, timedelta, date

# Web3 Integration (Optional)
try:
    from utils.web3_client import web3_client
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    web3_client = None

# Page configuration
st.set_page_config(
    page_title="AI DSA Coach - Web3 Learning",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for LeetCode-like styling with Web3 elements
st.markdown("""
<style>
    /* Hide default sidebar */
    .css-1d391kg {display: none;}
    
    /* Main container styling */
    .main-container {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Web3 Enhancement Bar - Hidden by default */
    .web3-enhancement-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        display: none;
        font-size: 14px;
        position: relative;
        overflow: hidden;
    }
    
    .web3-enhancement-bar.show {
        display: block;
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .web3-toggle {
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    
    .web3-toggle:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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
    
    /* Web3 styling */
    .wallet-connected {
        background: #e6fffa;
        border: 1px solid #14b8a6;
        padding: 8px 16px;
        border-radius: 8px;
        color: #0f766e;
        font-weight: 600;
    }
    
    .nft-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        margin: 4px;
        display: inline-block;
    }
    
    .token-display {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
        color: #000;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    
    .web3-transaction {
        background: linear-gradient(135deg, #00d4aa 0%, #00a86b 100%);
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        font-size: 14px;
        font-weight: 500;
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
        "active_tab": "problem",
        
        # Web3 Integration (Optional)
        "web3_enabled": False,
        "wallet_connected": False,
        "user_wallet_address": None,
        "dsa_tokens": 10,  # Starting tokens (simulated if Web3 not available)
        "total_earned_tokens": 0,
        "daily_login_streak": 0,
        "last_login_date": None,
        "problems_solved_today": 0,
        "completed_problems": set(),  # Track unique problems solved
        "nft_certificates": [],  # Store NFT-like certificates
        "web3_transactions": [],  # Track transactions
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Web3 Functions (Enhanced but Optional)
def init_web3():
    """Initialize Web3 connection if available"""
    if WEB3_AVAILABLE and web3_client:
        try:
            return web3_client.initialize()
        except Exception as e:
            st.error(f"Web3 initialization failed: {e}")
    return False

def award_tokens_web3(amount: int, reason: str):
    """Award tokens via Web3 if available, otherwise simulate"""
    if st.session_state.web3_enabled and st.session_state.wallet_connected:
        try:
            # Real Web3 transaction
            if WEB3_AVAILABLE:
                tx_hash = web3_client.transfer_dsa_tokens(
                    st.session_state.user_wallet_address, 
                    amount
                )
                if tx_hash:
                    st.session_state.web3_transactions.append({
                        "type": "token_award",
                        "hash": tx_hash,
                        "amount": amount,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.markdown(f'''
                    <div class="web3-transaction">
                        🎉 +{amount} DSA tokens earned on blockchain! {reason}
                    </div>
                    ''', unsafe_allow_html=True)
                    return tx_hash
        except Exception as e:
            st.error(f"Web3 transaction failed: {e}")
    
    # Fallback to simulation
    st.session_state.dsa_tokens += amount
    st.session_state.total_earned_tokens += amount
    st.success(f"🎉 +{amount} DSA tokens earned! {reason}")
    return None

def mint_nft_web3(problem: dict, skill_level: str):
    """Mint NFT via Web3 if available, otherwise simulate"""
    if st.session_state.web3_enabled and st.session_state.wallet_connected:
        try:
            if WEB3_AVAILABLE:
                tx_hash = web3_client.mint_nft_badge(
                    st.session_state.user_wallet_address,
                    problem["title"],
                    problem["difficulty"]
                )
                if tx_hash:
                    certificate = {
                        "problem_title": problem["title"],
                        "difficulty": problem["difficulty"],
                        "skill_level": skill_level,
                        "tx_hash": tx_hash,
                        "timestamp": datetime.now().isoformat(),
                        "blockchain": True
                    }
                    st.session_state.nft_certificates.append(certificate)
                    st.markdown(f'''
                    <div class="web3-transaction">
                        🏆 NFT Certificate minted on blockchain for {problem["title"]}!
                    </div>
                    ''', unsafe_allow_html=True)
                    return
        except Exception as e:
            st.error(f"NFT minting failed: {e}")
    
    # Fallback to simulation
    certificate = {
        "problem_title": problem["title"],
        "difficulty": problem["difficulty"],
        "skill_level": skill_level,
        "timestamp": datetime.now().isoformat(),
        "blockchain": False
    }
    st.session_state.nft_certificates.append(certificate)
    st.success(f"🎨 NFT Certificate earned for {problem['title']}!")

# Web3 Enhancement Bar
def render_web3_toggle():
    """Render Web3 toggle button"""
    if WEB3_AVAILABLE:
        if st.button("🌐 Web3 Mode", key="web3_toggle", help="Toggle Web3 blockchain features"):
            st.session_state.web3_enabled = not st.session_state.web3_enabled
            if st.session_state.web3_enabled:
                if init_web3():
                    st.success("Web3 mode enabled! Connect your wallet to earn real tokens.")
                else:
                    st.session_state.web3_enabled = False
                    st.error("Failed to initialize Web3 connection")
            st.rerun()

def render_web3_enhancement_bar():
    """Render optional Web3 enhancement bar"""
    if st.session_state.web3_enabled:
        st.markdown('<div class="web3-enhancement-bar show">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.wallet_connected:
                st.markdown(f'<div class="wallet-connected">🟢 Wallet Connected</div>', unsafe_allow_html=True)
            else:
                if st.button("🔗 Connect Wallet", key="connect_wallet_btn"):
                    # Simulate wallet connection
                    st.session_state.user_wallet_address = "0x742d35Cc6634C0532925a3b8D5c27Aa4fCd52Ed2"
                    st.session_state.wallet_connected = True
                    st.success("Wallet connected!")
                    st.rerun()
        
        with col2:
            st.markdown(f'<div class="token-display">💰 {st.session_state.dsa_tokens} DSA</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"🏆 **NFTs:** {len(st.session_state.nft_certificates)}")
        
        with col4:
            if st.button("❌ Disable Web3", key="disable_web3"):
                st.session_state.web3_enabled = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Your Original Functions (Preserved)
def render_top_nav():
    problem_titles = [p["title"] for p in problems]
    
    with st.container():
        st.markdown('<div class="top-nav">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 2, 2, 2, 1, 1])
        
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
                        text=f"🔍 {progress['current_phase']} ({progress['progress_percentage']}%)")
        
        with col5:
            if st.session_state.skill_level:
                skill_colors = {"Beginner": "#ff9800", "Intermediate": "#2196f3", "Advanced": "#4caf50"}
                color = skill_colors.get(st.session_state.skill_level, "#666")
                st.markdown(f'<span style="background:{color};color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;">🎯 {st.session_state.skill_level}</span>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<span style="background:#666;color:white;padding:4px 8px;border-radius:12px;font-size:11px;font-weight:600;">🎯 Detecting...</span>', 
                           unsafe_allow_html=True)
        
        with col6:
            # Web3 Toggle Button
            if WEB3_AVAILABLE:
                if st.button("🌐", key="web3_toggle_nav", help="Toggle Web3 Features"):
                    st.session_state.web3_enabled = not st.session_state.web3_enabled
                    if st.session_state.web3_enabled and not init_web3():
                        st.session_state.web3_enabled = False
                    st.rerun()
        
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
    
    # Web3 Rewards Info (if enabled)
    if st.session_state.web3_enabled:
        reward_amounts = {"Easy": 1, "Medium": 2, "Hard": 3}
        base_reward = reward_amounts[selected_problem["difficulty"]]
        
        st.markdown("### 🎁 Web3 Rewards")
        st.markdown(f"""
        - **Base Reward:** {base_reward} DSA tokens
        - **Efficiency Bonus:** +2 DSA (no hints used)
        - **NFT Certificate:** Minted on U2U blockchain
        """)

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
            skill_level=st.session_state.skill_level or "Intermediate",
            hints_used=st.session_state.hints_used,
            final_code=st.session_state.user_code,
            problem=selected_problem,
            conversation_history=st.session_state.mentor_conversation + st.session_state.code_conversation
        )
        
        # Performance summary
        st.markdown(evaluation["summary"])
        
        # Technical scores
        raw_data = evaluation.get("raw_data", {})
        tech_score = raw_data.get("technical_score", 0)
        approach_score = raw_data.get("approach_score", 0)
        
        # Progress bars for scores
        st.progress(tech_score / 10, text=f"🔧 Technical: {tech_score}/10")
        st.progress(approach_score / 10, text=f"🧠 Approach: {approach_score}/10")
        
        # Complexity analysis
        st.markdown("---")
        st.markdown(evaluation["complexity_analysis"])
        
        # Enhanced session summary with orchestrator analytics
        st.markdown("### 📈 Session Summary")
        analytics = st.session_state.orchestrator.get_session_analytics()
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
        
        # Web3 Token Rewards and NFT Minting (if enabled)
        if st.session_state.web3_enabled:
            st.markdown("### 💰 Web3 Rewards")
            problem_key = f"{st.session_state.current_problem}_{st.session_state.skill_level}"
            
            if problem_key not in st.session_state.completed_problems:
                # Calculate and award tokens
                difficulty_points = {'Easy': 1, 'Medium': 2, 'Hard': 3}
                base_reward = difficulty_points.get(selected_problem['difficulty'], 1)
                hint_bonus = max(0, 2 - st.session_state.hints_used)
                tokens_earned = base_reward + hint_bonus
                
                # Award tokens
                award_tokens_web3(tokens_earned, f"Solved {selected_problem['difficulty']} problem!")
                
                # Mint NFT certificate
                mint_nft_web3(selected_problem, st.session_state.skill_level or "Intermediate")
                
                st.session_state.completed_problems.add(problem_key)
                
                # Show breakdown
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Base Reward", f"{base_reward} DSA")
                with col2:
                    st.metric("Efficiency Bonus", f"+{hint_bonus} DSA")
                with col3:
                    st.metric("Total Earned", f"+{tokens_earned} DSA")
            else:
                st.info("💡 You've already earned rewards for this problem configuration!")
        
        # Actionable feedback
        st.markdown("---")
        st.markdown(evaluation["actionable_feedback"])
        
        # Action buttons
        st.markdown("---")
        st.markdown("### 🎯 Next Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Try New Problem", type="primary", use_container_width=True):
                st.session_state.orchestrator.complete_session()
                st.session_state.orchestrator.reset()
                st.session_state.mentor_conversation = []
                st.session_state.code_conversation = []
                st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
                st.session_state.approach_approved = False
                st.session_state.skill_level = None
                st.session_state.hints_used = 0
                st.rerun()
        
        with col2:
            if st.button("🧠 Discuss Approach", use_container_width=True):
                st.session_state.approach_approved = False
                safe_transition(st.session_state.orchestrator.transition_to_mentoring)
        
        with col3:
            if st.button("💻 Back to Coding", use_container_width=True):
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
                st.write(f"🔍 **Approach Approved:** {'✅ Yes' if st.session_state.approach_approved else '❌ No'}")
                st.write(f"💬 **Mentor Chats:** {mentor_msgs}")
                st.write(f"🔧 **Code Reviews:** {code_msgs}")
            else:
                st.info("Detailed analysis not available")

def process_mentor_input(user_input):
    with st.spinner("🤖 AI Mentor is analyzing your approach..."):
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
        
        st.session_state.orchestrator.log_user_interaction("hint_requested", {
            "hint_number": st.session_state.hints_used,
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
                st.session_state.skill_level or "Intermediate"
            )
            
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
            st.session_state.skill_level or "Intermediate"
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

def safe_transition(target_state_func):
    current_state = st.session_state.orchestrator.get_current_state()
    if target_state_func():
        st.success(f"✅ Moved to {st.session_state.orchestrator.get_current_state().title()} phase")
        st.rerun()
    else:
        st.error(f"❌ Cannot transition from {current_state} to requested state")

# Main App
def main():
    # Set current problem if not set
    if not st.session_state.current_problem:
        st.session_state.current_problem = problems[0]["title"]
        st.session_state.user_code = LANGUAGE_TEMPLATES[st.session_state.selected_language]
    
    # Render Web3 enhancement bar (optional)
    render_web3_enhancement_bar()
    
    # Render top navigation
    render_top_nav()
    
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
    
    # Web3 Dashboard (collapsible)
    if st.session_state.web3_enabled:
        with st.expander("🌐 Web3 Dashboard", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 DSA Balance", st.session_state.dsa_tokens)
            
            with col2:
                st.metric("🏆 NFT Certificates", len(st.session_state.nft_certificates))
            
            with col3:
                st.metric("📊 Problems Solved", len(st.session_state.completed_problems))
            
            with col4:
                usdc_convertible = st.session_state.dsa_tokens // 100
                st.metric("💵 USDC Available", usdc_convertible)
            
            # NFT Gallery
            if st.session_state.nft_certificates:
                st.markdown("### 🎨 NFT Certificates")
                cols = st.columns(3)
                for i, cert in enumerate(st.session_state.nft_certificates):
                    with cols[i % 3]:
                        blockchain_badge = "🔗" if cert.get("blockchain") else "📝"
                        st.markdown(f'''
                        <div class="nft-badge">
                            {blockchain_badge} {cert["problem_title"]}
                            <br><small>{cert["difficulty"]} • {cert["skill_level"]}</small>
                        </div>
                        ''', unsafe_allow_html=True)
            
            # Recent Web3 Transactions
            if st.session_state.web3_transactions:
                st.markdown("### 📜 Recent Blockchain Transactions")
                for tx in st.session_state.web3_transactions[-3:]:
                    st.markdown(f"**{tx['type'].title()}** - {tx['amount']} DSA - Hash: `{tx['hash'][:10]}...`")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; padding: 20px;">'
        '🤖 <strong>AI DSA Coach</strong> - Your personalized DSA preparation companion'
        f'{" | 🌐 Web3 Mode Active" if st.session_state.web3_enabled else ""} | '
        f'Current Phase: {st.session_state.orchestrator.get_current_state().title()} | '
        f'Language: {st.session_state.selected_language}'
        '</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()