from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime, timedelta

class PersonaAgent:
    """
    Manages user persona and adaptive behavior based on skill level and performance
    """
    
    def __init__(self):
        self.persona_profiles = {
            "Beginner": {
                "tone": "supportive",
                "patience_level": "high",
                "explanation_detail": "high",
                "encouragement_frequency": "high",
                "complexity_introduction": "gradual",
                "hint_directness": "direct",
                "motivation_style": "achievement-focused"
            },
            "Intermediate": {
                "tone": "encouraging",
                "patience_level": "medium",
                "explanation_detail": "medium",
                "encouragement_frequency": "medium",
                "complexity_introduction": "moderate",
                "hint_directness": "guided",
                "motivation_style": "progress-focused"
            },
            "Advanced": {
                "tone": "challenging",
                "patience_level": "low",
                "explanation_detail": "low",
                "encouragement_frequency": "low",
                "complexity_introduction": "immediate",
                "hint_directness": "subtle",
                "motivation_style": "mastery-focused"
            }
        }
        
        self.interaction_history = []
        self.performance_indicators = {
            "confidence_level": 0.5,  # 0-1 scale
            "frustration_level": 0.0,  # 0-1 scale
            "engagement_level": 0.5,   # 0-1 scale
            "learning_velocity": 0.5   # 0-1 scale
        }
    
    def get_user_profile(self, skill_level: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get personalized user profile with adaptive messaging"""
        
        base_profile = self.persona_profiles.get(skill_level, self.persona_profiles["Intermediate"])
        
        # Adapt profile based on session performance
        if session_data:
            adapted_profile = self._adapt_profile(base_profile, session_data, skill_level)
        else:
            adapted_profile = base_profile.copy()
        
        # Generate persona message
        persona_message = self._generate_persona_message(skill_level, adapted_profile, session_data)
        
        return {
            **adapted_profile,
            "skill_level": skill_level,
            "persona_message": persona_message,
            "interaction_style": self._get_interaction_style(skill_level, session_data),
            "motivation_message": self._get_motivation_message(skill_level, session_data)
        }
    
    def _adapt_profile(self, base_profile: Dict[str, str], session_data: Dict[str, Any], skill_level: str) -> Dict[str, str]:
        """Adapt persona profile based on real-time session data"""
        
        adapted = base_profile.copy()
        
        # Analyze session indicators
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        interactions = session_data.get("user_interactions", 0)
        
        # Adjust based on hint usage
        if hints_used > 3:
            # User is struggling, increase support
            if skill_level == "Advanced":
                adapted["tone"] = "encouraging"
                adapted["hint_directness"] = "guided"
            adapted["encouragement_frequency"] = "high"
            adapted["patience_level"] = "high"
        elif hints_used == 0 and time_spent > 300:  # 5 minutes without hints
            # User might be stuck but not asking for help
            adapted["encouragement_frequency"] = "medium"
        
        # Adjust based on time spent
        if time_spent > 900:  # 15 minutes
            adapted["patience_level"] = "high"
            adapted["encouragement_frequency"] = "high"
        
        # Adjust based on interaction frequency
        interaction_rate = interactions / max(time_spent / 60, 0.1)  # interactions per minute
        if interaction_rate < 0.5:  # Low engagement
            adapted["encouragement_frequency"] = "high"
            adapted["motivation_style"] = "engagement-focused"
        
        return adapted
    
    def _generate_persona_message(self, skill_level: str, profile: Dict[str, str], session_data: Dict[str, Any] = None) -> str:
        """Generate personalized message based on current context"""
        
        messages = {
            "Beginner": {
                "default": "You're doing great! Every expert was once a beginner. Take your time and think through each step. 🌟",
                "struggling": "Don't worry if this feels challenging - that's how learning happens! Let's break it down together. 💪",
                "progressing": "Excellent progress! You're building strong problem-solving foundations. Keep it up! 🚀",
                "confident": "Look at you go! Your logical thinking is really developing. I'm proud of your effort! 🎯"
            },
            "Intermediate": {
                "default": "You're developing solid DSA skills! Focus on patterns and you'll see improvement quickly. 👍",
                "struggling": "This is a good challenge for your level. Use it as a learning opportunity to strengthen your skills. 🧠",
                "progressing": "Nice work! You're connecting concepts well. Ready to tackle more complex problems? 🎪",
                "confident": "Your problem-solving approach is getting sophisticated. Time to explore advanced techniques! 💡"
            },
            "Advanced": {
                "default": "Ready for some serious problem-solving? Let's see that algorithmic thinking in action! 🔥",
                "struggling": "Even the best engineers face tough problems. This is where real learning happens. 🏆",
                "progressing": "Solid analysis! Your systematic approach shows real expertise. 🎯",
                "confident": "Impressive work! You're thinking like a senior engineer. Challenge yourself further! 🚀"
            }
        }
        
        # Determine user state
        if session_data:
            hints_used = session_data.get("hints_requested", 0)
            time_spent = session_data.get("total_duration", 0)
            
            if hints_used > 3 or time_spent > 900:
                state = "struggling"
            elif hints_used <= 1 and time_spent < 300:
                state = "confident"
            elif session_data.get("user_interactions", 0) > 3:
                state = "progressing"
            else:
                state = "default"
        else:
            state = "default"
        
        return messages.get(skill_level, messages["Intermediate"]).get(state, messages["Intermediate"]["default"])
    
    def _get_interaction_style(self, skill_level: str, session_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Get specific interaction style guidelines"""
        
        styles = {
            "Beginner": {
                "question_style": "Simple, direct questions that guide thinking",
                "feedback_style": "Detailed explanations with examples",
                "hint_style": "Step-by-step guidance with clear direction",
                "encouragement": "Frequent positive reinforcement"
            },
            "Intermediate": {
                "question_style": "Thought-provoking questions about patterns",
                "feedback_style": "Balanced analysis with suggestions",
                "hint_style": "Nudges toward the right approach",
                "encouragement": "Recognition of progress and growth"
            },
            "Advanced": {
                "question_style": "Challenging questions about optimization",
                "feedback_style": "Technical analysis with edge cases",
                "hint_style": "Subtle suggestions and counterexamples",
                "encouragement": "Acknowledgment of expertise"
            }
        }
        
        return styles.get(skill_level, styles["Intermediate"])
    
    def _get_motivation_message(self, skill_level: str, session_data: Dict[str, Any] = None) -> str:
        """Get motivational message based on skill level and performance"""
        
        if not session_data:
            return self._get_default_motivation(skill_level)
        
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        
        # Performance-based motivation
        if hints_used == 0 and time_spent < 600:  # Quick solve without hints
            return "🏆 Outstanding! You solved this independently and efficiently!"
        elif hints_used <= 2:
            return "💪 Great job! You used hints strategically and found the solution!"
        elif hints_used > 3:
            return "🌟 Persistence pays off! Every hint used is a step toward understanding!"
        elif time_spent > 900:  # Long session
            return "⏰ Your dedication shows! Sometimes the best learning happens when we stick with challenging problems!"
        else:
            return self._get_default_motivation(skill_level)
    
    def _get_default_motivation(self, skill_level: str) -> str:
        """Get default motivational message for skill level"""
        
        defaults = {
            "Beginner": "🌱 Every step forward is progress! You're building the foundation for great things!",
            "Intermediate": "🚀 You're gaining momentum! Each problem solved makes you stronger!",
            "Advanced": "⚡ Push your limits! Your expertise grows with every challenge!"
        }
        
        return defaults.get(skill_level, defaults["Intermediate"])
    
    def update_performance_indicators(self, session_data: Dict[str, Any]) -> None:
        """Update performance indicators based on session data"""
        
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        interactions = session_data.get("user_interactions", 0)
        successful_completion = session_data.get("completed", False)
        
        # Update confidence level
        if successful_completion and hints_used <= 2:
            self.performance_indicators["confidence_level"] = min(1.0, 
                self.performance_indicators["confidence_level"] + 0.1)
        elif hints_used > 4:
            self.performance_indicators["confidence_level"] = max(0.0, 
                self.performance_indicators["confidence_level"] - 0.1)
        
        # Update frustration level
        if hints_used > 3 or time_spent > 1200:  # 20 minutes
            self.performance_indicators["frustration_level"] = min(1.0, 
                self.performance_indicators["frustration_level"] + 0.2)
        elif successful_completion:
            self.performance_indicators["frustration_level"] = max(0.0, 
                self.performance_indicators["frustration_level"] - 0.15)
        
        # Update engagement level
        interaction_rate = interactions / max(time_spent / 60, 0.1)
        if interaction_rate > 1.0:
            self.performance_indicators["engagement_level"] = min(1.0, 
                self.performance_indicators["engagement_level"] + 0.1)
        elif interaction_rate < 0.3:
            self.performance_indicators["engagement_level"] = max(0.0, 
                self.performance_indicators["engagement_level"] - 0.1)
        
        # Update learning velocity
        if successful_completion and time_spent < 600:  # Quick completion
            self.performance_indicators["learning_velocity"] = min(1.0, 
                self.performance_indicators["learning_velocity"] + 0.1)
        elif time_spent > 1800:  # 30 minutes
            self.performance_indicators["learning_velocity"] = max(0.0, 
                self.performance_indicators["learning_velocity"] - 0.05)
    
    def get_adaptive_hint_strategy(self, skill_level: str, current_hints: int) -> Dict[str, Any]:
        """Get adaptive hint strategy based on skill level and current hint count"""
        
        strategies = {
            "Beginner": {
                "max_hints": 5,
                "hint_progression": ["conceptual", "structural", "implementation", "debugging", "solution"],
                "hint_detail": "high",
                "wait_time": 30  # seconds before offering next hint
            },
            "Intermediate": {
                "max_hints": 4,
                "hint_progression": ["approach", "algorithm", "optimization", "edge_cases"],
                "hint_detail": "medium",
                "wait_time": 60
            },
            "Advanced": {
                "max_hints": 3,
                "hint_progression": ["direction", "complexity", "edge_case"],
                "hint_detail": "low",
                "wait_time": 120
            }
        }
        
        strategy = strategies.get(skill_level, strategies["Intermediate"])
        
        # Adapt based on performance indicators
        if self.performance_indicators["frustration_level"] > 0.7:
            strategy["max_hints"] += 1
            strategy["wait_time"] = max(15, strategy["wait_time"] // 2)
        elif self.performance_indicators["confidence_level"] > 0.8:
            strategy["max_hints"] = max(1, strategy["max_hints"] - 1)
            strategy["wait_time"] *= 2
        
        return strategy
    
    def get_difficulty_adjustment(self, skill_level: str, recent_performance: List[Dict[str, Any]]) -> str:
        """Suggest difficulty adjustment based on recent performance"""
        
        if not recent_performance:
            return "maintain"
        
        # Analyze recent sessions
        avg_hints = sum(session.get("hints_requested", 0) for session in recent_performance) / len(recent_performance)
        avg_time = sum(session.get("total_duration", 0) for session in recent_performance) / len(recent_performance)
        completion_rate = sum(1 for session in recent_performance if session.get("completed", False)) / len(recent_performance)
        
        # Decision logic
        if completion_rate > 0.8 and avg_hints < 2 and avg_time < 600:
            return "increase"  # User is finding it too easy
        elif completion_rate < 0.3 or avg_hints > 4 or avg_time > 1200:
            return "decrease"  # User is struggling
        else:
            return "maintain"
    
    def generate_encouragement_message(self, context: str, skill_level: str) -> str:
        """Generate contextual encouragement message"""
        
        encouragements = {
            "Beginner": {
                "hint_request": "Great question! Asking for help shows wisdom. Let me guide you through this! 🤝",
                "long_pause": "Take your time! Complex thinking requires patience. You're on the right track! ⏰",
                "multiple_attempts": "I love your persistence! Each attempt teaches you something valuable! 💪",
                "near_solution": "You're so close! Trust your instincts and take the next step! 🎯"
            },
            "Intermediate": {
                "hint_request": "Smart approach! Using hints strategically is a key problem-solving skill! 🧠",
                "long_pause": "Deep thinking in action! Sometimes the best solutions come after careful consideration! 🤔",
                "multiple_attempts": "Your iterative approach shows real engineering mindset! Keep refining! 🔧",
                "near_solution": "Your analysis is solid! One more insight and you'll crack this! 💡"
            },
            "Advanced": {
                "hint_request": "Even experts consult resources! This shows good judgment and efficiency! 📚",
                "long_pause": "Thorough analysis leads to elegant solutions. Your methodical approach is impressive! 🎓",
                "multiple_attempts": "Optimization through iteration - that's advanced problem-solving! 🚀",
                "near_solution": "Your systematic approach is paying off! The solution is within reach! 🏆"
            }
        }
        
        return encouragements.get(skill_level, encouragements["Intermediate"]).get(context, 
               "You're doing great! Keep up the excellent work! 🌟")
    
    def record_interaction(self, interaction_type: str, context: Dict[str, Any]) -> None:
        """Record user interaction for learning and adaptation"""
        
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "context": context,
            "performance_snapshot": self.performance_indicators.copy()
        }
        
        self.interaction_history.append(interaction_record)
        
        # Keep only last 50 interactions to manage memory
        if len(self.interaction_history) > 50:
            self.interaction_history = self.interaction_history[-50:]
    
    def get_session_summary(self, session_data: Dict[str, Any], skill_level: str) -> Dict[str, Any]:
        """Generate comprehensive session summary with insights"""
        
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        completed = session_data.get("completed", False)
        interactions = session_data.get("user_interactions", 0)
        
        # Performance analysis
        performance_level = "excellent" if (hints_used <= 1 and time_spent < 300 and completed) else \
                           "good" if (hints_used <= 3 and completed) else \
                           "needs_improvement"
        
        # Generate insights
        insights = []
        if hints_used == 0 and completed:
            insights.append("Independent problem-solving - excellent work!")
        if time_spent < 300 and completed:
            insights.append("Efficient solution - great time management!")
        if interactions > 5:
            insights.append("High engagement - shows strong learning mindset!")
        if hints_used > 3:
            insights.append("Consider reviewing fundamental concepts to reduce hint dependency")
        
        # Recommendations
        recommendations = self._generate_recommendations(skill_level, session_data)
        
        return {
            "performance_level": performance_level,
            "insights": insights,
            "recommendations": recommendations,
            "next_difficulty": self.get_difficulty_adjustment(skill_level, [session_data]),
            "encouragement": self._get_motivation_message(skill_level, session_data),
            "skill_progress": self._assess_skill_progress(skill_level, session_data)
        }
    
    def _generate_recommendations(self, skill_level: str, session_data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on session performance"""
        
        recommendations = []
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        
        if hints_used > 3:
            if skill_level == "Beginner":
                recommendations.append("Review basic concepts before attempting similar problems")
                recommendations.append("Practice smaller, similar problems to build confidence")
            else:
                recommendations.append("Consider breaking down complex problems into smaller steps")
                recommendations.append("Focus on pattern recognition in similar problem types")
        
        if time_spent > 900:  # 15 minutes
            recommendations.append("Try setting time limits to improve efficiency")
            recommendations.append("Practice explaining your approach out loud")
        
        if session_data.get("user_interactions", 0) < 2:
            recommendations.append("Don't hesitate to ask questions or request hints when stuck")
            recommendations.append("Engage more with the learning process for better understanding")
        
        return recommendations
    
    def _assess_skill_progress(self, skill_level: str, session_data: Dict[str, Any]) -> str:
        """Assess skill progress based on session performance"""
        
        hints_used = session_data.get("hints_requested", 0)
        time_spent = session_data.get("total_duration", 0)
        completed = session_data.get("completed", False)
        
        if completed and hints_used <= 1 and time_spent < 300:
            return "advancing_rapidly"
        elif completed and hints_used <= 2:
            return "steady_progress"
        elif completed:
            return "gradual_improvement"
        else:
            return "needs_practice"