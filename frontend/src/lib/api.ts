// API client for the FastAPI backend
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Problem {
  id: string;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  category: string;
  description: string;
  examples: { input: string; output: string; explanation?: string }[];
  constraints?: string[];
  hints?: string[];
  time_complexity?: string;
  space_complexity?: string;
  companies?: string[];
  tags?: string[];
}

export interface MentorResult {
  skill_level: string;
  approved: boolean;
  message: string;
  reasoning?: string;
  hint?: string;
  completeness_score?: number;
  conversation: { role: string; content: string }[];
  state: string;
}

export interface CodeResult {
  passed: boolean;
  feedback: string;
  bugs?: string[];
  optimizations?: string[];
  time_complexity?: string;
}

export interface EvalResult {
  summary: string;
  complexity_analysis: string;
  actionable_feedback: string;
  raw_data: {
    technical_score: number;
    approach_score: number;
    time_complexity: string;
    space_complexity: string;
    is_optimal: boolean;
    correctness: string;
    key_strengths: string[];
    main_weakness: string;
    optimization_tip: string;
    next_focus: string;
  };
  analytics: {
    total_duration: number;
    user_interactions: number;
    hints_requested: number;
    code_submissions: number;
    total_transitions: number;
    interaction_frequency: number;
  };
}

export interface SessionState {
  state: string;
  active_agent: string;
  skill_level: string | null;
  hints_used: number;
  approach_approved: boolean;
  progress: { current_phase: string; progress_percentage: number };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  getProblems: () => request<Problem[]>("/problems"),

  mentorAnalyze: (sessionId: string, userInput: string, problem: Problem) =>
    request<MentorResult>("/mentor/analyze", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, user_input: userInput, problem }),
    }),

  mentorHint: (sessionId: string, skillLevel: string, problem: Problem) =>
    request<{ hint: string; hints_used: number; conversation: { role: string; content: string }[] }>(
      "/mentor/hint",
      {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, skill_level: skillLevel, problem }),
      }
    ),

  codeEvaluate: (sessionId: string, userCode: string, problem: Problem, skillLevel: string, language?: string) =>
    request<CodeResult>("/code/evaluate", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, user_code: userCode, problem, skill_level: skillLevel, language: language ?? "python" }),
    }),

  codeAssist: (sessionId: string, question: string, userCode: string, problem: Problem, skillLevel: string) =>
    request<{ response: string; conversation: { role: string; content: string }[] }>("/code/assist", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        question,
        user_code: userCode,
        problem,
        skill_level: skillLevel,
      }),
    }),

  evaluate: (sessionId: string, problem: Problem, userCode: string, skillLevel: string, hintsUsed: number) =>
    request<EvalResult>("/evaluate", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        problem,
        user_code: userCode,
        skill_level: skillLevel,
        hints_used: hintsUsed,
      }),
    }),

  getState: (sessionId: string) => request<SessionState>(`/session/${sessionId}/state`),

  resetSession: (sessionId: string) =>
    request<{ status: string }>("/session/reset", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
};
