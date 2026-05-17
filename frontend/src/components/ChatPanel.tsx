"use client";
import { useRef, useEffect, useState } from "react";
import { Send, Lightbulb, CheckCircle, Loader2, ChevronRight } from "lucide-react";
import { useApp } from "@/lib/context";

// Inline markdown renderer using basic HTML
function MarkdownText({ text }: { text: string }) {
  // Bold **text**
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/💡 \*\*Hint:\*\*/g, '💡 <strong>Hint:</strong>');
  return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
}

export default function ChatPanel() {
  const { state, sendApproach, requestHint, moveToCode } = useApp();
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.mentorMessages]);

  const handleSend = async () => {
    if (!input.trim() || state.loading) return;
    const text = input.trim();
    setInput("");
    await sendApproach(text);
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleSend();
  };

  const roleConfig: Record<string, { label: string; color: string; bg: string; side: "left" | "right" }> = {
    user: { label: "You", color: "text-blue-300", bg: "bg-blue-500/10 border-blue-500/20", side: "right" },
    mentor: { label: "🗣️ Mentor Agent", color: "text-[#6c63ff]", bg: "bg-[#6c63ff]/10 border-[#6c63ff]/20", side: "left" },
    code_agent: { label: "💻 Code Agent", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20", side: "left" },
    system: { label: "⚙️ System", color: "text-slate-400", bg: "bg-white/5 border-white/10", side: "left" },
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div>
          <h2 className="text-white font-semibold text-sm">🗣️ Mentor Agent</h2>
          <p className="text-slate-500 text-xs mt-0.5">Explain your approach to unlock the code editor</p>
        </div>
        {state.skillLevel && (
          <span className="text-xs font-semibold text-[#6c63ff] bg-[#6c63ff]/10 border border-[#6c63ff]/20 px-3 py-1 rounded-full">
            {state.skillLevel}
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-3 pr-1 mb-4">
        {state.mentorMessages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-3">🧠</div>
            <p className="text-slate-400 text-sm font-medium">Hi! I&apos;m your Mentor Agent.</p>
            <p className="text-slate-500 text-xs mt-1 max-w-xs mx-auto">
              Describe your approach in detail. I&apos;ll guide you through your thinking before you code.
            </p>
            <div className="mt-4 bg-white/5 border border-white/10 rounded-xl p-4 max-w-sm mx-auto text-left space-y-3">
              <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">✅ What a good approach looks like:</p>
              <div className="space-y-2 text-xs text-slate-300">
                <p><span className="text-[#6c63ff]">Arrays:</span> <span className="italic text-slate-400">&quot;I&apos;ll use two nested loops. The outer runs 0 to n-1, inner from i+1 to n-1. I check the condition and return the indices.&quot;</span></p>
                <p><span className="text-emerald-400">Trees:</span> <span className="italic text-slate-400">&quot;I&apos;ll use DFS recursion. Base case is null node. I process each node, recurse left and right, and combine results.&quot;</span></p>
                <p><span className="text-amber-400">Graphs:</span> <span className="italic text-slate-400">&quot;I&apos;ll use BFS with a queue. Start from source, mark visited, add neighbours, continue until target found.&quot;</span></p>
              </div>
              <p className="text-[10px] text-slate-600 border-t border-white/10 pt-2">❌ Too vague: &quot;use a loop&quot; or &quot;use a hash map&quot; — explain the full algorithm!</p>
            </div>
          </div>
        )}

        {state.mentorMessages.map((msg) => {
          const cfg = roleConfig[msg.role] ?? roleConfig["system"];
          return (
            <div
              key={msg.id}
              className={`flex ${cfg.side === "right" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl border px-4 py-3 text-sm leading-relaxed ${cfg.bg}`}
              >
                <div className={`text-[11px] font-semibold uppercase tracking-wider mb-1.5 ${cfg.color}`}>
                  {cfg.label}
                </div>
                <div className="text-slate-300">
                  <MarkdownText text={msg.content} />
                </div>
              </div>
            </div>
          );
        })}

        {state.loading && (
          <div className="flex justify-start">
            <div className="bg-[#6c63ff]/10 border border-[#6c63ff]/20 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2 text-[#6c63ff] text-xs">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Mentor is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Approved Banner */}
      {state.approachApproved && (
        <div className="mb-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span className="text-emerald-300 text-sm font-medium">Approach approved! Ready to code.</span>
          </div>
          <button
            onClick={moveToCode}
            className="flex items-center gap-1 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-all"
          >
            Start Coding <ChevronRight className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Input Area */}
      <div className="space-y-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Describe your approach in detail... (Ctrl+Enter to send)"
          rows={3}
          className="w-full bg-[#0d0d14] border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-[#6c63ff]/60 resize-none transition-colors"
          disabled={state.loading}
        />
        <div className="flex gap-2">
          <button
            onClick={requestHint}
            disabled={state.loading || !state.selectedProblem}
            className="flex items-center gap-2 px-4 py-2.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl text-xs font-semibold hover:bg-amber-500/20 transition-all disabled:opacity-40"
          >
            <Lightbulb className="w-3.5 h-3.5" />
            Hint {state.hintsUsed > 0 && `(${state.hintsUsed})`}
          </button>
          <button
            onClick={handleSend}
            disabled={state.loading || !input.trim() || !state.selectedProblem}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-xl text-sm font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {state.loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                Submit Approach
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {state.error && (
        <div className="mt-2 bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-400 text-xs">
          ⚠️ {state.error}
        </div>
      )}
    </div>
  );
}
