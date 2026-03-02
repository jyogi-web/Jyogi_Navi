'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { hasConsented } from '@/lib/session';

export default function ChatPage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // 未同意の場合はホームページへリダイレクト
    if (!hasConsented()) {
      router.push('/');
    } else {
      setIsChecking(false);
    }
  }, [router]);

  if (isChecking) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100 mx-auto"></div>
          <p className="mt-4 text-sm text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">チャット画面</h1>
        <p className="text-muted-foreground">
          この画面は次のステップで実装します
        </p>
      </div>
    </div>
  );
}
