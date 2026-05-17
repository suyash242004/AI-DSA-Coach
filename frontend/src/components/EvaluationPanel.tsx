"use client";
import { useEffect, useState } from "react";
import { Loader2, RefreshCw, TrendingUp, AlertCircle, CheckCircle, Zap, Target } from "lucide-react";
import { useApp } from "@/lib/context";
import { api, EvalResult } from "@/lib/api";

function ScoreRing({ score, max = 10, color }: { score: number; max?: number; color: string }) {
  const pct = (score / max) * 100;
  const r = 28;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width="72" height="72" className="rotate-[-90deg]">
      <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="6" />
      <circle
        cx="36" cy="36" r={r} fill="none"
        stroke={color} strokeWidth="6"
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        style={{ transition: "stroke-dasharray 1s ease" }}
      />
    </svg>
  );
}

export default function EvaluationPanel() {
  const { state, resetForNewProblem, moveToCode } = useApp();
  const [result, setResult] = useState<EvalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!state.selectedProblem) return;
    setLoading(true);
    setError(null);
    api
      .evaluate(
        state.sessionId,
        state.selectedProblem,
        state.userCode,
        state.skillLevel || "Intermediate",
        state.hintsUsed
      )
      .then(setResult)
      .catch((e) => setError(e.message || "Evaluation failed"))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-2 border-[#6c63ff]/20 flex items-center justify-center">
            <Loader2 className="w-7 h-7 text-[#6c63ff] animate-spin" />
          </div>
        </div>
        <div className="text-center">
          <p className="text-white font-medium">Analyzing your solution...</p>
          <p className="text-slate-500 text-xs mt-1">The Evaluation Agent is reviewing your code</p>
        </div>
      </div>
    );

  if (error)
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="w-10 h-10 text-red-400" />
        <p className="text-red-400 text-sm text-center max-w-xs">{error}</p>
        <button
          onClick={() => {
            setError(null);
            setLoading(true);
          }}
          className="text-xs text-[#6c63ff] underline"
        >
          Retry
        </button>
      </div>
    );

  if (!result) return null;

  const raw = result.raw_data ?? {};
  const analytics = result.analytics ?? {};

  return (
    <div className="flex flex-col h-full overflow-y-auto custom-scrollbar pr-1">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 pb-3 border-b border-white/10">
        <div>
          <h2 className="text-white font-semibold">📊 Solution Analysis</h2>
          <p className="text-slate-500 text-xs mt-0.5">Evaluation Agent Report</p>
        </div>
        <span
          className={`text-xs font-bold px-3 py-1 rounded-full ${
            (raw.technical_score ?? 0) >= 7
              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
              : (raw.technical_score ?? 0) >= 4
              ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
              : "bg-red-500/10 text-red-400 border border-red-500/30"
          }`}
        >
          {(raw.technical_score ?? 0) >= 7 ? "✅ Strong" : (raw.technical_score ?? 0) >= 4 ? "⚠️ Needs Work" : "🔴 Improve"}
        </span>
      </div>

      {/* Score Rings */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        {[
          { label: "Technical", value: raw.technical_score, color: "#6c63ff" },
          { label: "Approach", value: raw.approach_score, color: "#10b981" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col items-center">
            <div className="relative">
              <ScoreRing score={value ?? 0} color={color} />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-lg font-bold text-white" style={{ color }}>{value ?? 0}</span>
              </div>
            </div>
            <span className="text-xs text-slate-400 mt-2 font-medium">{label}</span>
          </div>
        ))}
      </div>

      {/* Complexity */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {[
          { label: "Time", value: raw.time_complexity, icon: "⏱️" },
          { label: "Space", value: raw.space_complexity, icon: "💾" },
        ].map(({ label, value, icon }) => (
          <div key={label} className="bg-[#0d0d14] border border-white/10 rounded-xl p-3 text-center">
            <div className="text-xs text-slate-500 mb-1">{icon} {label}</div>
            <code className="text-[#6c63ff] font-bold text-sm">{value || "N/A"}</code>
          </div>
        ))}
      </div>

      {/* Optimal badge */}
      <div className={`flex items-center gap-2 p-3 rounded-xl border mb-4 text-sm ${
        raw.is_optimal
          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
          : "bg-amber-500/10 border-amber-500/30 text-amber-300"
      }`}>
        {raw.is_optimal ? <CheckCircle className="w-4 h-4 flex-shrink-0" /> : <Zap className="w-4 h-4 flex-shrink-0" />}
        <span className="text-xs">{raw.is_optimal ? "Optimal solution!" : "Can be optimized — " + (raw.optimization_tip || "")}</span>
      </div>

      {/* Session Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {[
          { label: "Time", value: `${analytics.total_duration?.toFixed(0) ?? 0}s` },
          { label: "Hints", value: state.hintsUsed },
          { label: "Submissions", value: analytics.code_submissions ?? 0 },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-3 text-center">
            <div className="text-lg font-bold text-white">{value}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Strengths */}
      {raw.key_strengths?.length > 0 && (
        <div className="mb-4 bg-white/5 border border-white/10 rounded-xl p-4">
          <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2">✅ Strengths</p>
          <ul className="space-y-1">
            {raw.key_strengths.map((s, i) => (
              <li key={i} className="text-slate-300 text-xs flex gap-2">
                <span className="text-emerald-400 mt-0.5">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weakness */}
      {raw.main_weakness && (
        <div className="mb-4 bg-white/5 border border-white/10 rounded-xl p-4">
          <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">🎯 Improve</p>
          <p className="text-slate-300 text-xs">{raw.main_weakness}</p>
        </div>
      )}

      {/* Next Focus */}
      {raw.next_focus && (
        <div className="mb-4 bg-[#6c63ff]/10 border border-[#6c63ff]/20 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-3.5 h-3.5 text-[#6c63ff]" />
            <p className="text-xs font-semibold text-[#6c63ff] uppercase tracking-wider">Next Focus</p>
          </div>
          <p className="text-slate-300 text-xs">{raw.next_focus}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-auto pt-4 border-t border-white/10">
        <button
          onClick={moveToCode}
          className="flex-1 py-2.5 bg-white/5 border border-white/10 text-slate-300 rounded-xl text-xs font-semibold hover:bg-white/10 transition-all"
        >
          ← Back to Code
        </button>
        <button
          onClick={resetForNewProblem}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-xl text-xs font-semibold transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          New Problem
        </button>
      </div>
    </div>
  );
}
