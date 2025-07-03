
# from utils.gemini_client import get_gemini_model
# import re
# import json
# import ast

# class CodeAgent:
#     def __init__(self):
#         self.model = get_gemini_model()
    
#     def evaluate_code(self, user_code: str, problem: dict, skill_level: str) -> dict:
#         """
#         Comprehensive code evaluation
#         Returns: {
#             "passed": bool,
#             "feedback": str,
#             "bugs": list,
#             "optimizations": list,
#             "complexity": dict
#         }
#         """
        
#         # First, check if code is syntactically valid
#         syntax_check = self._check_syntax(user_code)
#         if not syntax_check["valid"]:
#             return {
#                 "passed": False,
#                 "feedback": f"❌ **Syntax Error:** {syntax_check['error']}\n\nPlease fix the syntax and try again.",
#                 "bugs": [syntax_check['error']],
#                 "optimizations": [],
#                 "complexity": {}
#             }
        
#         prompt = f"""
# You are an expert code reviewer for DSA problems. Analyze this solution thoroughly.

# Problem: {problem['title']} ({problem['difficulty']})
# Description: {problem['description']}
# Student Level: {skill_level}

# Code to analyze:
# ```python
# {user_code}
# ```

# Provide analysis in JSON format:
# {{
#     "passed": true/false,
#     "overall_rating": "Excellent|Good|Needs Improvement|Poor",
#     "correctness": "Analysis of logical correctness",
#     "time_complexity": "Big O time complexity",
#     "space_complexity": "Big O space complexity",
#     "bugs": ["List of bugs/issues found"],
#     "optimizations": ["List of possible optimizations"],
#     "edge_cases": ["Edge cases that might not be handled"],
#     "feedback": "Detailed friendly feedback with specific examples",
#     "next_steps": "What the student should focus on improving"
# }}

# Testing criteria:
# 1. Does it solve the basic problem correctly?
# 2. Does it handle edge cases appropriately?
# 3. Is the complexity reasonable for the problem?
# 4. Are there obvious bugs or logical errors?
# 5. Code quality and readability

# Be encouraging but thorough. Give specific examples of issues found.
# """
        
#         try:
#             response = self.model.generate_content(prompt)
#             response_text = response.text.strip()
            
#             # Extract JSON from response
#             json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
#             if json_match:
#                 result = json.loads(json_match.group())
                
#                 # Format the feedback nicely
#                 formatted_feedback = self._format_feedback(result, skill_level)
#                 result["feedback"] = formatted_feedback
                
#                 return result
#             else:
#                 raise ValueError("No JSON found in response")
                
#         except Exception as e:
#             print(f"[Code Agent Error] {e}")
#             return {
#                 "passed": False,
#                 "feedback": "⚠️ Unable to evaluate code at the moment. Please check your solution manually.",
#                 "bugs": ["Evaluation service unavailable"],
#                 "optimizations": [],
#                 "complexity": {}
#             }
    
#     def chat_assistance(self, user_question: str, user_code: str, problem: dict, skill_level: str) -> str:
#         """Enhanced real-time coding assistance - focuses on guidance rather than direct solutions"""
        
#         prompt = f"""
# You are a helpful DSA coding mentor for a {skill_level} level student. Your role is to GUIDE and TEACH, not to provide direct code solutions.

# Problem: {problem['title']} ({problem['description']})

# Student's current code:
# ```python
# {user_code}
# ```

# Student's question: "{user_question}"

# IMPORTANT GUIDELINES:
# 1. DO NOT write complete code solutions for the student
# 2. Instead, provide conceptual guidance, hints, and explanations
# 3. If they ask "how to implement X", explain the approach/algorithm steps
# 4. If they ask for optimization, guide them to think about different approaches
# 5. If they have bugs, point them to the problematic area and ask guiding questions
# 6. Use pseudocode or small code snippets (2-3 lines max) only when absolutely necessary for clarity
# 7. Encourage them to think through the problem themselves

# Your response should:
# - Ask clarifying questions to make them think
# - Provide hints and direction rather than solutions
# - Explain concepts and approaches
# - Point out what they're missing conceptually
# - Give them steps to think through, not code to copy

# Examples of good responses:
# - "Think about what data structure would help you quickly check if an element exists..."
# - "Consider the time complexity of your current approach. What happens when you have nested loops?"
# - "You're on the right track! But what happens when the array is empty? How would you handle that case?"
# - "Instead of nested loops, think about what you could store in a hash map to solve this in one pass..."

