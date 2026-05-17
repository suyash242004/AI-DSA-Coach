"use client";
import Link from "next/link";
import { Brain, ChevronRight, Code2, MessageSquare, BarChart2, Cpu, Zap, CheckCircle } from "lucide-react";

const AGENTS = [
  {
    icon: "🗣️",
    name: "Mentor Agent",
    color: "#6c63ff",
    bg: "bg-[#6c63ff]/10",
    border: "border-[#6c63ff]/20",
    desc: "Evaluates your approach before you write code. Adapts to Beginner, Intermediate, and Advanced levels with personalized hints.",
  },
  {
    icon: "💻",
    name: "Code Agent",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    desc: "Reviews your code for correctness, bugs, edge cases, and time/space complexity. Provides an inline AI coding assistant.",
  },
  {
    icon: "📊",
    name: "Evaluation Agent",
    color: "#f59e0b",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
    desc: "Generates a detailed performance report with scores, complexity analysis, strengths, weaknesses, and next steps.",
  },
  {
    icon: "🎮",
    name: "Orchestrator",
    color: "#ec4899",
    bg: "bg-pink-500/10",
    border: "border-pink-500/20",
    desc: "Manages the flow between all agents, tracks your session, and ensures smooth transitions through each phase.",
  },
];

const FEATURES = [
  { icon: <MessageSquare className="w-4 h-4" />, text: "Adaptive AI mentoring based on your skill level" },
  { icon: <Code2 className="w-4 h-4" />, text: "VS Code-quality Monaco editor with syntax highlighting" },
  { icon: <BarChart2 className="w-4 h-4" />, text: "Detailed performance scores and complexity analysis" },
  { icon: <Cpu className="w-4 h-4" />, text: "Multi-language support (Python, Java, C++, JavaScript)" },
  { icon: <Zap className="w-4 h-4" />, text: "Real-time feedback and optimisation tips" },
  { icon: <CheckCircle className="w-4 h-4" />, text: "12+ curated DSA problems across difficulty levels" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-mesh flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-white/10 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#6c63ff] flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-bold">AI DSA Coach</span>
        </div>
        <Link
          href="/app"
          className="flex items-center gap-2 px-4 py-2 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-xl text-sm font-semibold transition-all"
        >
          Launch App <ChevronRight className="w-4 h-4" />
        </Link>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-[#6c63ff]/10 border border-[#6c63ff]/30 rounded-full px-4 py-1.5 mb-8">
          <div className="w-2 h-2 rounded-full bg-[#6c63ff] animate-pulse" />
          <span className="text-[#6c63ff] text-xs font-semibold">Powered by Google Gemini AI</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 leading-tight max-w-4xl">
          Master DSA with{" "}
          <span className="bg-gradient-to-r from-[#6c63ff] to-[#a78bfa] bg-clip-text text-transparent">
            4 AI Agents
          </span>{" "}
          by your side
        </h1>

        <p className="text-slate-400 text-lg max-w-xl mb-10 leading-relaxed">
          Not just a LeetCode clone — a full AI coaching experience. The Mentor guides your thinking, the Code Agent reviews your solution, and the Evaluation Agent tracks your growth.
        </p>

        <div className="flex items-center gap-4 flex-wrap justify-center">
          <Link
            href="/app"
            className="flex items-center gap-2 px-8 py-4 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-2xl text-base font-bold transition-all shadow-lg shadow-[#6c63ff]/25 hover:shadow-[#6c63ff]/40 hover:-translate-y-0.5"
          >
            Start Solving Problems
            <ChevronRight className="w-5 h-5" />
          </Link>
          <a
            href="https://github.com/suyash242004/AI-DSA-Coach"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-8 py-4 bg-white/5 border border-white/10 text-white rounded-2xl text-base font-semibold hover:bg-white/10 transition-all"
          >
            View on GitHub
          </a>
        </div>

        {/* Features list */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-16 max-w-3xl w-full text-left">
          {FEATURES.map((f, i) => (
            <div key={i} className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-3">
              <span className="text-[#6c63ff] flex-shrink-0">{f.icon}</span>
              <span className="text-slate-300 text-xs font-medium">{f.text}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Agents Section */}
      <section className="px-8 py-16 border-t border-white/10">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-3">Meet Your 4-Agent System</h2>
          <p className="text-slate-400 text-center text-sm mb-10 max-w-lg mx-auto">
            Each agent is a specialist. Together they form a complete AI coaching pipeline from problem understanding to final evaluation.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {AGENTS.map((agent) => (
              <div
                key={agent.name}
                className={`${agent.bg} border ${agent.border} rounded-2xl p-5 flex flex-col gap-3 hover:-translate-y-1 transition-transform`}
              >
                <div className="text-3xl">{agent.icon}</div>
                <div>
                  <h3 className="text-white font-bold text-sm mb-1">{agent.name}</h3>
                  <p className="text-slate-400 text-xs leading-relaxed">{agent.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-8 py-16 text-center border-t border-white/10">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to level up your DSA skills?</h2>
        <p className="text-slate-400 text-sm mb-8">No sign-up needed. Just pick a problem and start solving.</p>
        <Link
          href="/app"
          className="inline-flex items-center gap-2 px-10 py-4 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-2xl text-base font-bold transition-all shadow-lg shadow-[#6c63ff]/25 hover:-translate-y-0.5"
        >
          Open the Coach <ChevronRight className="w-5 h-5" />
        </Link>
      </section>

      {/* Footer */}
      <footer className="px-8 py-6 border-t border-white/10 text-center text-slate-600 text-xs">
        AI DSA Coach — Built with ❤️ using Google Gemini, Next.js & FastAPI
      </footer>
    </div>
  );
}
