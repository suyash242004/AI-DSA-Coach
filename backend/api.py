# 0G Hackathon 2026 - AI DSA Coach Backend API
# FastAPI wrapper around the existing multi-agent system

import sys
import os

# Add parent directory to path so agents/ and utils/ are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from agents.mentor_agent import MentorAgent
from agents.code_agent import CodeAgent
from agents.evaluation_agent import EvaluationAgent
from agents.orchestrator import AgentOrchestrator

app = FastAPI(title="AI DSA Coach API", version="1.0.0")

# Allow requests from Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-memory session store (keyed by session_id) ───────────────────────────
sessions: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in sessions:
        sessions[session_id] = {
            "mentor": MentorAgent(),
            "code": CodeAgent(),
            "evaluator": EvaluationAgent(),
            "orchestrator": AgentOrchestrator(),
            "mentor_conversation": [],
            "code_conversation": [],
            "skill_level": None,
            "hints_used": 0,
            "user_code": "",
            "approach_approved": False,
        }
    return sessions[session_id]

# ─── Request / Response Models ────────────────────────────────────────────────

class MentorAnalyzeRequest(BaseModel):
    session_id: str
    user_input: str
    problem: Dict[str, Any]

class MentorHintRequest(BaseModel):
    session_id: str
    skill_level: str
    problem: Dict[str, Any]

class CodeEvaluateRequest(BaseModel):
    session_id: str
    user_code: str
    problem: Dict[str, Any]
    skill_level: Optional[str] = "Intermediate"
    language: Optional[str] = "python"

class CodeAssistRequest(BaseModel):
    session_id: str
    question: str
    user_code: str
    problem: Dict[str, Any]
    skill_level: Optional[str] = "Intermediate"

class EvaluateRequest(BaseModel):
    session_id: str
    problem: Dict[str, Any]
    user_code: str
    skill_level: Optional[str] = "Intermediate"
    hints_used: Optional[int] = 0

class ResetRequest(BaseModel):
    session_id: str

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "message": "AI DSA Coach API is running 🚀"}

@app.get("/problems")
def get_problems():
    """Load problems from the shared JSON file"""
    problems_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "problems.json"
    )
    try:
        with open(problems_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="problems.json not found")

@app.post("/mentor/analyze")
def mentor_analyze(req: MentorAnalyzeRequest):
    """Analyze user's approach with the Mentor Agent"""
    session = get_session(req.session_id)
    agent: MentorAgent = session["mentor"]

    session["mentor_conversation"].append({"role": "user", "content": req.user_input})

    result = agent.analyze_approach(
        user_input=req.user_input,
        problem=req.problem,
        current_skill_level=session["skill_level"]
    )

    if result.get("skill_level"):
        session["skill_level"] = result["skill_level"]

    session["mentor_conversation"].append({"role": "mentor", "content": result.get("message", "")})

    if result.get("approved"):
        session["approach_approved"] = True
        session["orchestrator"].transition_to_coding()

    if result.get("hint"):
        session["hints_used"] += 1

    return {
        **result,
        "conversation": session["mentor_conversation"],
        "state": session["orchestrator"].get_current_state(),
    }

@app.post("/mentor/hint")
def mentor_hint(req: MentorHintRequest):
    """Get a progressive hint from the Mentor Agent"""
    session = get_session(req.session_id)
    agent: MentorAgent = session["mentor"]

    hint = agent.give_hint(req.skill_level, req.problem)
    session["hints_used"] += 1
    session["mentor_conversation"].append({"role": "mentor", "content": f"💡 **Hint:** {hint}"})

    return {
        "hint": hint,
        "hints_used": session["hints_used"],
        "conversation": session["mentor_conversation"],
    }

@app.post("/code/evaluate")
def code_evaluate(req: CodeEvaluateRequest):
    """Evaluate user's code with the Code Agent"""
    session = get_session(req.session_id)
    agent: CodeAgent = session["code"]
    session["user_code"] = req.user_code

    result = agent.evaluate_code(
        user_code=req.user_code,
        problem=req.problem,
        skill_level=req.skill_level or session["skill_level"] or "Intermediate",
        language=req.language or "python"
    )

    session["code_conversation"].append({
        "role": "system",
        "content": f"**Code Test Results:**\n{result.get('feedback', '')}"
    })

    return result

@app.post("/code/assist")
def code_assist(req: CodeAssistRequest):
    """Chat assistance from the Code Agent"""
    session = get_session(req.session_id)
    agent: CodeAgent = session["code"]

    response = agent.chat_assistance(
        question=req.question,
        user_code=req.user_code,
        problem=req.problem,
        skill_level=req.skill_level or session["skill_level"] or "Intermediate"
    )

    session["code_conversation"].append({"role": "user", "content": req.question})
    session["code_conversation"].append({"role": "code_agent", "content": response})

    return {"response": response, "conversation": session["code_conversation"]}

@app.post("/evaluate")
def evaluate_session(req: EvaluateRequest):
    """Generate full session evaluation"""
    session = get_session(req.session_id)
    agent: EvaluationAgent = session["evaluator"]

    conversation = session["mentor_conversation"] + session["code_conversation"]

    result = agent.generate_evaluation(
        skill_level=req.skill_level or session["skill_level"] or "Intermediate",
        hints_used=req.hints_used or session["hints_used"],
        final_code=req.user_code or session["user_code"],
        problem=req.problem,
        conversation_history=conversation
    )

    analytics = session["orchestrator"].get_session_analytics()
    return {**result, "analytics": analytics}

@app.get("/session/{session_id}/state")
def get_state(session_id: str):
    """Get current orchestrator state for a session"""
    session = get_session(session_id)
    orch: AgentOrchestrator = session["orchestrator"]
    return {
        "state": orch.get_current_state(),
        "active_agent": orch.get_active_agent(),
        "skill_level": session["skill_level"],
        "hints_used": session["hints_used"],
        "approach_approved": session["approach_approved"],
        "progress": orch.get_progress_summary(),
    }

@app.post("/session/reset")
def reset_session(req: ResetRequest):
    """Reset a session for a new problem"""
    if req.session_id in sessions:
        del sessions[req.session_id]
    get_session(req.session_id)  # re-initialise fresh
    return {"status": "reset", "session_id": req.session_id}
