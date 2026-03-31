const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;
  const isNotMember = error === "not_member";

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <h1 className="mb-2 text-center text-2xl font-bold text-gray-900">
          じょぎナビ 管理画面
        </h1>
        <p className="mb-8 text-center text-sm text-gray-500">
          じょぎ Discord サーバーのメンバーのみログインできます
        </p>

        {isNotMember && (
          <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
            じょぎ Discord サーバーのメンバーではないためログインできません。
          </p>
        )}

        <a
          href={`${API_URL}/api/auth/login`}
          className="flex w-full items-center justify-center gap-3 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-indigo-700"
        >
          <svg width="20" height="20" viewBox="0 0 71 55" fill="none" aria-hidden="true">
            <path
              d="M60.1 4.9A58.5 58.5 0 0 0 45.7.7a40.7 40.7 0 0 0-1.8 3.7 54.1 54.1 0 0 0-16.2 0A40.5 40.5 0 0 0 25.9.7 58.4 58.4 0 0 0 11.4 4.9C1.6 19.6-1 33.9.3 48C6.6 52.7 12.7 55.6 18.7 57.5a44 44 0 0 0 3.8-6.2 38.3 38.3 0 0 1-6-2.9l1.5-1.1a41.8 41.8 0 0 0 35.8 0l1.5 1.1a38.4 38.4 0 0 1-6 2.9 43.9 43.9 0 0 0 3.8 6.2c6-1.9 12.1-4.8 18.4-9.5C72.9 33.9 69.9 19.6 60.1 4.9ZM23.7 39.4c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2c3.5 0 6.4 3.2 6.3 7.2 0 4-2.8 7.2-6.3 7.2Zm23.6 0c-3.5 0-6.3-3.2-6.3-7.2s2.8-7.2 6.3-7.2c3.6 0 6.4 3.2 6.4 7.2 0 4-2.8 7.2-6.4 7.2Z"
              fill="currentColor"
            />
          </svg>
          Discord でログイン
        </a>
      </div>
    </div>
  );
}
