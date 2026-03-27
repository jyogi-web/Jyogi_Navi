const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export type UserRole = "ADMIN" | "MEMBER";

export interface AdminUser {
  id: string;
  discord_user_id: string;
  role: UserRole;
}

/** 現在ログイン中のユーザー情報を取得する。未認証時は null を返す。 */
export async function getMe(): Promise<AdminUser | null> {
  try {
    const res = await fetch(`${API_URL}/api/auth/me`, {
      credentials: "include",
    });
    if (!res.ok) return null;
    return res.json() as Promise<AdminUser>;
  } catch {
    return null;
  }
}

/** ログアウトして /login にリダイレクトする。 */
export async function logout(): Promise<void> {
  await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  window.location.href = "/login";
}
