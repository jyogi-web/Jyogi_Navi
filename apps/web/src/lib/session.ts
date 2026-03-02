/**
 * セッション管理
 * 新入生のセッションIDとログ同意状態を管理
 */

import { v4 as uuidv4 } from 'uuid';

const SESSION_ID_KEY = 'jyogi_session_id';
const CONSENT_KEY = 'jyogi_consent';

/**
 * セッションIDを取得または生成
 */
export function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return '';
  
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  
  return sessionId;
}

/**
 * 同意状態を保存
 */
export function saveConsent(consented: boolean): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem(CONSENT_KEY, consented ? 'true' : 'false');
}

/**
 * 同意状態を取得
 */
export function getConsent(): boolean {
  if (typeof window === 'undefined') return false;
  
  return localStorage.getItem(CONSENT_KEY) === 'true';
}

/**
 * 同意状態をチェック
 */
export function hasConsented(): boolean {
  return getConsent();
}
