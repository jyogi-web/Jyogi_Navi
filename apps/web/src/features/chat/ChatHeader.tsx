"use client";

import { Button } from "@/components/ui/button";
import { ArrowLeft, MoreVertical } from "lucide-react";
import { useRouter } from "next/navigation";
import { saveConsent } from "@/lib/session";

interface ChatHeaderProps {
  messagesCount: number;
}

export function ChatHeader({ messagesCount }: ChatHeaderProps) {
  const router = useRouter();

  const handleBack = () => {
    // 同意をリセットしてホームに戻る（デモ用）
    if (
      confirm(
        "同意をリセットしてホーム画面に戻りますか？\n（開発中のため、実際はログアウト機能になります）"
      )
    ) {
      saveConsent(false);
      router.push("/");
    }
  };

  const handleMenuClick = () => {
    // TODO: メニュー機能を実装
    alert("メニュー機能は開発中です");
  };

  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white/80 backdrop-blur-sm dark:border-gray-700 dark:bg-gray-900/80">
      <div className="mx-auto max-w-4xl px-4 py-3">
        <div className="flex items-center justify-between">
          {/* 左側：戻るボタンとタイトル */}
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBack}
              className="rounded-full"
              aria-label="ホームへ戻る（同意をリセット）"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-600">
                <span className="text-2xl">🐰</span>
              </div>
              <div>
                <h1 className="text-lg leading-tight font-bold">じょぎナビ</h1>
                <p className="text-muted-foreground text-xs">
                  {messagesCount > 0 ? `${messagesCount}件の会話` : "いつでも質問してください"}
                </p>
              </div>
            </div>
          </div>

          {/* 右側：メニューボタン */}
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            aria-label="メニュー"
            onClick={handleMenuClick}
          >
            <MoreVertical className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
