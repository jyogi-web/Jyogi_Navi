'use client';

import { Button } from '@/components/ui/button';
import { ArrowLeft, MoreVertical } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { saveConsent } from '@/lib/session';

interface ChatHeaderProps {
  messagesCount: number;
}

export function ChatHeader({ messagesCount }: ChatHeaderProps) {
  const router = useRouter();

  const handleBack = () => {
    // 同意をリセットしてホームに戻る（デモ用）
    if (
      confirm(
        '同意をリセットしてホーム画面に戻りますか？\n（開発中のため、実際はログアウト機能になります）'
      )
    ) {
      saveConsent(false);
      router.push('/');
    }
  };

  return (
    <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* 左側：戻るボタンとタイトル */}
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBack}
              className="rounded-full"
              aria-label="戻る"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
                <span className="text-2xl">🐰</span>
              </div>
              <div>
                <h1 className="font-bold text-lg leading-tight">
                  じょぎナビ
                </h1>
                <p className="text-xs text-muted-foreground">
                  {messagesCount > 0
                    ? `${messagesCount}件の会話`
                    : 'いつでも質問してください'}
                </p>
              </div>
            </div>
          </div>

          {/* 右側：メニューボタン */}
          <Button variant="ghost" size="icon" className="rounded-full" aria-label="メニュー">
            <MoreVertical className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
