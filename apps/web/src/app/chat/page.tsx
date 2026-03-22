"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import { getConsent } from "@/lib/session";
import { ChatContainer } from "@/features/chat";

const subscribe = () => () => {};

export default function ChatPage() {
  const router = useRouter();
  const isHydrated = useSyncExternalStore(
    subscribe,
    () => true,
    () => false
  );
  const consented = isHydrated ? getConsent() : false;

  useEffect(() => {
    // 未同意の場合はホームページへリダイレクト
    if (isHydrated && !consented) {
      router.replace("/");
    }
  }, [router, isHydrated, consented]);

  if (!isHydrated || !consented) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-gray-900 dark:border-gray-100"></div>
          <p className="text-muted-foreground mt-4 text-sm">読み込み中...</p>
        </div>
      </div>
    );
  }

  return <ChatContainer />;
}
