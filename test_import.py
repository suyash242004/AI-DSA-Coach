# from utils.gemini_client import get_gemini_model

# model = get_gemini_model()
# print(model)

# from agents.evaluation_agent import generate_evaluation

# summary = generate_evaluation(2, "Intermediate", "✅ Code is efficient and correct.")
# print(summary)


# print("✅ evaluation_agent loaded")
# def generate_evaluation(hints_used: int, skill_level: str, code_quality: str) -> str:
#     return f"""
#     🔍 Session Summary:
#     - Hints Used: {hints_used}
#     - Final Code Review: {code_quality}
#     - Estimated Skill Level: {skill_level}

#     ✅ Keep practicing to move to the next level!
#     """

# import agents.evaluation_agent as eval_agent

# print(dir(eval_agent))

# from agents.evaluation_agent import generate_evaluation

# print(generate_evaluation(1, "Intermediate", "✅ Good"))

# from agents.persona_agent import get_user_profile

# print(get_user_profile())

from agents.orchestrator import AgentOrchestrator

agent = AgentOrchestrator()
print(agent.get_state())




