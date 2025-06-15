from utils.gemini_client import get_gemini_model
import json
import re
from typing import Dict, List, Any

class EvaluationAgent:
    def __init__(self):
        self.model = get_gemini_model()
    
    def generate_evaluation(self, skill_level: str, hints_used: int, final_code: str, 
                          problem: dict, conversation_history: List[dict]) -> Dict[str, str]:
        """
        Generate comprehensive evaluation of the learning session
        """
        
        # Analyze conversation quality
        conversation_analysis = self._analyze_conversation(conversation_history, skill_level)
        
        # Analyze code quality
        code_analysis = self._analyze_code_quality(final_code, problem, skill_level)
        
        prompt = f"""
You are an expert educational evaluator for DSA learning. Provide a comprehensive evaluation of this learning session.

Session Details:
- Problem: {problem['title']} ({problem['difficulty']})
- Student Level: {skill_level}
- Hints Used: {hints_used}
- Conversation Quality: {conversation_analysis}
- Code Analysis: {code_analysis}

Final Code:
```python
{final_code}
```

Provide evaluation in JSON format:
{{
    "overall_performance": "Excellent|Good|Satisfactory|Needs Improvement",
    "summary": "Brief overall summary of performance",
    "detailed_analysis": "Detailed breakdown of strengths and areas for improvement",
    "thought_process_score": 1-10,
    "code_quality_score": 1-10,
    "problem_solving_approach": "Analysis of their approach",
    "learning_indicators": ["List of positive learning behaviors observed"],
    "improvement_areas": ["Specific areas to focus on"],
    "recommendations": "Specific next steps and practice suggestions",
    "skill_level_assessment": "Current skill level assessment with reasoning",
    "next_difficulty": "Recommended next problem difficulty"
}}

Consider:
1. How well did they articulate their thought process?
2. Did they show good problem-solving methodology?
3. How efficiently did they use hints?
4. Code correctness and optimization
5. Learning progression indicators
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                evaluation_data = json.loads(json_match.group())
                
                # Format the evaluation nicely
                return {
                    "summary": self._format_summary(evaluation_data),
                    "detailed_analysis": self._format_detailed_analysis(evaluation_data),
                    "recommendations": self._format_recommendations(evaluation_data, skill_level),
                    "raw_data": evaluation_data
                }
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"[Evaluation Agent Error] {e}")
            return self._generate_fallback_evaluation(skill_level, hints_used, final_code)
    
    def _analyze_conversation(self, conversation_history: List[dict], skill_level: str) -> str:
        """Analyze the quality of mentor-student conversation"""
        
        if not conversation_history:
            return "Limited conversation data"
        
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        
        analysis_points = []
        
        # Check conversation depth
        if len(user_messages) >= 3:
            analysis_points.append("Good engagement level")
        elif len(user_messages) >= 1:
            analysis_points.append("Moderate engagement")
        else:
            analysis_points.append("Limited engagement")
        
        # Analyze message quality (basic heuristics)
        avg_message_length = sum(len(msg.get("content", "")) for msg in user_messages) / max(len(user_messages), 1)
        
        if avg_message_length > 100:
            analysis_points.append("Detailed responses")
        elif avg_message_length > 50:
            analysis_points.append("Adequate detail in responses")
        else:
            analysis_points.append("Brief responses")
        
        return "; ".join(analysis_points)
    
    def _analyze_code_quality(self, code: str, problem: dict, skill_level: str) -> str:
        """Basic code quality analysis"""
        
        if not code.strip():
            return "No code submitted"
        
        analysis_points = []
        
        # Basic metrics
        lines_of_code = len([line for line in code.split('\n') if line.strip()])
        
        if lines_of_code > 50:
            analysis_points.append("Comprehensive solution")
        elif lines_of_code > 10:
            analysis_points.append("Well-structured solution")
        else:
            analysis_points.append("Concise solution")
        
        # Check for common patterns
        if "def " in code:
            analysis_points.append("Function-based approach")
        
        if any(keyword in code.lower() for keyword in ["time", "space", "complexity"]):
            analysis_points.append("Complexity-aware")
        
        if "# " in code or '"""' in code:
            analysis_points.append("Well-commented")
        
        return "; ".join(analysis_points)
    
    def _format_summary(self, evaluation_data: dict) -> str:
        """Format the performance summary"""
        
        performance = evaluation_data.get("overall_performance", "Good")
        thought_score = evaluation_data.get("thought_process_score", 7)
        code_score = evaluation_data.get("code_quality_score", 7)
        
        summary_parts = [
            f"## 🎯 Overall Performance: {performance}",
            "",
            f"**Thought Process:** {thought_score}/10 {'🌟' * min(thought_score//2, 5)}",
            f"**Code Quality:** {code_score}/10 {'🌟' * min(code_score//2, 5)}",
            "",
            evaluation_data.get("summary", "Good work on this problem!")
        ]
        
        return "\n".join(summary_parts)
    
    def _format_detailed_analysis(self, evaluation_data: dict) -> str:
        """Format the detailed analysis"""
        
        analysis_parts = []
        
        # Problem-solving approach
        if evaluation_data.get("problem_solving_approach"):
            analysis_parts.extend([
                "### 🧠 Problem-Solving Approach",
                evaluation_data["problem_solving_approach"],
                ""
            ])
        
        # Learning indicators
        if evaluation_data.get("learning_indicators"):
            analysis_parts.extend([
                "### ✅ Positive Learning Behaviors",
                ""
            ])
            for indicator in evaluation_data["learning_indicators"]:
                analysis_parts.append(f"• {indicator}")
            analysis_parts.append("")
        
        # Areas for improvement
        if evaluation_data.get("improvement_areas"):
            analysis_parts.extend([
                "### 🎯 Areas for Growth",
                ""
            ])
            for area in evaluation_data["improvement_areas"]:
                analysis_parts.append(f"• {area}")
            analysis_parts.append("")
        
        # Skill level assessment
        if evaluation_data.get("skill_level_assessment"):
            analysis_parts.extend([
                "### 📊 Skill Level Assessment",
                evaluation_data["skill_level_assessment"],
                ""
            ])
        
        return "\n".join(analysis_parts)
    
    def _format_recommendations(self, evaluation_data: dict, skill_level: str) -> str:
        """Format recommendations and next steps"""
        
        rec_parts = []
        
        # Next difficulty recommendation
        next_diff = evaluation_data.get("next_difficulty", "Same level")
        rec_parts.extend([
            f"### 🚀 Next Steps",
            f"**Recommended Next Difficulty:** {next_diff}",
            ""
        ])
        
        # Specific recommendations
        if evaluation_data.get("recommendations"):
            rec_parts.extend([
                "### 💡 Specific Recommendations",
                evaluation_data["recommendations"],
                ""
            ])
        
        # Practice suggestions based on skill level
        practice_suggestions = self._get_practice_suggestions(skill_level, evaluation_data)
        if practice_suggestions:
            rec_parts.extend([
                "### 📚 Practice Suggestions",
                ""
            ])
            for suggestion in practice_suggestions:
                rec_parts.append(f"• {suggestion}")
        
        return "\n".join(rec_parts)
    
    def _get_practice_suggestions(self, skill_level: str, evaluation_data: dict) -> List[str]:
        """Generate practice suggestions based on performance"""
        
        suggestions = []
        
        # Based on skill level
        if skill_level == "Beginner":
            suggestions.extend([
                "Practice more array and string manipulation problems",
                "Focus on understanding time complexity basics",
                "Work through problems step-by-step with pen and paper first"
            ])
        elif skill_level == "Intermediate":
            suggestions.extend([
                "Explore advanced data structures (trees, graphs)",
                "Practice dynamic programming problems",
                "Focus on optimization techniques"
            ])
        else:  # Advanced
            suggestions.extend([
                "Tackle system design problems",
                "Practice competitive programming challenges",
                "Focus on proving correctness of solutions"
            ])
        
        # Based on performance
        thought_score = evaluation_data.get("thought_process_score", 7)
        code_score = evaluation_data.get("code_quality_score", 7)
        
        if thought_score < 6:
            suggestions.append("Practice explaining your approach before coding")
        
        if code_score < 6:
            suggestions.append("Focus on writing cleaner, more readable code")
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _generate_fallback_evaluation(self, skill_level: str, hints_used: int, final_code: str) -> Dict[str, str]:
        """Generate a basic evaluation when AI analysis fails"""
        
        performance_level = "Good"
        if hints_used <= 1:
            performance_level = "Excellent"
        elif hints_used >= 4:
            performance_level = "Needs Improvement"
        
        return {
            "summary": f"""
## 🎯 Overall Performance: {performance_level}

**Thought Process:** 7/10 🌟🌟🌟
**Code Quality:** 7/10 🌟🌟🌟

You've made good progress on this problem! Your approach shows understanding of the core concepts.
""",
            "detailed_analysis": f"""
### 🧠 Problem-Solving Approach
You demonstrated a {skill_level.lower()}-level approach to this problem. 

### ✅ Positive Learning Behaviors
• Engaged with the mentor system
• {"Used hints efficiently" if hints_used <= 2 else "Sought help when needed"}
• Completed the coding phase

### 🎯 Areas for Growth
• Continue practicing similar problems
• Focus on explaining your approach clearly
""",
            "recommendations": f"""
### 🚀 Next Steps
**Recommended Next Difficulty:** {"Same level" if hints_used > 2 else "Slightly harder"}

### 💡 Specific Recommendations
Continue practicing problems at your level to build confidence and pattern recognition.

### 📚 Practice Suggestions
• Work on similar problem types
• Practice explaining solutions out loud
• Focus on time complexity analysis
""",
            "raw_data": {
                "overall_performance": performance_level,
                "thought_process_score": 7,
                "code_quality_score": 7
            }
        }
    
    def generate_progress_report(self, session_history: List[dict]) -> str:
        """Generate a progress report across multiple problems"""
        
        if not session_history:
            return "No session history available."
        
        prompt = f"""
Analyze this student's progress across multiple DSA problems and generate a learning progress report.

Session History:
{json.dumps(session_history, indent=2)}

Focus on:
1. Skill progression over time
2. Consistent strengths and weaknesses
3. Learning velocity
4. Recommended learning path

Provide an encouraging but honest assessment of their progress.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Progress analysis temporarily unavailable. Based on your recent sessions, you're making steady progress!"