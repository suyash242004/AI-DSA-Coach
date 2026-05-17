"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
import { Play, Send, RotateCcw, BarChart2, Loader2, MessageSquare, ChevronDown } from "lucide-react";
import { useApp } from "@/lib/context";
import { api } from "@/lib/api";

import CodeEditorUIW from "@uiw/react-textarea-code-editor";

const LANGUAGES = [
  { id: "python",     label: "Python",     monacoId: "python",     ext: "py" },
  { id: "javascript", label: "JavaScript", monacoId: "javascript", ext: "js" },
  { id: "java",       label: "Java",       monacoId: "java",       ext: "java" },
  { id: "cpp",        label: "C++",        monacoId: "cpp",        ext: "cpp" },
  { id: "go",         label: "Go",         monacoId: "go",         ext: "go" },
];

const DEFAULT_CODE: Record<string, string> = {
  python: `def solution():\n    # Write your solution here\n    pass\n\nif __name__ == "__main__":\n    pass`,
  javascript: `function solution() {\n    // Write your solution here\n}\n\nconsole.log(solution());`,
  java: `public class Solution {\n    public void solution() {\n        // Write your solution here\n    }\n\n    public static void main(String[] args) {\n        new Solution().solution();\n    }\n}`,
  cpp: `#include <iostream>\n#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    void solution() {\n        // Write your solution here\n    }\n};\n\nint main() {\n    Solution s;\n    s.solution();\n    return 0;\n}`,
  go: `package main\n\nimport "fmt"\n\nfunc solution() {\n    // Write your solution here\n}\n\nfunc main() {\n    solution()\n}`,
};

