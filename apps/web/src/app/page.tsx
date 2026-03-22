"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import { ConsentScreen } from "@/features/consent";
import { getConsent } from "@/lib/session";

const subscribe = () => () => {};

export default function Home() {
  const router = useRouter();
  const isHydrated = useSyncExternalStore(
    subscribe,
    () => true,
    () => false
  );
  const consented = isHydrated ? getConsent() : false;

  useEffect(() => {
    // 同意済みかチェックし、済んでいればチャット画面へリダイレクト
    if (isHydrated && consented) {
      router.replace("/chat");
    }
  }, [router, isHydrated, consented]);

  if (!isHydrated || consented) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-gray-900 dark:border-gray-100"></div>
          <p className="text-muted-foreground mt-4 text-sm">読み込み中...</p>
        </div>
      </div>
    );
  }

  return <ConsentScreen />;
}
