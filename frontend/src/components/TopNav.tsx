"use client";
import { Problem } from "@/lib/api";
import { useApp, Phase } from "@/lib/context";
import { Brain, ChevronDown, CheckCircle } from "lucide-react";

const AGENT_LABELS: Record<Phase, { label: string; icon: string; color: string }> = {
  mentoring: { label: "Mentor Agent", icon: "🗣️", color: "text-[#6c63ff]" },
  coding: { label: "Code Agent", icon: "💻", color: "text-emerald-400" },
  evaluation: { label: "Evaluation Agent", icon: "📊", color: "text-amber-400" },
};

const PHASES: { id: Phase; label: string; step: number }[] = [
  { id: "mentoring", label: "Approach", step: 1 },
  { id: "coding", label: "Code", step: 2 },
  { id: "evaluation", label: "Evaluate", step: 3 },
];

const SKILL_CONFIG: Record<string, { color: string; bg: string; border: string }> = {
  Beginner:     { color: "text-amber-400",   bg: "bg-amber-400/10",   border: "border-amber-400/30" },
  Intermediate: { color: "text-blue-400",    bg: "bg-blue-400/10",    border: "border-blue-400/30" },
  Advanced:     { color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/30" },
};

interface Props {
  problems: Problem[];
  onSelectProblem: (p: Problem) => void;
}

export default function TopNav({ problems, onSelectProblem }: Props) {
  const { state, dispatch } = useApp();
  const agent = AGENT_LABELS[state.phase];
  const phaseIndex = PHASES.findIndex((p) => p.id === state.phase);
  const skill = state.skillLevel ? SKILL_CONFIG[state.skillLevel] : null;

  return (
    <header className="flex items-center gap-3 px-5 py-2.5 border-b border-white/10 bg-[#0a0a0f]/90 backdrop-blur-md z-50 flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="w-7 h-7 rounded-lg bg-[#6c63ff] flex items-center justify-center">
          <Brain className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="text-white font-bold text-sm">AI DSA Coach</span>
      </div>

      {/* Problem Selector */}
      <div className="flex-1 max-w-xs relative">
        <select
          value={state.selectedProblem?.id ?? ""}
          onChange={(e) => {
            const p = problems.find((x) => x.id === e.target.value);
            if (p) onSelectProblem(p);
          }}
          className="w-full appearance-none bg-white/5 border border-white/10 text-xs text-slate-200 rounded-xl px-3 py-2 pr-7 focus:outline-none focus:border-[#6c63ff]/50 transition-colors cursor-pointer"
        >
          <option value="" disabled className="bg-[#111118]">Select a problem...</option>
          {problems.map((p) => (
            <option key={p.id} value={p.id} className="bg-[#111118]">
              {p.title} — {p.difficulty}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500 pointer-events-none" />
      </div>

      {/* Phase Steps (the ONE tab bar — in TopNav only) */}
      <div className="hidden md:flex items-center gap-1 bg-white/5 border border-white/10 rounded-xl p-1">
        {PHASES.map((phase, idx) => {
          const isDone = idx < phaseIndex;
          const isActive = idx === phaseIndex;
          return (
            <button
              key={phase.id}
              onClick={() => dispatch({ type: "SET_PHASE", phase: phase.id })}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? "bg-[#6c63ff] text-white shadow"
                  : isDone
                  ? "text-emerald-400 hover:bg-white/5 cursor-pointer"
                  : "text-slate-500 hover:text-slate-300 cursor-pointer"
              }`}
            >
              {isDone ? <CheckCircle className="w-3 h-3" /> : <span>{phase.step}.</span>}
              {phase.label}
            </button>
          );
        })}
      </div>

      {/* Skill Level Badge */}
      {skill && state.skillLevel ? (
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold ${skill.color} ${skill.bg} ${skill.border}`}>
          🎯 {state.skillLevel}
        </div>
      ) : (
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold text-slate-500 bg-white/5 border-white/10">
          🎯 Detecting Level...
        </div>
      )}

      {/* Active Agent + pulse */}
      <div className="ml-auto flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-3 py-1.5">
        <span className="text-sm">{agent.icon}</span>
        <div>
          <p className={`text-xs font-semibold leading-none ${agent.color}`}>{agent.label}</p>
          <p className="text-[10px] text-slate-500 leading-none mt-0.5">Active</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1 flex-shrink-0" />
      </div>
    </header>
  );
}
