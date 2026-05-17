"use client";
import React, { createContext, useContext, useReducer, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import { Problem, MentorResult, api } from "@/lib/api";

export type Phase = "mentoring" | "coding" | "evaluation";
export type SkillLevel = "Beginner" | "Intermediate" | "Advanced" | null;

export interface Message {
  id: string;
  role: "user" | "mentor" | "code_agent" | "system";
  content: string;
  timestamp: Date;
}

interface AppState {
  sessionId: string;
  selectedProblem: Problem | null;
  phase: Phase;
  skillLevel: SkillLevel;
  hintsUsed: number;
  approachApproved: boolean;
  mentorMessages: Message[];
  codeMessages: Message[];
  userCode: string;
  language: string;
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: "SET_PROBLEM"; problem: Problem }
  | { type: "SET_PHASE"; phase: Phase }
  | { type: "SET_SKILL"; level: string }
  | { type: "ADD_MENTOR_MSG"; msg: Message }
  | { type: "ADD_CODE_MSG"; msg: Message }
  | { type: "SET_CODE"; code: string }
  | { type: "SET_LANGUAGE"; language: string }
  | { type: "SET_HINTS"; count: number }
  | { type: "SET_APPROVED" }
  | { type: "SET_LOADING"; loading: boolean }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "RESET"; sessionId: string };

const DEFAULT_CODE = `def solution():
    # Write your solution here
    pass

# Test your solution
if __name__ == "__main__":
    pass`;

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "SET_PROBLEM":
      return { ...state, selectedProblem: action.problem };
    case "SET_PHASE":
      return { ...state, phase: action.phase };
    case "SET_SKILL":
      return { ...state, skillLevel: action.level as SkillLevel };
    case "ADD_MENTOR_MSG":
      return { ...state, mentorMessages: [...state.mentorMessages, action.msg] };
    case "ADD_CODE_MSG":
      return { ...state, codeMessages: [...state.codeMessages, action.msg] };
    case "SET_CODE":
      return { ...state, userCode: action.code };
    case "SET_LANGUAGE":
      return { ...state, language: action.language };
    case "SET_HINTS":
      return { ...state, hintsUsed: action.count };
    case "SET_APPROVED":
      return { ...state, approachApproved: true };
    case "SET_LOADING":
      return { ...state, loading: action.loading };
    case "SET_ERROR":
      return { ...state, error: action.error };
    case "RESET":
      return {
        ...initialState,
        sessionId: action.sessionId,
        selectedProblem: state.selectedProblem,
        userCode: DEFAULT_CODE,
      };
    default:
      return state;
  }
}

const initialState: AppState = {
  sessionId: uuidv4(),
  selectedProblem: null,
  phase: "mentoring",
  skillLevel: null,
  hintsUsed: 0,
  approachApproved: false,
  mentorMessages: [],
  codeMessages: [],
  userCode: DEFAULT_CODE,
  language: "python",
  loading: false,
  error: null,
};

interface AppContextValue {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  sendApproach: (input: string) => Promise<void>;
  requestHint: () => Promise<void>;
  moveToCode: () => void;
  moveToEvaluation: () => void;
  resetForNewProblem: () => void;
  addMsg: (
    conv: "mentor" | "code",
    role: Message["role"],
    content: string
  ) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const addMsg = useCallback(
    (conv: "mentor" | "code", role: Message["role"], content: string) => {
      const msg: Message = { id: uuidv4(), role, content, timestamp: new Date() };
      dispatch({ type: conv === "mentor" ? "ADD_MENTOR_MSG" : "ADD_CODE_MSG", msg });
    },
    []
  );

  const sendApproach = useCallback(
    async (input: string) => {
      if (!state.selectedProblem) return;
      dispatch({ type: "SET_LOADING", loading: true });
      dispatch({ type: "SET_ERROR", error: null });
      addMsg("mentor", "user", input);
      try {
        const result: MentorResult = await api.mentorAnalyze(
          state.sessionId,
          input,
          state.selectedProblem
        );
        addMsg("mentor", "mentor", result.message);
        if (result.skill_level) dispatch({ type: "SET_SKILL", level: result.skill_level });
        // NOTE: Do NOT increment hints here — only increment when user explicitly clicks Hint button
        if (result.approved) {
          dispatch({ type: "SET_APPROVED" });
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Failed to connect to AI backend. Make sure the Python server is running.";
        dispatch({ type: "SET_ERROR", error: msg });
      } finally {
        dispatch({ type: "SET_LOADING", loading: false });
      }
    },
    [state.selectedProblem, state.sessionId, state.hintsUsed, addMsg]
  );

  const requestHint = useCallback(async () => {
    if (!state.selectedProblem) return;
    dispatch({ type: "SET_LOADING", loading: true });
    try {
      const result = await api.mentorHint(
        state.sessionId,
        state.skillLevel || "Intermediate",
        state.selectedProblem
      );
      addMsg("mentor", "mentor", `💡 **Hint:** ${result.hint}`);
      dispatch({ type: "SET_HINTS", count: result.hints_used });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to get hint.";
      dispatch({ type: "SET_ERROR", error: msg });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  }, [state.selectedProblem, state.sessionId, state.skillLevel, addMsg]);

  const moveToCode = useCallback(() => dispatch({ type: "SET_PHASE", phase: "coding" }), []);
  const moveToEvaluation = useCallback(() => dispatch({ type: "SET_PHASE", phase: "evaluation" }), []);

  const resetForNewProblem = useCallback(() => {
    const newId = uuidv4();
    api.resetSession(state.sessionId).catch(() => {});
    dispatch({ type: "RESET", sessionId: newId });
  }, [state.sessionId]);

  return (
    <AppContext.Provider value={{ state, dispatch, sendApproach, requestHint, moveToCode, moveToEvaluation, resetForNewProblem, addMsg }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
