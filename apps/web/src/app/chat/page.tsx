'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { hasConsented } from '@/lib/session';
import { ChatContainer } from '@/features/chat';

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

  return <ChatContainer />;
}
