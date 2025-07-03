
from utils.gemini_client import get_gemini_model
import json
import re

class MentorAgent:
    def __init__(self):
        self.model = get_gemini_model()
        self.conversation_history = []
        self.hints_given = 0
        self.approach_attempts = 0
    
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
        
        self.approach_attempts += 1
        
        prompt = f"""
You are an expert DSA mentor helping a student solve coding problems. Your role is to:
1. Assess their problem-solving approach thoroughly
2. Determine their skill level if not already known
3. Decide if their approach is COMPLETE and DETAILED enough to proceed to coding
4. Provide encouraging, level-appropriate feedback

Problem: {problem['title']} ({problem['difficulty']})
Description: {problem['description']}

Current skill level: {current_skill_level or "Unknown"}
Attempt number: {self.approach_attempts}

Student's approach description:
\"{user_input}\"

STRICT APPROVAL CRITERIA:
- For Beginner: Must explain the COMPLETE step-by-step logic, not just mention data structures
- For Intermediate: Must include algorithm steps, time complexity awareness, and edge case consideration
- For Advanced: Must provide detailed algorithm, complexity analysis, and edge case handling



AUTOMATIC REJECTION EXAMPLES (VAGUE APPROACHES):
❌ "Use loops" → Missing: what type of loops? what do they iterate over? what logic inside?
❌ "Use recursion" → Missing: base case? recursive call? what parameters?
❌ "Use stack/queue" → Missing: what gets pushed/popped? when? what's the algorithm?
❌ "Use dynamic programming" → Missing: what's the DP state? transition? base cases?
❌ "Use BFS/DFS" → Missing: what's the graph structure? what are we searching for?
❌ "Sort the array" → Missing: what happens after sorting? complete algorithm?
❌ "Use two pointers" → Missing: where do pointers start? how do they move? what condition?
❌ "Use sliding window" → Missing: window size? what's in window? when to expand/contract?

APPROVAL EXAMPLES (COMPLETE APPROACHES):
✅ Arrays: "Use two nested loops: outer from 0 to n-2, inner from i+1 to n-1, check condition X, return Y when found"
✅ Trees: "Use DFS recursion: base case is null node, for each node process value, recursively call left and right subtrees, return combined result"
✅ Graphs: "Use BFS with queue: start from source, add neighbors to queue, track visited nodes, continue until queue empty or target found"
✅ DP: "Use 2D DP table: dp[i][j] represents X, base case dp[0][0] = Y, transition dp[i][j] = dp[i-1][j] + dp[i][j-1], return dp[n][m]"

DO NOT APPROVE if the approach is:
- Too vague (e.g., "use for loops", "use hash map" without explaining HOW)
- Missing key steps in the algorithm
- Doesn't address how to find the solution
- Lacks logical flow

EXAMPLES OF INSUFFICIENT APPROACHES:
- "use for loops" (too vague)
- "use hash map" (doesn't explain the algorithm)
- "check all pairs" (doesn't explain how to check or return)

EXAMPLES OF SUFFICIENT APPROACHES:
- "Use two nested loops: outer loop from 0 to n-1, inner loop from i+1 to n-1, check if arr[i] + arr[j] equals target, return their indices"
- "Use hash map: iterate through array, for each element check if (target - element) exists in hash map, if yes return indices, if no store element and index in hash map"

Based on their approach, respond in JSON format:
{{
    "skill_level": "Beginner|Intermediate|Advanced",
    "approved": true/false,
    "message": "Your encouraging response with feedback",
    "reasoning": "Why you made this decision",
    "hint": "Optional hint if they need guidance",
    "completeness_score": 0-100
}}

Skill level guidelines:
- Beginner: Basic understanding, mentions brute force, may miss edge cases
- Intermediate: Knows data structures, mentions time complexity, some optimization ideas
- Advanced: Identifies optimal patterns, considers space-time tradeoffs, edge cases

Be encouraging but maintain high standards for approval.

OUTPUT guidelines:
1. Simple and Easy to Understand.
2. Dont generate to much large Output (mostly try to generate 2-4 lines).
3. Whenever needed try to explain with examples.
"""

