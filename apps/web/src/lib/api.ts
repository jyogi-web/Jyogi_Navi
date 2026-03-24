/**
 * Backend API client
 * Provides saveUsageLog, sendFeedback, createSession functions.
 * Errors are caught silently so UI is not disrupted by backend failures.
 */
import { client } from "@/client/client.gen";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

client.setConfig({ baseUrl: API_BASE });

export { client };

// ---- Types ----

export interface SessionResponse {
  id: string;
  is_guest: boolean;
  consented: boolean;
  created_at: string;
}

export interface UsageLogResponse {
  id: string;
  session_id: string;
  tokens: number;
  category: string;
  created_at: string;
}

export interface FeedbackResponse {
  id: string;
  session_id: string;
  message_id: string;
  rating: boolean;
  created_at: string;
}

// ---- API functions ----

/**
 * セッションを作成する（同意画面でユーザーが同意したとき）。
 */
export async function createSession(is_guest = true): Promise<SessionResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/consent/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_guest }),
    });
    if (!res.ok) return null;
    return (await res.json()) as SessionResponse;
  } catch {
    return null;
  }
}

/**
 * トークン消費ログを保存する（メッセージ送受信後）。
 */
export async function saveUsageLog(
  session_id: string,
  tokens: number,
  category = ""
): Promise<UsageLogResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/consent/usage_logs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, tokens, category }),
    });
    if (!res.ok) return null;
    return (await res.json()) as UsageLogResponse;
  } catch {
    return null;
  }
}

/**
 * フィードバック（👍👎）を保存する。
 */
export async function sendFeedback(
  session_id: string,
  message_id: string,
  rating: boolean
): Promise<FeedbackResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, message_id, rating }),
    });
    if (!res.ok) return null;
    return (await res.json()) as FeedbackResponse;
  } catch {
    return null;
  }
}
