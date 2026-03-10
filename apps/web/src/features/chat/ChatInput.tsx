'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2 } from 'lucide-react';

const chatInputSchema = z.object({
  message: z
    .string()
    .min(1, '質問を入力してください')
    .max(500, '質問は500文字以内で入力してください'),
});

type ChatInputValues = z.infer<typeof chatInputSchema>;

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [isFocused, setIsFocused] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChatInputValues>({
    resolver: zodResolver(chatInputSchema),
  });

  const onSubmit = (data: ChatInputValues) => {
    onSend(data.message);
    reset();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enterキーで送信（Shift+Enterで改行）
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(onSubmit)();
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="w-full">
      <div
        className={`relative flex items-end gap-2 p-4 rounded-2xl border-2 transition-all duration-200 bg-white dark:bg-gray-800 ${
          isFocused
            ? 'border-blue-500 shadow-lg shadow-blue-500/20'
            : 'border-gray-200 dark:border-gray-700'
        }`}
      >
        {/* テキストエリア */}
        <div className="flex-1">
          <Textarea
            {...register('message')}
            placeholder="じょぎについて質問してください..."
            disabled={isLoading || disabled}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            className="min-h-[24px] max-h-[200px] resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 text-sm bg-transparent"
            rows={1}
          />
          {errors.message && (
            <p className="text-xs text-red-500 mt-1">{errors.message.message}</p>
          )}
        </div>

        {/* 送信ボタン */}
        <Button
          type="submit"
          size="icon"
          disabled={isLoading || disabled}
          className="h-10 w-10 rounded-xl flex-shrink-0 bg-gradient-to-br from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
          aria-label={isLoading ? 'メッセージを送信中' : 'メッセージを送信'}
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </div>

      {/* ヒント */}
      <div className="flex items-center justify-between mt-2 px-2">
        <p className="text-xs text-muted-foreground">
          {isLoading ? '回答を生成中...' : 'Enterで送信 / Shift+Enterで改行'}
        </p>
        <p className="text-xs text-muted-foreground">
          {/* 文字数カウントは後で追加可能 */}
        </p>
      </div>
    </form>
  );
}
