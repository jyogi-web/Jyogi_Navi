'use client';

import { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message } from '@/types/chat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatHeader } from './ChatHeader';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2 } from 'lucide-react';

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // 送信中の場合は再入を防ぐ
    if (isLoading) {
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
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // TODO: 実際のDify API呼び出しに置き換える
      // 現在はダミーレスポンス
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `ご質問ありがとうございます！「${trimmed}」についてですね。\n\nこちらは開発中のダミーレスポンスです。実際のDify APIを統合すると、じょぎに関する詳しい情報をお答えできます。\n\n気軽に他の質問もしてくださいね！`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // エラーメッセージを表示
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: '申し訳ございません。エラーが発生しました。もう一度お試しください。',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* ヘッダー */}
      <ChatHeader messagesCount={messages.length} />

      {/* メッセージエリア */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              // 初期状態の表示
              <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center">
                <div className="w-24 h-24 mb-6 bg-gradient-to-br from-purple-500 to-pink-600 rounded-3xl flex items-center justify-center shadow-xl">
                  <span className="text-5xl">🐰</span>
                </div>
                <h2 className="text-2xl font-bold mb-3 text-gray-900 dark:text-gray-100">
                  じょぎナビへようこそ！
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
                  じょぎに関する質問に何でもお答えします。
                  <br />
                  活動内容、メンバー、イベントなど、気軽に聞いてくださいね！
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                  {[
                    '💡 じょぎってどんなサークル？',
                    '📅 活動はいつやっているの？',
                    '🎯 初心者でも参加できる？',
                    '💰 費用はどれくらいかかる？',
                  ].map((example, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(example.replace(/^[^\s]+ /, ''))}
                      disabled={isLoading}
                      className="text-left p-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
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
                  <ChatMessage key={message.id} message={message} />
                ))}
                {isLoading && (
                  <div className="flex items-center gap-3 mb-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-lg">
                      🐰
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 border border-gray-200 dark:border-gray-700">
                      <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
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
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