# Keep responses concise but educational. Focus on building their problem-solving skills.
# """
        
#         try:
#             response = self.model.generate_content(prompt)
#             return response.text.strip()
#         except Exception as e:
#             print(f"[Code Chat Error] {e}")
#             return "❌ I'm having trouble processing your question right now. Please try rephrasing or ask again in a moment."
    
#     def suggest_test_cases(self, problem: dict, user_code: str) -> list:
#         """Generate test cases for the problem"""
        
#         prompt = f"""
# Generate comprehensive test cases for this DSA problem:

# Problem: {problem['title']}
# Description: {problem['description']}

# Include:
# 1. Basic test cases (given examples)
# 2. Edge cases (empty input, single element, etc.)
# 3. Corner cases (maximum constraints, negative numbers, etc.)

# Format as a list of dictionaries with 'input' and 'expected_output' keys.
# Respond in JSON format: {{"test_cases": [...]}}
# """
        
#         try:
#             response = self.model.generate_content(prompt)
#             response_text = response.text.strip()
            
#             json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
#             if json_match:
#                 result = json.loads(json_match.group())
#                 return result.get("test_cases", [])
#             return []
#         except Exception as e:
#             print(f"[Test Case Generation Error] {e}")
#             return []
    
#     def _check_syntax(self, code: str) -> dict:
#         """Check if Python code has valid syntax"""
#         try:
#             ast.parse(code)
#             return {"valid": True, "error": None}
#         except SyntaxError as e:
#             return {
#                 "valid": False,
#                 "error": f"Line {e.lineno}: {e.msg}"
#             }
#         except Exception as e:
#             return {
#                 "valid": False,
#                 "error": f"Code parsing error: {str(e)}"
#             }
    
#     def _format_feedback(self, result: dict, skill_level: str) -> str:
#         """Format the evaluation feedback nicely"""
        
#         feedback = []
        
#         # Overall assessment
#         if result.get("passed"):
#             feedback.append("✅ **Great job!** Your solution looks good overall.")
#         else:
#             feedback.append("⚠️ **Almost there!** Let's address a few issues.")
        
#         # Correctness
#         if result.get("correctness"):
#             feedback.append(f"**Logic:** {result['correctness']}")
        
#         # Complexity analysis (adjust detail based on skill level)
#         if skill_level != "Beginner":
#             time_comp = result.get("time_complexity", "Not analyzed")
#             space_comp = result.get("space_complexity", "Not analyzed")
#             feedback.append(f"**Complexity:** Time: {time_comp}, Space: {space_comp}")
        
#         # Bugs
#         if result.get("bugs"):
#             feedback.append("**🐛 Issues Found:**")
#             for bug in result["bugs"]:
#                 feedback.append(f"  • {bug}")
        
#         # Optimizations (show more for intermediate/advanced)
#         if result.get("optimizations") and skill_level != "Beginner":
#             feedback.append("**🚀 Optimization Ideas:**")
#             for opt in result["optimizations"]:
#                 feedback.append(f"  • {opt}")
        
#         # Edge cases
#         if result.get("edge_cases") and skill_level == "Advanced":
#             feedback.append("**⚠️ Edge Cases to Consider:**")
#             for edge in result["edge_cases"]:
#                 feedback.append(f"  • {edge}")
        
#         # Next steps
#         if result.get("next_steps"):
#             feedback.append(f"**🎯 Focus Areas:** {result['next_steps']}")
        
#         return "\n\n".join(feedback)
    
#     def debug_assistance(self, user_code: str, error_message: str, skill_level: str) -> str:
#         """Help debug specific errors"""
        
#         prompt = f"""
# A {skill_level} level student has encountered this error:

# Error: {error_message}

# In this code:
# ```python
# {user_code}
# ```

# Provide specific debugging help:
# 1. Identify the likely cause
# 2. Suggest specific fixes
# 3. Explain why this error occurred (in simple terms for beginners, more technical for advanced)

# Be encouraging and provide concrete solutions.
# """
        
#         try:
#             response = self.model.generate_content(prompt)
#             return response.text.strip()
#         except Exception as e:
#             return f"Having trouble analyzing the error. Common issues to check: syntax errors, variable names, indentation, and logic flow."


from utils.gemini_client import get_gemini_model
import re
import json
import ast

