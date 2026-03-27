import { NextRequest, NextResponse } from "next/server";

const COOKIE_NAME = "admin_token";
const LOGIN_PATH = "/login";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // ログインページ自体はスルー
  if (pathname === LOGIN_PATH) {
    return NextResponse.next();
  }

  const token = request.cookies.get(COOKIE_NAME)?.value;
  if (!token) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = LOGIN_PATH;
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  // _next の静的アセットと favicon はスキップ
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
