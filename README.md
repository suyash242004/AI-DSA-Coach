<div align="center">
  <h1>🧠 AI DSA Coach</h1>
  <p><em>Your intelligent, on-chain companion for mastering Data Structures & Algorithms.</em></p>
  
  [![0G Network Integration](https://img.shields.io/badge/Network-0G_Galileo_Testnet-green?style=for-the-badge&logo=web3.js)](https://chainscan-galileo.0g.ai/)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
  [![Gemini](https://img.shields.io/badge/AI-Google_Gemini-8E75B2?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
</div>

<br/>

## 📋 Overview

**AI DSA Coach** is a next-generation learning platform that combines a LeetCode-like coding environment with a multi-agent AI mentor system. It dynamically adapts to your skill level (Beginner to Advanced), gently guides you through your thought process, evaluates your code, and rewards your learning with verifiable **on-chain tokens and NFTs**!

---

## 🌐 0G Network Integration

This project fully integrates with the **0G Galileo Testnet** to reward users with verifiable on-chain assets upon completing DSA challenges!

### 🏆 Verified Smart Contracts
- **DSA Token Contract:** [`0xb31AcDfaAac74731e655c96A90EB910dD827bFFB`](https://chainscan-galileo.0g.ai/address/0xb31AcDfaAac74731e655c96A90EB910dD827bFFB)
- **DSA Badge NFT Contract:** [`0xB253e155c3fe23772fB6254A4CAb3cF6BcA78366`](https://chainscan-galileo.0g.ai/address/0xB253e155c3fe23772fB6254A4CAb3cF6BcA78366)

### ⛓️ On-Chain Proofs
- **Demo Wallet:** [`0xFCF1cdaB5269342B0b5447E3A5b8fa56c6B7B152`](https://chainscan-galileo.0g.ai/address/0xfcf1cdab5269342b0b5447e3a5b8fa56c6b7b152)
- **NFT Minting Proof:** [View Transaction on 0G Explorer](https://chainscan-galileo.0g.ai/tx/f9717bcf59cf5a942665e2f5848ad5cefe337177ce63ec01531a7066fed68b0a)

---

## 🚀 Key Features

*   **🗣️ Mentor Agent:** Fosters critical thinking by evaluating your approach *before* you write code. Provides hints based on your skill level without giving away the answer.
*   **💻 Code Agent:** Runs and evaluates your code for correctness, edge cases, and time/space complexity optimality.
*   **📈 Evaluation Agent:** Generates a comprehensive summary of your performance, tracks hint usage, and updates your progression.
*   **💰 Web3 Rewards:** Connect your wallet to earn `$DSA` tokens for solving problems and mint unique NFT badges for your achievements!

---

## 🛠️ Quick Start

### 📦 Installation

```bash
git clone https://github.com/suyash242004/AI-DSA-Coach.git
cd AI-DSA-Coach

# Install Backend / Streamlit dependencies
pip install -r requirements.txt

# Install Frontend dependencies (Next.js)
cd frontend
npm install
```

### 🚀 Running the App (Two Options)

#### Option 1: Classic Streamlit Interface (with Web3 Integration)
This runs the original monolithic interface including the Web3 wallet connection.
```bash
cd AI-DSA-Coach
streamlit run app.py
# Or run demo.py for the full Web3 interface:
streamlit run demo.py
```
*Available at `http://localhost:8501`*

#### Option 2: Modern Next.js Interface (Recommended)
This runs the new high-performance, split-pane IDE interface. **Requires 2 Terminals.**

**Terminal 1 (Backend):**
```bash
cd AI-DSA-Coach
.\run_backend.bat
# Or manually: uvicorn backend.api:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd AI-DSA-Coach/frontend
npm run dev
```
*Available at `http://localhost:3000`*

---

## 🎮 How to Use

1. **Pick a Challenge:** Select a DSA problem from the dropdown.
2. **Connect Wallet:** Toggle Web3 mode and link your 0G/Metamask wallet.
3. **Discuss Approach:** Explain your strategy to the Mentor Agent.
4. **Write Code:** Implement your approved logic in the built-in editor.
5. **Get Rewarded:** Analyze your performance and claim your on-chain tokens!

<div align="center">
  <i>Built with ❤️</i>
</div>
