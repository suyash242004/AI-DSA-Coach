"use client";
import { Problem } from "@/lib/api";
import { useApp } from "@/lib/context";

const DIFFICULTY_CONFIG = {
  Easy: { color: "text-emerald-400", bg: "bg-emerald-400/10 border-emerald-400/20" },
  Medium: { color: "text-amber-400", bg: "bg-amber-400/10 border-amber-400/20" },
  Hard: { color: "text-red-400", bg: "bg-red-400/10 border-red-400/20" },
};

interface Props {
  problem: Problem;
}

export default function ProblemPanel({ problem }: Props) {
  const { state } = useApp();
  const diff = DIFFICULTY_CONFIG[problem.difficulty] ?? DIFFICULTY_CONFIG["Medium"];

  return (
    <div className="flex flex-col h-full overflow-y-auto custom-scrollbar pr-2">
      {/* Header */}
      <div className="mb-5">
        <div className="flex items-center gap-3 mb-3 flex-wrap">
          <span className="text-xs font-semibold text-[#6c63ff] uppercase tracking-wider bg-[#6c63ff]/10 px-3 py-1 rounded-full border border-[#6c63ff]/20">
            {problem.category}
          </span>
          <span className={`text-xs font-semibold uppercase tracking-wider px-3 py-1 rounded-full border ${diff.color} ${diff.bg}`}>
            {problem.difficulty}
          </span>
        </div>

        <h1 className="text-2xl font-bold text-white mb-3 leading-tight">{problem.title}</h1>

        {problem.companies && (
          <div className="flex gap-2 flex-wrap mb-3">
            {problem.companies.slice(0, 4).map((c) => (
              <span key={c} className="text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                {c}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Description */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-4">
        <p className="text-slate-300 text-sm leading-relaxed">{problem.description}</p>
      </div>

      {/* Examples */}
      {problem.examples?.length > 0 && (
        <div className="mb-4">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Examples</h2>
          <div className="space-y-3">
            {problem.examples.map((ex, i) => (
              <div key={i} className="bg-[#0d0d14] border border-white/10 rounded-lg p-4 font-mono text-sm">
                <div className="text-slate-400 mb-1">
                  <span className="text-slate-500">Input: </span>
                  <span className="text-emerald-300">{ex.input}</span>
                </div>
                <div className="text-slate-400 mb-1">
                  <span className="text-slate-500">Output: </span>
                  <span className="text-purple-300">{ex.output}</span>
                </div>
                {ex.explanation && (
                  <div className="text-slate-500 text-xs mt-2 border-t border-white/5 pt-2">
                    {ex.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Constraints */}
      {problem.constraints && problem.constraints.length > 0 && (
        <div className="mb-4">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Constraints</h2>
          <ul className="space-y-1.5">
            {problem.constraints.map((c, i) => (
              <li key={i} className="text-slate-400 text-sm flex gap-2">
                <span className="text-[#6c63ff] mt-0.5">•</span>
                <code className="text-slate-300 font-mono text-xs bg-white/5 px-2 py-0.5 rounded">{c}</code>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Complexity targets */}
      {(problem.time_complexity || problem.space_complexity) && (
        <div className="mt-auto pt-4 border-t border-white/10">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Optimal Complexity</h2>
          <div className="flex gap-3">
            {problem.time_complexity && (
              <div className="flex-1 bg-[#6c63ff]/10 border border-[#6c63ff]/20 rounded-lg p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">Time</div>
                <code className="text-[#6c63ff] font-bold text-sm">{problem.time_complexity}</code>
              </div>
            )}
            {problem.space_complexity && (
              <div className="flex-1 bg-emerald-400/10 border border-emerald-400/20 rounded-lg p-3 text-center">
                <div className="text-[10px] text-slate-500 mb-1">Space</div>
                <code className="text-emerald-400 font-bold text-sm">{problem.space_complexity}</code>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
