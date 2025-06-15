from utils.gemini_client import get_gemini_model
import re
import json
import ast

class CodeAgent:
    def __init__(self):
        self.model = get_gemini_model()
    
    def evaluate_code(self, user_code: str, problem: dict, skill_level: str) -> dict:
        """
        Comprehensive code evaluation
        Returns: {
            "passed": bool,
            "feedback": str,
            "bugs": list,
            "optimizations": list,
            "complexity": dict
        }
        """
        
        # First, check if code is syntactically valid
        syntax_check = self._check_syntax(user_code)
        if not syntax_check["valid"]:
            return {
                "passed": False,
                "feedback": f"❌ **Syntax Error:** {syntax_check['error']}\n\nPlease fix the syntax and try again.",
                "bugs": [syntax_check['error']],
                "optimizations": [],
                "complexity": {}
            }
        
        prompt = f"""
You are an expert code reviewer for DSA problems. Analyze this solution thoroughly.

Problem: {problem['title']} ({problem['difficulty']})
Description: {problem['description']}
Student Level: {skill_level}

Code to analyze:
```python
{user_code}
```

Provide analysis in JSON format:
{{
    "passed": true/false,
    "overall_rating": "Excellent|Good|Needs Improvement|Poor",
    "correctness": "Analysis of logical correctness",
    "time_complexity": "Big O time complexity",
    "space_complexity": "Big O space complexity",
    "bugs": ["List of bugs/issues found"],
    "optimizations": ["List of possible optimizations"],
    "edge_cases": ["Edge cases that might not be handled"],
    "feedback": "Detailed friendly feedback with specific examples",
    "next_steps": "What the student should focus on improving"
}}

Testing criteria:
1. Does it solve the basic problem correctly?
2. Does it handle edge cases appropriately?
3. Is the complexity reasonable for the problem?
4. Are there obvious bugs or logical errors?
5. Code quality and readability

Be encouraging but thorough. Give specific examples of issues found.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Format the feedback nicely
                formatted_feedback = self._format_feedback(result, skill_level)
                result["feedback"] = formatted_feedback
                
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"[Code Agent Error] {e}")
            return {
                "passed": False,
                "feedback": "⚠️ Unable to evaluate code at the moment. Please check your solution manually.",
                "bugs": ["Evaluation service unavailable"],
                "optimizations": [],
                "complexity": {}
            }
    
    def chat_assistance(self, user_question: str, user_code: str, problem: dict, skill_level: str) -> str:
        """Real-time coding assistance"""
        
        prompt = f"""
You are a helpful DSA coding assistant. A {skill_level} level student is working on this problem:

Problem: {problem['title']}
Description: {problem['description']}

Their current code:
```python
{user_code}
```

Student's question: "{user_question}"

Provide helpful, specific guidance. If they're asking about:
- Bugs: Point out specific lines and suggest fixes
- Optimization: Suggest specific improvements with examples
- Logic: Help them understand the algorithmic approach
- Testing: Suggest test cases or debugging strategies

Keep your response concise but helpful. Use code examples when appropriate.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Code Chat Error] {e}")
            return "❌ I'm having trouble processing your question right now. Please try rephrasing or ask again in a moment."
    
    def suggest_test_cases(self, problem: dict, user_code: str) -> list:
        """Generate test cases for the problem"""
        
        prompt = f"""
Generate comprehensive test cases for this DSA problem:

Problem: {problem['title']}
Description: {problem['description']}

Include:
1. Basic test cases (given examples)
2. Edge cases (empty input, single element, etc.)
3. Corner cases (maximum constraints, negative numbers, etc.)

Format as a list of dictionaries with 'input' and 'expected_output' keys.
Respond in JSON format: {{"test_cases": [...]}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("test_cases", [])
            return []
        except Exception as e:
            print(f"[Test Case Generation Error] {e}")
            return []
    
    def _check_syntax(self, code: str) -> dict:
        """Check if Python code has valid syntax"""
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Line {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Code parsing error: {str(e)}"
            }
    
    def _format_feedback(self, result: dict, skill_level: str) -> str:
        """Format the evaluation feedback nicely"""
        
        feedback = []
        
        # Overall assessment
        if result.get("passed"):
            feedback.append("✅ **Great job!** Your solution looks good overall.")
        else:
            feedback.append("⚠️ **Almost there!** Let's address a few issues.")
        
        # Correctness
        if result.get("correctness"):
            feedback.append(f"**Logic:** {result['correctness']}")
        
        # Complexity analysis (adjust detail based on skill level)
        if skill_level != "Beginner":
            time_comp = result.get("time_complexity", "Not analyzed")
            space_comp = result.get("space_complexity", "Not analyzed")
            feedback.append(f"**Complexity:** Time: {time_comp}, Space: {space_comp}")
        
        # Bugs
        if result.get("bugs"):
            feedback.append("**🐛 Issues Found:**")
            for bug in result["bugs"]:
                feedback.append(f"  • {bug}")
        
        # Optimizations (show more for intermediate/advanced)
        if result.get("optimizations") and skill_level != "Beginner":
            feedback.append("**🚀 Optimization Ideas:**")
            for opt in result["optimizations"]:
                feedback.append(f"  • {opt}")
        
        # Edge cases
        if result.get("edge_cases") and skill_level == "Advanced":
            feedback.append("**⚠️ Edge Cases to Consider:**")
            for edge in result["edge_cases"]:
                feedback.append(f"  • {edge}")
        
        # Next steps
        if result.get("next_steps"):
            feedback.append(f"**🎯 Focus Areas:** {result['next_steps']}")
        
        return "\n\n".join(feedback)
    
    def debug_assistance(self, user_code: str, error_message: str, skill_level: str) -> str:
        """Help debug specific errors"""
        
        prompt = f"""
A {skill_level} level student has encountered this error:

Error: {error_message}

In this code:
```python
{user_code}
```

Provide specific debugging help:
1. Identify the likely cause
2. Suggest specific fixes
3. Explain why this error occurred (in simple terms for beginners, more technical for advanced)

Be encouraging and provide concrete solutions.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Having trouble analyzing the error. Common issues to check: syntax errors, variable names, indentation, and logic flow."