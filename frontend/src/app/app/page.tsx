"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { api, Problem } from "@/lib/api";
import { useApp } from "@/lib/context";
import TopNav from "@/components/TopNav";
import ProblemPanel from "@/components/ProblemPanel";
import ChatPanel from "@/components/ChatPanel";
import CodeEditor from "@/components/CodeEditor";
import EvaluationPanel from "@/components/EvaluationPanel";
import { Brain, WifiOff } from "lucide-react";

export default function AppPage() {
  const { state, dispatch } = useApp();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Resizable split — left panel width in px
  const [leftWidth, setLeftWidth] = useState(420);
  const isDragging = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Check backend health + load problems
  useEffect(() => {
    api
      .health()
      .then(() => {
        setBackendOk(true);
        return api.getProblems();
      })
      .then((data) => {
        setProblems(data);
        if (data.length > 0 && !state.selectedProblem) {
          dispatch({ type: "SET_PROBLEM", problem: data[0] });
        }
      })
      .catch((e) => {
        setBackendOk(false);
        setLoadError(e.message);
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectProblem = (problem: Problem) => {
    dispatch({ type: "RESET", sessionId: state.sessionId });
    dispatch({ type: "SET_PROBLEM", problem });
  };

  // Drag handlers for resizable splitter
  const onMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const newWidth = Math.max(280, Math.min(e.clientX - rect.left, rect.width - 320));
    setLeftWidth(newWidth);
  }, []);

  const onMouseUp = useCallback(() => {
    isDragging.current = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [onMouseMove, onMouseUp]);

  const startDrag = () => {
    isDragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  // ── Offline screen ────────────────────────────────────────────────────────
  if (backendOk === false) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-6 text-center px-4">
        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
          <WifiOff className="w-7 h-7 text-red-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Backend Offline</h1>
          <p className="text-slate-400 text-sm max-w-sm">
            Start the AI agent server first:
          </p>
        </div>
        <div className="bg-[#0d0d14] border border-white/10 rounded-xl p-4 text-left font-mono text-xs w-full max-w-sm">
          <p className="text-slate-500 mb-1"># From project root:</p>
          <p className="text-emerald-400">.\start.ps1</p>
          <p className="text-slate-500 mt-2 mb-1"># Or manually:</p>
          <p className="text-emerald-400">uvicorn backend.api:app --port 8000</p>
        </div>
        {loadError && <p className="text-red-400 text-xs">{loadError}</p>}
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2.5 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-xl text-sm font-semibold transition-all"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // ── Loading screen ────────────────────────────────────────────────────────
  if (backendOk === null) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-[#6c63ff]/20 flex items-center justify-center animate-pulse">
          <Brain className="w-6 h-6 text-[#6c63ff]" />
        </div>
        <p className="text-slate-400 text-sm">Connecting to AI agents...</p>
      </div>
    );
  }

  // ── Main App ──────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Single Top Navigation (contains phase tabs) */}
      <TopNav problems={problems} onSelectProblem={handleSelectProblem} />

      {!state.selectedProblem ? (
        /* Welcome splash */
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-4">
          <div className="text-6xl">🧠</div>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-2">Select a Problem to Begin</h2>
            <p className="text-slate-400 text-sm max-w-sm">
              Choose a DSA problem above. The Mentor Agent will guide you through your thinking before you code.
            </p>
          </div>
          <div className="grid grid-cols-4 gap-3 max-w-md w-full">
            {[
              { icon: "🗣️", label: "Mentor Agent" },
              { icon: "💻", label: "Code Agent" },
              { icon: "📊", label: "Evaluation Agent" },
              { icon: "🎮", label: "Orchestrator" },
            ].map((a) => (
              <div key={a.label} className="bg-white/5 border border-white/10 rounded-xl p-3 text-center">
                <div className="text-2xl mb-1">{a.icon}</div>
                <p className="text-[10px] text-slate-400 font-medium leading-tight">{a.label}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* Split layout with draggable divider */
        <div ref={containerRef} className="flex-1 flex overflow-hidden">
          {/* Left: Problem Panel */}
          <div
            className="flex-shrink-0 border-r border-white/10 bg-[#111118] p-5 overflow-hidden flex flex-col"
            style={{ width: leftWidth }}
          >
            <ProblemPanel problem={state.selectedProblem} />
          </div>

          {/* Drag Handle */}
          <div
            onMouseDown={startDrag}
            className="w-1.5 flex-shrink-0 cursor-col-resize hover:bg-[#6c63ff]/50 bg-white/5 transition-colors group relative"
            title="Drag to resize"
          >
            <div className="absolute inset-y-0 -left-1 -right-1" />
          </div>

          {/* Right: Agent Panel — NO extra tab bar here */}
          <div className="flex-1 bg-[#0f0f17] p-5 overflow-hidden flex flex-col min-w-0">
            {state.phase === "mentoring" && <ChatPanel />}
            {state.phase === "coding" && <CodeEditor />}
            {state.phase === "evaluation" && <EvaluationPanel />}
          </div>
        </div>
      )}
    </div>
  );
}