# REQUIRED FOR APPROVAL - ALL MUST BE PRESENT:
# 1. ALGORITHM STEPS: Must explain the step-by-step process from start to finish
# 2. DATA STRUCTURES: Must explain what data structures are used and why
# 3. CONTROL FLOW: Must explain loops, conditions, recursion details (ranges, base cases, etc.)
# 4. LOGIC/OPERATIONS: Must explain what calculations, comparisons, or operations are performed
# 5. OUTPUT/RETURN: Must explain what is returned/output and under what conditions

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_response = json.loads(json_match.group())
                
                # Add additional validation
                if json_response.get("completeness_score", 0) < 70:
                    json_response["approved"] = False
                
                # Personalize message based on skill level
                personalized_message = self._personalize_message(
                    json_response["message"], 
                    json_response["skill_level"],
                    json_response["approved"]
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
                "hint": "Try breaking down the problem into smaller parts.",
                "completeness_score": 0
            }
    
    def give_hint(self, skill_level: str, problem: dict) -> str:
        """Provides skill-appropriate hints"""
        
        self.hints_given += 1
        
        hint_prompts = {
            "Beginner": f"""
            Give a beginner-friendly hint for this problem: {problem['title']}
            Description: {problem['description']}
            
            This is hint #{self.hints_given}. Focus on:
            - Basic approach or pattern
            - What data structure might help
            - Simple step-by-step guidance
            
            Make it progressively more helpful if this is a later hint.
            Keep it encouraging and not too revealing.
            """,
            
            "Intermediate": f"""
            Give an intermediate-level hint for: {problem['title']}
            Description: {problem['description']}
            
            This is hint #{self.hints_given}. Focus on:
            - Optimization opportunities
            - Time/space complexity considerations
            - Alternative approaches
            
            Make it progressively more detailed if this is a later hint.
            """,
            
            "Advanced": f"""
            Give an advanced hint for: {problem['title']}
            Description: {problem['description']}
            
            This is hint #{self.hints_given}. Focus on:
            - Edge cases to consider
            - Proof of correctness
            - Most optimal solution insights
            
            Make it progressively more specific if this is a later hint.
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
    
    def provide_guided_questions(self, skill_level: str, problem: dict) -> str:
        """Provides guided questions to help user think through the approach"""
        
        questions = {
            "Beginner": [
                "What do we need to find in this problem?",
                "How could we check if two numbers add up to the target?",
                "What's the most straightforward way to try all possible pairs?",
                "What information do we need to return?"
            ],
            "Intermediate": [
                "What's the brute force approach and its time complexity?",
                "How can we optimize this using additional space?",
                "What data structure would help us find complements quickly?",
                "How do we handle edge cases like duplicate values?"
            ],
            "Advanced": [
                "What are the space-time tradeoffs for different approaches?",
                "How do we prove the correctness of our solution?",
                "What are the edge cases and how do we handle them?",
                "Can we solve this with constant space?"
            ]
        }
        
        question_list = questions.get(skill_level, questions["Intermediate"])
        return "Let me guide you with some questions:\n" + "\n".join(f"• {q}" for q in question_list)
    
    def _personalize_message(self, message: str, skill_level: str, approved: bool) -> str:
        """Add personality based on skill level and approval status"""
        
        if approved:
            personality_prefixes = {
                "Beginner": "🌟 Excellent! ",
                "Intermediate": "👍 Great work! ",
                "Advanced": "💡 Outstanding! "
            }
            
            personality_suffixes = {
                "Beginner": " You've thought through this well! Let's code it up! 🚀",
                "Intermediate": " Your approach is solid! Time to implement! 💪",
                "Advanced": " Your systematic approach is impressive! Let's see the implementation! 🎯"
            }
        else:
            personality_prefixes = {
                "Beginner": "🤔 Good thinking, but ",
                "Intermediate": "👀 You're on the right track, but ",
                "Advanced": "🧠 Interesting approach, but "
            }
            
            personality_suffixes = {
                "Beginner": " Can you explain the step-by-step process? 🔍",
                "Intermediate": " Let's add more detail to your algorithm! 📝",
                "Advanced": " I need more specifics about your implementation! ⚡"
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
    
    def reset_session(self):
        """Reset session counters for a new problem"""
        self.hints_given = 0
        self.approach_attempts = 0
        self.conversation_history = []
    
    def get_follow_up_questions(self, user_input: str, problem: dict) -> str:
        """Generate follow-up questions based on incomplete user input"""
        
        prompt = f"""
The user gave this incomplete approach for the problem: "{user_input}"

Problem: {problem['title']}
Description: {problem['description']}

Generate 2-3 specific follow-up questions that would help them elaborate their approach into a complete algorithm. Focus on the missing pieces.

Example:
If they said "use for loops", ask:
- "How many loops would you use and what would each loop do?"
- "What condition would you check inside the loops?"
- "What would you return when you find the answer?"

Make the questions encouraging and specific to their current level of understanding.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "Can you explain your approach step by step? What exactly would your algorithm do?"






