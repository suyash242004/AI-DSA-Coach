# 0G Hackathon 2026 Submission - Integrated with 0G Modular Infrastructure
import os
import google.generativeai as genai

# Try to load from local config.py, otherwise fallback to Environment Variables (for Render deployment)
try:
    from config import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Set it in config.py or as an Environment Variable.")

genai.configure(api_key=GEMINI_API_KEY)

# gemini-3.1-flash-lite-preview	15 RPM

def get_gemini_model():
    return genai.GenerativeModel("models/gemini-3.1-flash-lite-preview")
# def get_gemini_model():
#     return genai.GenerativeModel("models/gemini-2.5-flash")



# import os
# import google.generativeai as genai

# def get_gemini_model():
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY environment variable not set")
#     genai.configure(api_key=api_key)
#     return genai.GenerativeModel("models/gemini-2.0-flash-lite")





# from openai import OpenAI
# from config import OPENROUTER_API_KEY, GEMINI_API_KEY
# import time

# def get_gemini_model():
#     client = OpenAI(
#         base_url="https://openrouter.ai/api/v1",
#         api_key=OPENROUTER_API_KEY
#     )
#     def generate_response(prompt):
#         for attempt in range(3):
#             try:
#                 response = client.chat.completions.create(
#                     model="google/gemini-2.5-pro-exp-03-25:free",
#                     messages=[{"role": "user", "content": prompt}],
#                     extra_headers={"X-Google-Api-Key": GEMINI_API_KEY}
#                 )
#                 return response.choices[0].message.content
#             except Exception as e:
#                 if "429" in str(e):
#                     time.sleep(60)  # Wait for rate limit reset
#                 else:
#                     raise e
#         raise Exception("Rate limit exceeded after retries")
#     return generate_response