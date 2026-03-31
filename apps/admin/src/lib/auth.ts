import { logoutApiAuthLogoutPost, meApiAuthMeGet } from "@jyogi-navi/openapi/sdk";
import type { UserResponse, UserRole } from "@jyogi-navi/openapi/types";

export type { UserResponse, UserRole };

/** 現在ログイン中のユーザー情報を取得する。未認証時は null を返す。 */
export async function getMe(): Promise<UserResponse | null> {
  try {
    const { data } = await meApiAuthMeGet({ credentials: "include" });
    return data ?? null;
  } catch {
    return null;
  }
}

/** ログアウトして /login にリダイレクトする。 */
export async function logout(): Promise<void> {
  await logoutApiAuthLogoutPost({ credentials: "include" });
  window.location.href = "/login";
}
