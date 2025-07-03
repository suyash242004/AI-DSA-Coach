### 🧠 AI DSA Coach – Espyr Hackathon Submission

A smart, multi-agent web application to guide users in solving Data Structures and Algorithms (DSA) problems — like LeetCode, but with an AI mentor. 🚀

## 🚀 Features

- **Mentor Agent** 🗣️

  - Asks for the user’s approach first to foster critical thinking.
  - Provides adaptive hints tailored to the user’s skill level (Beginner, Intermediate, Advanced).
  - Motivates users and triggers the code editor when the approach is ready.

- **Code Agent** 🧪

  - Evaluates user code for correctness, edge cases, and performance.
  - Suggests optimizations and improvements.
  - Redirects users to the Mentor Agent if logical gaps are detected.

- **Evaluation Summary** 📊

  - Analyzes the clarity of the user’s thought process.
  - Tracks the number of hints used during problem-solving.
  - Rates code optimality based on efficiency and complexity.

## 📋 Overview

AI DSA Coach is an innovative platform that combines a LeetCode-like interface with a multi-agent AI system to enhance DSA skills. It dynamically adapts to Beginner, Intermediate, and Advanced users, offering personalized guidance through problem-solving, coding, and evaluation phases. 🌟

## 🛠️ Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/dsa-ai-coach.git
   cd dsa-ai-coach
   ```

2. **Install Dependencies**: Ensure Python 3.8+ is installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Gemini API**:

   - Obtain an API key from Google Cloud for Gemini.

   - Configure `utils/gemini_client.py` with your API key:

     ```python
     from google.cloud import aiplatform
     def get_gemini_model():
         return aiplatform.Model("your-model-name")
     ```

4. **Run the App**:

   ```bash
   streamlit run app.py
   ```

   Access it at `http://localhost:8501`. 🌐

## 📖 Usage

1. **Select a Problem**: Choose a DSA problem from the dropdown. 📚
2. **Discuss Approach**: Share your thought process with the Mentor Agent. 🧠
3. **Write Code**: Implement your solution in the code editor once approved. 💻
4. **Test & Optimize**: Use the Code Agent to test and improve your code. 🧪
5. **Review Evaluation**: Get detailed feedback on your performance. 📈

## 📂 File Structure

```
dsa-ai-coach/
├── app.py                    # Main Streamlit entrypoint 🖥️
├── requirements.txt          # Dependencies 🐍
├── config.py                 # Configuration settings ⚙️
├── agents/
│   ├── mentor_agent.py       # Mentor logic: classify skill, give hints 🗣️
│   ├── code_agent.py         # Code evaluator logic 🧪
│   ├── evaluation_agent.py   # Session summary 📊
│   ├── persona_agent.py      # User profile tracking 👤
│   └── orchestrator.py       # Controls agent flow/state 🎮
├── utils/
│   ├── gemini_client.py      # Gemini API configuration 🔌
│   └── data/
│       └── problems.json     # Sample DSA problems 📋
```

## 🤝 Contributing

Contributions are welcome! 🙌

1. Fork the repo. 🍴
2. Create a branch (`git checkout -b feature/your-feature`). 🌿
3. Commit changes (`git commit -m "Add feature"`). 💾
4. Push to the branch (`git push origin feature/your-feature`). 🚀
5. Open a Pull Request. 📬

Please follow PEP 8 standards and include clear comments in your code. 😊

## 📜 License

Licensed under the MIT License. See LICENSE for details. 🗳️

---

Happy coding with AI DSA Coach! 🎉💪
