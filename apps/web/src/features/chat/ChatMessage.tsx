import { Message } from "@/types/chat";
import { cn } from "@/lib/utils";
import { FeedbackButtons } from "@/features/feedback";

interface ChatMessageProps {
  message: Message;
  sessionId: string;
}

export function ChatMessage({ message, sessionId }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "animate-in fade-in slide-in-from-bottom-2 mb-4 flex w-full duration-300",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "flex max-w-[85%] gap-3 md:max-w-[75%]",
          isUser ? "flex-row-reverse" : "flex-row"
        )}
      >
        {/* アバター */}
        <div
          className={cn(
            "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-lg",
            isUser
              ? "bg-gradient-to-br from-blue-500 to-indigo-600"
              : "bg-gradient-to-br from-purple-500 to-pink-600"
          )}
        >
          {isUser ? "👤" : "🐰"}
        </div>

        {/* メッセージバブル */}
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm",
            isUser
              ? "bg-gradient-to-br from-blue-500 to-indigo-600 text-white"
              : "border border-gray-200 bg-white text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          )}
        >
          <p className="text-sm leading-relaxed break-words whitespace-pre-wrap">
            {message.content}
          </p>
          <div
            className={cn(
              "mt-1.5 text-xs opacity-70",
              isUser ? "text-blue-100" : "text-gray-500 dark:text-gray-400"
            )}
          >
            {message.timestamp.toLocaleTimeString("ja-JP", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          {!isUser && <FeedbackButtons sessionId={sessionId} />}
        </div>
      </div>
    </div>
  );
}
