/**
 * セッション管理
 * 新入生のセッションIDとログ同意状態を管理
 */

import { v4 as uuidv4 } from "uuid";

const SESSION_ID_KEY = "jyogi_session_id";
const CONSENT_KEY = "jyogi_consent";

/**
 * セッションIDを取得または生成
 */
export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "";

  try {
    let sessionId = localStorage.getItem(SESSION_ID_KEY);

    if (!sessionId) {
      sessionId = uuidv4();
      localStorage.setItem(SESSION_ID_KEY, sessionId);
    }

    return sessionId;
  } catch (error) {
    // SecurityError や QuotaExceededError などでストレージアクセスが失敗した場合
    // 空文字を返して呼び出し側に SESSION_ERROR として処理させる
    console.error("Failed to access localStorage:", error);
    return "";
  }
}

/**
 * 同意状態を保存
 */
export function saveConsent(consented: boolean): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.setItem(CONSENT_KEY, consented ? "true" : "false");
  } catch (error) {
    // SecurityError や QuotaExceededError などでストレージアクセスが失敗した場合は無視
    console.error("Failed to save consent to localStorage:", error);
  }
}

/**
 * 同意状態を取得
 */
export function getConsent(): boolean {
  if (typeof window === "undefined") return false;

  try {
    return localStorage.getItem(CONSENT_KEY) === "true";
  } catch (error) {
    // SecurityError や QuotaExceededError などでストレージアクセスが失敗した場合は安全なデフォルト値を返す
    console.error("Failed to get consent from localStorage:", error);
    return false;
  }
}
