from utils.gemini_client import get_gemini_model
import json
import re

class MentorAgent:
    def __init__(self):
        self.model = get_gemini_model()
        self.conversation_history = []
    
    def analyze_approach(self, user_input: str, problem: dict, current_skill_level: str = None) -> dict:
        """
        Analyzes user's approach and determines if they're ready to code
        Returns: {
            "message": str,
            "skill_level": str,
            "approved": bool,
            "hint": str (optional)
        }
        """
        
        prompt = f"""
You are an expert DSA mentor helping a student solve coding problems. Your role is to:
1. Assess their problem-solving approach
2. Determine their skill level if not already known
3. Decide if their approach is solid enough to proceed to coding
4. Provide encouraging, level-appropriate feedback

Problem: {problem['title']} ({problem['difficulty']})
Description: {problem['description']}

Current skill level: {current_skill_level or "Unknown"}

Student's approach description:
\"{user_input}\"

Based on their approach, respond in JSON format:
{{
    "skill_level": "Beginner|Intermediate|Advanced",
    "approved": true/false,
    "message": "Your encouraging response with feedback",
    "reasoning": "Why you made this decision",
    "hint": "Optional hint if they need guidance"
}}

Skill level guidelines:
- Beginner: Basic understanding, mentions brute force, may miss edge cases
- Intermediate: Knows data structures, mentions time complexity, some optimization ideas
- Advanced: Identifies optimal patterns, considers space-time tradeoffs, edge cases

Approval guidelines:
- Approve if they show understanding of a viable approach (even if not optimal)
- Don't approve if approach is fundamentally wrong or too vague
- Always be encouraging regardless of approval status
"""


        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_response = json.loads(json_match.group())
                
                # Personalize message based on skill level
                personalized_message = self._personalize_message(
                    json_response["message"], 
                    json_response["skill_level"]
                )
                json_response["message"] = personalized_message
                
                return json_response
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"[Mentor Agent Error] {e}")
            return {
                "skill_level": current_skill_level or "Intermediate",
                "approved": False,
                "message": "I need a bit more detail about your approach. Can you explain your thinking step by step?",
                "reasoning": "Error in processing",
                "hint": "Try breaking down the problem into smaller parts."
            }
    
    def give_hint(self, skill_level: str, problem: dict) -> str:
        """Provides skill-appropriate hints"""
        
        hint_prompts = {
            "Beginner": f"""
            Give a beginner-friendly hint for this problem: {problem['title']}
            Description: {problem['description']}
            
            Focus on:
            - Basic approach or pattern
            - What data structure might help
            - Simple step-by-step guidance
            Keep it encouraging and not too revealing.
            """,
            
            "Intermediate": f"""
            Give an intermediate-level hint for: {problem['title']}
            Description: {problem['description']}
            
            Focus on:
            - Optimization opportunities
            - Time/space complexity considerations
            - Alternative approaches
            """,
            
            "Advanced": f"""
            Give an advanced hint for: {problem['title']}
            Description: {problem['description']}
            
            Focus on:
            - Edge cases to consider
            - Proof of correctness
            - Most optimal solution insights
            """
        }
        
        prompt = hint_prompts.get(skill_level, hint_prompts["Intermediate"])
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            fallback_hints = {
                "Beginner": "Think about what data structure could help you look up values quickly. 🤔",
                "Intermediate": "Consider the time complexity - can you reduce it using additional space?",
                "Advanced": "What edge cases might break your current approach? How would you handle them?"
            }
            return fallback_hints.get(skill_level, "Keep thinking - you're on the right track!")
    
    def _personalize_message(self, message: str, skill_level: str) -> str:
        """Add personality based on skill level"""
        
        personality_prefixes = {
            "Beginner": "🌟 Great start! ",
            "Intermediate": "👍 Nice thinking! ",
            "Advanced": "💡 Excellent analysis! "
        }
        
        personality_suffixes = {
            "Beginner": " Remember, every expert was once a beginner! 🚀",
            "Intermediate": " You're developing strong problem-solving skills! 💪",
            "Advanced": " Your systematic approach is impressive! 🎯"
        }
        
        prefix = personality_prefixes.get(skill_level, "")
        suffix = personality_suffixes.get(skill_level, "")
        
        return f"{prefix}{message}{suffix}"
    
    def get_encouragement(self, skill_level: str, hints_used: int) -> str:
        """Provides encouragement based on performance"""
        
        if hints_used == 0:
            messages = {
                "Beginner": "Wow! You figured that out on your own! 🌟",
                "Intermediate": "Excellent independent thinking! 🎯",
                "Advanced": "Outstanding problem-solving skills! 🏆"
            }
        elif hints_used <= 2:
            messages = {
                "Beginner": "Great job using hints effectively! 👍",
                "Intermediate": "Good balance of independent work and guidance! 💪",
                "Advanced": "Smart use of hints to validate your thinking! 🧠"
            }
        else:
            messages = {
                "Beginner": "Don't worry - learning takes practice! Keep going! 🚀",
                "Intermediate": "Challenging problems require patience. You're learning! 📚",
                "Advanced": "Even experts need different perspectives sometimes! 🤝"
            }
        
        return messages.get(skill_level, "Keep up the great work!")
    
    
    
