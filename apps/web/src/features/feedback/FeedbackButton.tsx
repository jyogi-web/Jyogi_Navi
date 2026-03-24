"use client";

import { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { sendFeedback } from "@/lib/api";
import { getOrCreateSessionId } from "@/lib/session";

interface FeedbackButtonProps {
  messageId: string;
}

export function FeedbackButton({ messageId }: FeedbackButtonProps) {
  const [voted, setVoted] = useState<boolean | null>(null);

  const handleVote = async (rating: boolean) => {
    if (voted !== null) return;
    setVoted(rating);
    const sessionId = getOrCreateSessionId();
    await sendFeedback(sessionId, messageId, rating);
  };

  return (
    <div className="mt-2 flex items-center gap-1">
      <button
        onClick={() => handleVote(true)}
        disabled={voted !== null}
        aria-label="役に立った"
        className={cn(
          "rounded-md p-1 transition-colors",
          voted === true
            ? "text-blue-500"
            : "text-gray-400 hover:text-blue-500 disabled:cursor-default"
        )}
      >
        <ThumbsUp className="h-4 w-4" />
      </button>
      <button
        onClick={() => handleVote(false)}
        disabled={voted !== null}
        aria-label="役に立たなかった"
        className={cn(
          "rounded-md p-1 transition-colors",
          voted === false
            ? "text-red-500"
            : "text-gray-400 hover:text-red-500 disabled:cursor-default"
        )}
      >
        <ThumbsDown className="h-4 w-4" />
      </button>
    </div>
  );
}