export default function CodeEditor() {
  const { state, dispatch, moveToEvaluation, addMsg } = useApp();
  const [question, setQuestion] = useState("");
  const [running, setRunning] = useState(false);
  const [asking, setAsking] = useState(false);
  const [testResult, setTestResult] = useState<{ passed: boolean; feedback: string } | null>(null);

  // Language stored in global state so evaluation panel can use it
  const language = state.language;
  const currentLang = LANGUAGES.find((l) => l.id === language) ?? LANGUAGES[0];

  const handleLanguageChange = (langId: string) => {
    dispatch({ type: "SET_LANGUAGE", language: langId });
    // Reset to template only if code is still default or empty
    const isDefault = Object.values(DEFAULT_CODE).some(
      (tmpl) => state.userCode.trim() === tmpl.trim()
    );
    if (isDefault || !state.userCode.trim()) {
      dispatch({ type: "SET_CODE", code: DEFAULT_CODE[langId] });
    }
    setTestResult(null);
  };

  const handleRunCode = async () => {
    if (!state.selectedProblem || !state.userCode.trim()) return;
    setRunning(true);
    setTestResult(null);
    try {
      const result = await api.codeEvaluate(
        state.sessionId,
        state.userCode,
        state.selectedProblem,
        state.skillLevel || "Intermediate",
        language          // ← pass language to backend
      );
      setTestResult({ passed: result.passed, feedback: result.feedback });
      addMsg("code", "system", result.feedback);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Evaluation failed";
      setTestResult({ passed: false, feedback: `Error: ${msg}` });
    } finally {
      setRunning(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim() || !state.selectedProblem) return;
    setAsking(true);
    addMsg("code", "user", question);
    const q = question;
    setQuestion("");
    try {
      const res = await api.codeAssist(
        state.sessionId,
        q,
        state.userCode,
        state.selectedProblem,
        state.skillLevel || "Intermediate"
      );
      addMsg("code", "code_agent", res.response);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Assistant failed";
      addMsg("code", "system", `Error: ${msg}`);
    } finally {
      setAsking(false);
    }
  };

  const roleConfig: Record<string, { label: string; color: string }> = {
    user: { label: "You", color: "text-blue-300" },
    code_agent: { label: "💻 Code Agent", color: "text-emerald-400" },
    system: { label: "⚙️ Result", color: "text-slate-400" },
  };

  return (
    <div className="flex flex-col h-full gap-3 min-h-0">
      {/* Toolbar row */}
      <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">
        <div className="flex items-center gap-2 bg-[#0d0d14] border border-white/10 rounded-xl px-3 py-1.5 flex-1 min-w-0">
          <span className="text-slate-500 text-xs font-mono truncate">solution.{currentLang.ext}</span>
          <div className="ml-auto flex items-center gap-1 flex-shrink-0">
            <span className="text-[10px] text-slate-600">Hints:</span>
            <span className="text-amber-400 text-[10px] font-bold">{state.hintsUsed}</span>
          </div>
        </div>

        {/* Language Selector */}
        <div className="relative flex-shrink-0">
          <select
            value={language}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="appearance-none bg-white/5 border border-white/10 text-xs text-slate-300 rounded-xl px-3 py-2 pr-7 focus:outline-none focus:border-[#6c63ff]/50 cursor-pointer"
          >
            {LANGUAGES.map((l) => (
              <option key={l.id} value={l.id} className="bg-[#111118]">
                {l.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500 pointer-events-none" />
        </div>

        <button
          onClick={handleRunCode}
          disabled={running || !state.selectedProblem}
          className="flex items-center gap-1.5 px-3 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-xl text-xs font-semibold transition-all disabled:opacity-40 flex-shrink-0"
        >
          {running ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          Run
        </button>
        <button
          onClick={() => { dispatch({ type: "SET_CODE", code: DEFAULT_CODE[language] }); setTestResult(null); }}
          className="flex items-center gap-1.5 px-2.5 py-2 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-xs hover:bg-white/10 transition-all flex-shrink-0"
          title="Reset to template"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={moveToEvaluation}
          className="flex items-center gap-1.5 px-3 py-2 bg-[#6c63ff] hover:bg-[#7c73ff] text-white rounded-xl text-xs font-semibold transition-all flex-shrink-0"
        >
          <BarChart2 className="w-3.5 h-3.5" />
          Evaluate
        </button>
      </div>

      {/* Simple Textarea Editor - 100% bug free cursor */}
      <div className="flex-1 min-h-0 rounded-xl overflow-hidden border border-white/10 w-full relative bg-[#1e1e1e]">
        <div className="absolute inset-0 overflow-auto custom-scrollbar">
          <CodeEditorUIW
            value={state.userCode || DEFAULT_CODE[language]}
            language={currentLang.monacoId}
            placeholder="Please enter your code here."
            onChange={(evn) => dispatch({ type: "SET_CODE", code: evn.target.value })}
            padding={16}
            style={{
              fontSize: 14,
              backgroundColor: "transparent",
              fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
              outline: "none"
            }}
          />
        </div>
      </div>

      {/* Test Result */}
      {testResult && (
        <div
          className={`flex-shrink-0 p-3 rounded-xl border text-xs leading-relaxed ${
            testResult.passed
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-red-500/10 border-red-500/30 text-red-300"
          }`}
        >
          <strong>{testResult.passed ? "✅ Passed" : "❌ Failed"}</strong>
          <p className="text-slate-400 mt-1 whitespace-pre-wrap text-[11px] leading-relaxed">
            {testResult.feedback.slice(0, 300)}{testResult.feedback.length > 300 ? "..." : ""}
          </p>
        </div>
      )}

      {/* Code Assistant Chat */}
      <div className="flex-shrink-0 border border-white/10 rounded-xl overflow-hidden">
        <div className="bg-white/5 px-3 py-2 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Code Assistant</span>
          </div>
          {state.codeMessages.length > 0 && (
            <span className="text-[10px] text-slate-600">{state.codeMessages.length} msgs</span>
          )}
        </div>

        {state.codeMessages.length > 0 && (
          <div className="max-h-24 overflow-y-auto custom-scrollbar p-3 space-y-1.5">
            {state.codeMessages.slice(-4).map((msg) => {
              const cfg = roleConfig[msg.role] ?? { label: msg.role, color: "text-slate-400" };
              return (
                <div key={msg.id} className="text-xs leading-relaxed">
                  <span className={`font-semibold ${cfg.color}`}>{cfg.label}: </span>
                  <span className="text-slate-300">{msg.content.slice(0, 180)}{msg.content.length > 180 ? "..." : ""}</span>
                </div>
              );
            })}
          </div>
        )}

        <div className="flex gap-2 p-3 border-t border-white/10">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !asking && handleAsk()}
            placeholder="Ask about your code, complexity, bugs..."
            className="flex-1 bg-transparent text-xs text-slate-300 placeholder-slate-600 outline-none"
            disabled={asking}
          />
          <button
            onClick={handleAsk}
            disabled={asking || !question.trim()}
            className="text-[#6c63ff] hover:text-[#7c73ff] disabled:opacity-40 transition-colors flex-shrink-0"
          >
            {asking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}
