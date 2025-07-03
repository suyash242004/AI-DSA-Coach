from enum import Enum
from typing import Dict, Any, Optional
import time

class AgentState(Enum):
    MENTORING = "mentoring"
    CODING = "coding"
    EVALUATION = "evaluation"
    COMPLETED = "completed"

class AgentOrchestrator:
    """
    Manages the flow between different AI agents and tracks session state
    """
    
    def __init__(self):
        self.current_state = AgentState.MENTORING
        self.session_data = {
            "start_time": time.time(),
            "transitions": [],
            "user_interactions": 0,
            "hints_requested": 0,
            "code_submissions": 0
        }
        self.state_history = [AgentState.MENTORING]
    
    def get_current_state(self) -> str:
        """Get current state as string"""
        return self.current_state.value
    
    def get_active_agent(self) -> str:
        """Get the currently active agent name"""
        agent_mapping = {
            AgentState.MENTORING: "Mentor Agent",
            AgentState.CODING: "Code Agent", 
            AgentState.EVALUATION: "Evaluation Agent",
            AgentState.COMPLETED: "Session Complete"
        }
        return agent_mapping.get(self.current_state, "Unknown")
    
    def can_transition_to(self, target_state: AgentState) -> bool:
        """Check if transition to target state is allowed"""
        allowed_transitions = {
            AgentState.MENTORING: [AgentState.CODING],
            AgentState.CODING: [AgentState.MENTORING, AgentState.EVALUATION],
            AgentState.EVALUATION: [AgentState.MENTORING, AgentState.COMPLETED],
            AgentState.COMPLETED: [AgentState.MENTORING]
        }
        
        return target_state in allowed_transitions.get(self.current_state, [])
    
    def transition_to_coding(self) -> bool:
        """Transition from mentoring to coding phase"""
        if self.can_transition_to(AgentState.CODING):
            self._log_transition(self.current_state, AgentState.CODING)
            self.current_state = AgentState.CODING
            return True
        return False
    
    def transition_to_mentoring(self) -> bool:
        """Transition back to mentoring phase"""
        if self.can_transition_to(AgentState.MENTORING):
            self._log_transition(self.current_state, AgentState.MENTORING)
            self.current_state = AgentState.MENTORING
            return True
        return False
    
    def transition_to_evaluation(self) -> bool:
        """Transition to evaluation phase"""
        if self.can_transition_to(AgentState.EVALUATION):
            self._log_transition(self.current_state, AgentState.EVALUATION)
            self.current_state = AgentState.EVALUATION
            return True
        return False
    
    def complete_session(self) -> bool:
        """Mark session as completed"""
        if self.can_transition_to(AgentState.COMPLETED):
            self._log_transition(self.current_state, AgentState.COMPLETED)
            self.current_state = AgentState.COMPLETED
            self.session_data["end_time"] = time.time()
            return True
        return False
    
    def reset(self):
        """Reset orchestrator to initial state"""
        self.current_state = AgentState.MENTORING
        self.session_data = {
            "start_time": time.time(),
            "transitions": [],
            "user_interactions": 0,
            "hints_requested": 0,
            "code_submissions": 0
        }
        self.state_history = [AgentState.MENTORING]
    
    def _log_transition(self, from_state: AgentState, to_state: AgentState):
        """Log state transitions for analytics"""
        transition = {
            "from": from_state.value,
            "to": to_state.value,
            "timestamp": time.time(),
            "duration_in_previous_state": time.time() - self.session_data.get("last_transition_time", self.session_data["start_time"])
        }
        
        self.session_data["transitions"].append(transition)
        self.session_data["last_transition_time"] = time.time()
        self.state_history.append(to_state)
    
    def log_user_interaction(self, interaction_type: str, details: Optional[Dict[str, Any]] = None):
        """Log user interactions for session analytics"""
        interaction = {
            "type": interaction_type,
            "timestamp": time.time(),
            "state": self.current_state.value,
            "details": details or {}
        }
        
        if "interactions" not in self.session_data:
            self.session_data["interactions"] = []
        
        self.session_data["interactions"].append(interaction)
        self.session_data["user_interactions"] += 1
        
        # Update specific counters
        if interaction_type == "hint_requested":
            self.session_data["hints_requested"] += 1
        elif interaction_type == "code_submitted":
            self.session_data["code_submissions"] += 1
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get comprehensive session analytics"""
        current_time = time.time()
        total_duration = current_time - self.session_data["start_time"]
        
        analytics = {
            "total_duration": total_duration,
            "current_state": self.current_state.value,
            "states_visited": len(set(self.state_history)),
            "total_transitions": len(self.session_data["transitions"]),
            "user_interactions": self.session_data["user_interactions"],
            "hints_requested": self.session_data["hints_requested"],
            "code_submissions": self.session_data["code_submissions"],
            "time_per_state": self._calculate_time_per_state(),
            "interaction_frequency": self.session_data["user_interactions"] / max(total_duration / 60, 0.1)  # interactions per minute
        }
        
        return analytics
    
    def _calculate_time_per_state(self) -> Dict[str, float]:
        """Calculate time spent in each state"""
        time_per_state = {}
        current_time = time.time()
        
        if not self.session_data["transitions"]:
            # Only been in initial state
            time_per_state[AgentState.MENTORING.value] = current_time - self.session_data["start_time"]
        else:
            # Calculate time for each transition
            prev_time = self.session_data["start_time"]
            prev_state = AgentState.MENTORING.value
            
            for transition in self.session_data["transitions"]:
                duration = transition["timestamp"] - prev_time
                time_per_state[prev_state] = time_per_state.get(prev_state, 0) + duration
                
                prev_time = transition["timestamp"]
                prev_state = transition["to"]
            
            # Add time for current state
            current_duration = current_time - prev_time
            time_per_state[prev_state] = time_per_state.get(prev_state, 0) + current_duration
        
        return time_per_state
    
    def get_next_recommended_action(self) -> str:
        """Get recommended next action based on current state and history"""
        recommendations = {
            AgentState.MENTORING: "Continue discussing your approach with the mentor until you're confident, then move to coding.",
            AgentState.CODING: "Write and test your solution. Use the code assistant if you need help debugging or optimizing.",
            AgentState.EVALUATION: "Review your performance analysis and consider starting a new problem.",
            AgentState.COMPLETED: "Great job! Ready to tackle another problem?"
        }
        
        return recommendations.get(self.current_state, "Continue with the current phase.")
    
    def should_suggest_hint(self) -> bool:
        """Determine if a hint should be suggested based on session analytics"""
        analytics = self.get_session_analytics()
        
        # Suggest hint if user has been in mentoring state for too long without progress
        if (self.current_state == AgentState.MENTORING and 
            analytics["time_per_state"].get("mentoring", 0) > 300 and  # 5 minutes
            analytics["hints_requested"] == 0):
            return True
        
        return False
    
    # def get_progress_summary(self) -> Dict[str, Any]:
    #     analytics = self.get_session_analytics()
    
    #     # Map states to your actual UI
    #     if self.current_state in [AgentState.MENTORING]:
    #         progress_percentage = 33
    #         phase_name = "Mentor Agent"
    #     elif self.current_state in [AgentState.CODING]:
    #         progress_percentage = 67
    #         phase_name = "Code Agent"
    #     elif self.current_state in [AgentState.EVALUATION, AgentState.COMPLETED]:
    #         progress_percentage = 100
    #         phase_name = "Evaluation Agent"
    #     else:
    #         progress_percentage = 0
    #         phase_name = "Unknown"
    
    #     return {
    #         "progress_percentage": progress_percentage,
    #         "current_phase": self.get_active_agent(),
    #         "time_spent": analytics["total_duration"],
    #         "interactions": analytics["user_interactions"],
    #         "next_action": self.get_next_recommended_action()
    #     }
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of user's progress through the session"""
        analytics = self.get_session_analytics()
        
        progress_percentage = 0
        if self.current_state == AgentState.MENTORING:
            progress_percentage = 33
        elif self.current_state == AgentState.CODING:
            progress_percentage = 67
        elif self.current_state == AgentState.EVALUATION:
            progress_percentage = 100
        elif self.current_state == AgentState.COMPLETED:
            progress_percentage = 100
        
        return {
            "progress_percentage": progress_percentage,
            "current_phase": self.get_active_agent(),
            "time_spent": analytics["total_duration"],
            "interactions": analytics["user_interactions"],
            "next_action": self.get_next_recommended_action()
        }
   
    
    