
from utils.gemini_client import get_gemini_model
import json
import re
from typing import Dict, List, Any, Tuple

class EvaluationAgent:
    def __init__(self):
        self.model = get_gemini_model()
    
    def generate_evaluation(self, skill_level: str, hints_used: int, final_code: str, 
                          problem: dict, conversation_history: List[dict]) -> Dict[str, str]:
        """
        Generate technical evaluation focused on DSA skills and code quality
        """
        
        # Quick technical analysis
        code_metrics = self._analyze_code_technical(final_code, problem)
        complexity_analysis = self._analyze_complexity(final_code, problem)
        approach_quality = self._evaluate_approach_quality(conversation_history, skill_level)
        
        prompt = f"""
You are a technical DSA interview evaluator. Provide a CONCISE, TECHNICAL evaluation.

Problem: {problem['title']} ({problem['difficulty']})
Skill Level: {skill_level}
Hints Used: {hints_used}
Code Analysis: {code_metrics}
Complexity: {complexity_analysis}

Final Code:
```python
{final_code}
```

Provide evaluation in JSON format:
{{
    "technical_score": 1-10,
    "approach_score": 1-10,
    "time_complexity": "O(...)",
    "space_complexity": "O(...)",
    "is_optimal": true/false,
    "correctness": "Correct|Mostly Correct|Incorrect",
    "key_strengths": ["max 2 technical strengths"],
    "main_weakness": "single biggest technical issue",
    "optimization_tip": "one specific improvement",
    "next_focus": "specific skill to practice next"
}}

Be direct, technical, and focus on DSA fundamentals. No fluff.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                evaluation_data = json.loads(json_match.group())
                
                return {
                    "summary": self._format_technical_summary(evaluation_data, hints_used),
                    "complexity_analysis": self._format_complexity_analysis(evaluation_data, complexity_analysis),
                    "actionable_feedback": self._format_actionable_feedback(evaluation_data, skill_level),
                    "raw_data": evaluation_data
                }
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"[Evaluation Agent Error] {e}")
            return self._generate_technical_fallback(skill_level, hints_used, final_code, problem)
    
    def _analyze_code_technical(self, code: str, problem: dict) -> str:
        """Quick technical code analysis"""
        if not code.strip():
            return "No solution submitted"
        
        metrics = []
        
        # Check for common DSA patterns
        patterns = {
            "two_pointer": ["left", "right", "start", "end"],
            "sliding_window": ["window", "left", "right"],
            "hashmap": ["dict", "{}", "Counter", "defaultdict"],
            "sorting": ["sort", "sorted"],
            "recursion": ["def.*\\(.*\\).*:", "return.*\\("],
            "dp": ["dp", "memo", "cache"],
            "binary_search": ["mid", "left.*right", "binary"]
        }
        
        code_lower = code.lower()
        detected_patterns = []
        for pattern, keywords in patterns.items():
            if any(keyword in code_lower for keyword in keywords):
                detected_patterns.append(pattern)
        
        if detected_patterns:
            metrics.append(f"Patterns: {', '.join(detected_patterns)}")
        
        # Code structure analysis
        lines = len([l for l in code.split('\n') if l.strip()])
        if lines > 20:
            metrics.append("Complex solution")
        elif lines > 10:
            metrics.append("Standard solution")
        else:
            metrics.append("Concise solution")
        
        return "; ".join(metrics) if metrics else "Basic implementation"
    
    def _analyze_complexity(self, code: str, problem: dict) -> str:
        """Analyze time/space complexity heuristically"""
        if not code.strip():
            return "No complexity analysis possible"
        
        complexity_indicators = []
        
        # Time complexity indicators
        nested_loops = code.count('for') + code.count('while')
        if nested_loops >= 2:
            complexity_indicators.append("Likely O(n²) time")
        elif nested_loops >= 1:
            complexity_indicators.append("Likely O(n) time")
        
        # Space complexity indicators
        if any(keyword in code.lower() for keyword in ['dict', 'set', 'list', 'array']):
            complexity_indicators.append("O(n) space")
        else:
            complexity_indicators.append("O(1) space")
        
        return "; ".join(complexity_indicators)
    
    def _evaluate_approach_quality(self, conversation_history: List[dict], skill_level: str) -> int:
        """Evaluate approach discussion quality (1-10)"""
        if not conversation_history:
            return 5
        
        user_messages = [msg.get("content", "") for msg in conversation_history if msg.get("role") == "user"]
        
        # Check for technical keywords in user responses
        technical_keywords = [
            "complexity", "algorithm", "data structure", "optimize", 
            "efficient", "brute force", "pattern", "approach"
        ]
        
        technical_score = 0
        for msg in user_messages:
            msg_lower = msg.lower()
            technical_score += sum(1 for keyword in technical_keywords if keyword in msg_lower)
        
        # Normalize to 1-10 scale
        return min(10, max(1, technical_score + 5))
    
    def _format_technical_summary(self, eval_data: dict, hints_used: int) -> str:
        """Format concise technical summary"""
        technical_score = eval_data.get("technical_score", 7)
        approach_score = eval_data.get("approach_score", 7)
        correctness = eval_data.get("correctness", "Mostly Correct")
        
        # Performance rating
        avg_score = (technical_score + approach_score) / 2
        if avg_score >= 8:
            rating = "🟢 Strong"
        elif avg_score >= 6:
            rating = "🟡 Good"
        else:
            rating = "🔴 Needs Work"
        
        return f"""## {rating} Performance