class CodeAgent:
    def __init__(self):
        self.model = get_gemini_model()
    
    def evaluate_code(self, user_code: str, problem: dict, skill_level: str) -> dict:
        """
        Enhanced comprehensive code evaluation with better error detection
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
        
        # Enhanced prompt for better evaluation
        prompt = f"""
You are an expert code reviewer. Analyze this DSA solution quickly and concisely.

Problem: {problem['title']} ({problem['difficulty']})
Student Level: {skill_level}

Code:
```python
{user_code}
```

Provide CONCISE analysis in JSON format:
{{
    "passed": true/false,
    "correctness_score": 0-100,
    "logical_errors": ["ONE main logic error if exists"],
    "bugs": ["ONE main bug if exists"],
    "optimizations": ["ONE key optimization suggestion"],
    "time_complexity": "Big O only (e.g., O(n^2))",
    "next_steps": "ONE specific actionable step"
}}

Focus on:
1. Does it solve the problem correctly?
2. Most critical issue (if any)
3. One key improvement

Be brief and specific. Only include the most important points.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Enhanced feedback formatting
                formatted_feedback = self._format_enhanced_feedback(result, skill_level)
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
        """
        Enhanced chat assistance with concise, guided responses and visual examples
        """
        
        prompt = f"""
You are a DSA coding mentor for a {skill_level} level student. Provide CONCISE, GUIDED help.

Problem: {problem['title']}
Description: {problem['description']}

Student's code:
```python
{user_code}
```

Question: "{user_question}"

RESPONSE GUIDELINES:
1. Keep response under 150 words
2. NEVER provide complete code solutions
3. Use guiding questions and hints
4. When helpful, create simple ASCII diagrams using characters like |, -, +, *, #
5. Give step-by-step thinking process, not code

RESPONSE FORMAT:
- Start with a direct, short answer
- Add 1-2 guiding questions
- Include a simple ASCII diagram if it helps explain the concept
- End with a specific next step

Example ASCII diagrams you can use:
- Array: [1, 2, 3, 4, 5]
- Tree: 
    1
   / \\
  2   3
- Hash map flow:
  key -> hash() -> index
- Two pointers:
  [1, 2, 3, 4, 5]
   ^           ^
   left      right

Focus on UNDERSTANDING, not solutions. Be encouraging but brief.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Ensure response isn't too long
            if len(response_text) > 800:
                # Truncate and add guidance
                response_text = response_text[:600] + "...\n\n💡 Think through this step by step. What's your next move?"
            
            return response_text
        except Exception as e:
            print(f"[Code Chat Error] {e}")
            return "❌ I'm having trouble processing your question right now. Can you be more specific about what you're stuck on?"
    
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
        """Enhanced syntax checking"""
        try:
            # Parse the code
            ast.parse(code)
            
            # Additional checks for common issues
            if not code.strip():
                return {"valid": False, "error": "Code is empty"}
            
            # Check for basic function structure if it's a function
            if "def " in code and "return" not in code:
                return {"valid": False, "error": "Function missing return statement"}
            
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
    
    def _format_enhanced_feedback(self, result: dict, skill_level: str) -> str:
        """Concise feedback formatting - easy to read"""
        
        feedback = []
        
        # Overall assessment
        correctness_score = result.get("correctness_score", 0)
        if result.get("passed"):
            feedback.append("✅ **Great job!** Your solution works correctly.")
        else:
            feedback.append(f"⚠️ **Almost there!** Score: {correctness_score}/100")
        
        # Main issue (pick the most critical one)
        main_issues = []
        if result.get("logical_errors"):
            main_issues.extend(result["logical_errors"][:1])  # Only first error
        elif result.get("bugs"):
            main_issues.extend(result["bugs"][:1])  # Only first bug
        
        if main_issues:
            feedback.append(f"**🐛 Main Issue:** {main_issues[0]}")
        
        # Quick fix hint
        if result.get("optimizations") and skill_level != "Beginner":
            feedback.append(f"**💡 Quick Fix:** {result['optimizations'][0]}")
        
        # Complexity (simple version)
        if skill_level != "Beginner":
            time_comp = result.get("time_complexity", "").split("with")[0].strip()  # Remove explanation
            if time_comp:
                feedback.append(f"**⏱️ Complexity:** {time_comp}")
        
        # One specific next step
        if result.get("next_steps"):
            next_step = result["next_steps"]
            if isinstance(next_step, list):
                next_step = next_step[0]
            # Take first sentence only
            next_step = next_step.split('.')[0] + '.'
            feedback.append(f"**🎯 Focus on:** {next_step}")
        
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