import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_model():
    return genai.GenerativeModel("models/gemini-1.5-flash")

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