**Technical Implementation:** {technical_score}/10  
**Problem Solving:** {approach_score}/10  
**Solution Status:** {correctness}  
**Hints Used:** {hints_used}"""
    
    def _format_complexity_analysis(self, eval_data: dict, complexity_analysis: str) -> str:
        """Format complexity analysis"""
        time_complexity = eval_data.get("time_complexity", "Not analyzed")
        space_complexity = eval_data.get("space_complexity", "Not analyzed")
        is_optimal = eval_data.get("is_optimal", False)
        
        optimal_status = "✅ Optimal" if is_optimal else "⚠️ Can be optimized"
        
        return f"""### ⚡ Complexity Analysis

**Time Complexity:** {time_complexity}  
**Space Complexity:** {space_complexity}  
**Optimization Status:** {optimal_status}

*Analysis: {complexity_analysis}*"""
    
    def _format_actionable_feedback(self, eval_data: dict, skill_level: str) -> str:
        """Format actionable, specific feedback"""
        strengths = eval_data.get("key_strengths", [])
        weakness = eval_data.get("main_weakness", "Continue practicing")
        optimization_tip = eval_data.get("optimization_tip", "Focus on edge cases")
        next_focus = eval_data.get("next_focus", "Practice more problems")
        
        feedback_parts = []
        
        # Strengths (max 2, keep it short)
        if strengths:
            feedback_parts.extend([
                "### ✅ Key Strengths",
                ""
            ])
            for strength in strengths[:2]:
                feedback_parts.append(f"• {strength}")
            feedback_parts.append("")
        
        # Main area to improve
        feedback_parts.extend([
            "### 🎯 Main Area to Improve",
            f"**{weakness}**",
            "",
            "### 💡 Quick Optimization Tip",
            optimization_tip,
            "",
            "### 📚 Next Focus",
            f"Practice: {next_focus}"
        ])
        
        return "\n".join(feedback_parts)
    
    def _generate_technical_fallback(self, skill_level: str, hints_used: int, 
                                   final_code: str, problem: dict) -> Dict[str, str]:
        """Generate fallback technical evaluation"""
        
        # Basic scoring based on hints and code presence
        if not final_code.strip():
            tech_score = 2
            correctness = "Incomplete"
        elif hints_used <= 1:
            tech_score = 8
            correctness = "Likely Correct"
        elif hints_used <= 3:
            tech_score = 6
            correctness = "Mostly Correct"
        else:
            tech_score = 4
            correctness = "Needs Review"
        
        # Estimate complexity based on code patterns
        time_complexity = "O(n)" if "for" in final_code else "O(1)"
        space_complexity = "O(n)" if any(ds in final_code for ds in ["list", "dict", "set"]) else "O(1)"
        
        return {
            "summary": f"""## {'🟢 Good' if tech_score >= 6 else '⚠️ Fair'} Performance

**Technical Implementation:** {tech_score}/10  
**Problem Solving:** {tech_score}/10  
**Solution Status:** {correctness}  
**Hints Used:** {hints_used}""",
            
            "complexity_analysis": f"""### ⚡ Complexity Analysis

**Time Complexity:** {time_complexity}  
**Space Complexity:** {space_complexity}  
**Optimization Status:** {'✅ Good approach' if hints_used <= 2 else '⚠️ Can optimize'}""",
            
            "actionable_feedback": f"""### ✅ Key Strengths
• Completed the problem
• {'Efficient hint usage' if hints_used <= 2 else 'Engaged with mentor system'}

### 🎯 Main Area to Improve
**Focus on {skill_level.lower()}-level optimization patterns**

### 💡 Quick Optimization Tip
Review time complexity and consider more efficient data structures

### 📚 Next Focus
Practice: Similar {problem.get('difficulty', 'medium')} level problems""",
            
            "raw_data": {
                "technical_score": tech_score,
                "approach_score": tech_score,
                "time_complexity": time_complexity,
                "space_complexity": space_complexity,
                "correctness": correctness
            }
        }