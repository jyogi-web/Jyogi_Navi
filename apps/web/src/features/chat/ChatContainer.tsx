"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { v4 as uuidv4 } from "uuid";
import { Message } from "@/types/chat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { ChatHeader } from "./ChatHeader";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2 } from "lucide-react";

async function sendChatMessage(content: string): Promise<string> {
  // TODO: Dify API呼び出しに置き換える
  await new Promise((resolve) => setTimeout(resolve, 1500));
  return `ご質問ありがとうございます！「${content}」についてですね。\n\nこちらは開発中のダミーレスポンスです。実際のDify APIを統合すると、じょぎに関する詳しい情報をお答えできます。\n\n気軽に他の質問もしてくださいね！`;
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId] = useState<string>(() => uuidv4());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const { mutate, isPending } = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (responseContent) => {
      const assistantMessage: Message = {
        id: uuidv4(),
        role: "assistant",
        content: responseContent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
    onError: () => {
      const errorMessage: Message = {
        id: uuidv4(),
        role: "assistant",
        content: "申し訳ございません。エラーが発生しました。もう一度お試しください。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    },
  });

  const handleSendMessage = (content: string) => {
    // 送信中の場合は再入を防ぐ
    if (isPending) {
      return;
    }

    // 空白のみの入力を防ぐ
    const trimmed = content.trim();
    if (!trimmed) {
      return;
    }

    // ユーザーメッセージを追加
    const userMessage: Message = {
      id: uuidv4(),
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    mutate(trimmed);
  };

  return (
    <div className="flex h-screen max-h-screen flex-col bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* ヘッダー */}
      <ChatHeader messagesCount={messages.length} />

      {/* メッセージエリア */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="mx-auto max-w-4xl px-4 py-6">
            {messages.length === 0 ? (
              // 初期状態の表示
              <div className="flex h-full min-h-[50vh] flex-col items-center justify-center text-center">
                <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-xl">
                  <span className="text-5xl">🐰</span>
                </div>
                <h2 className="mb-3 text-2xl font-bold text-gray-900 dark:text-gray-100">
                  じょぎナビへようこそ！
                </h2>
                <p className="mb-6 max-w-md text-gray-600 dark:text-gray-400">
                  じょぎに関する質問に何でもお答えします。
                  <br />
                  活動内容、メンバー、イベントなど、気軽に聞いてくださいね！
                </p>
                <div className="grid max-w-2xl grid-cols-1 gap-3 md:grid-cols-2">
                  {[
                    "💡 じょぎってどんなサークル？",
                    "📅 活動はいつやっているの？",
                    "🎯 初心者でも参加できる？",
                    "💰 費用はどれくらいかかる？",
                  ].map((example, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(example.replace(/^[^\s]+ /, ""))}
                      disabled={isPending}
                      className="rounded-xl border border-gray-200 bg-white p-3 text-left text-sm transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // メッセージ一覧
              <>
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} sessionId={sessionId} />
                ))}
                {isPending && (
                  <div className="mb-4 flex items-center gap-3" role="status">
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-600 text-lg">
                      🐰
                    </div>
                    <div className="rounded-2xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
                      <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                      <span className="sr-only">応答生成中</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* 入力エリア */}
      <div className="border-t border-gray-200 bg-white/80 backdrop-blur-sm dark:border-gray-700 dark:bg-gray-900/80">
        <div className="mx-auto max-w-4xl px-4 py-4">
          <ChatInput onSend={handleSendMessage} isLoading={isPending} />
        </div>
      </div>
    </div>
  );
}
