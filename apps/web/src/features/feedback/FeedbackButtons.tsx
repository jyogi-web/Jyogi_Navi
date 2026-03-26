"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { createFeedbackFeedbackPost } from "@/client/sdk.gen";
import { cn } from "@/lib/utils";

interface FeedbackButtonsProps {
  sessionId: string;
  messageId: string;
}

export function FeedbackButtons({ sessionId, messageId: _messageId }: FeedbackButtonsProps) {
  const [selected, setSelected] = useState<"good" | "bad" | null>(null);

  const { mutate } = useMutation({
    mutationFn: (rating: "good" | "bad") =>
      createFeedbackFeedbackPost({
        body: { session_id: sessionId, rating },
      }),
  });

  const handleClick = (rating: "good" | "bad") => {
    if (selected === rating) {
      setSelected(null);
    } else {
      setSelected(rating);
      mutate(rating);
    }
  };

  return (
    <div className="mt-1.5 flex items-center gap-1">
      <button
        aria-label="good"
        data-selected={selected === "good"}
        onClick={() => handleClick("good")}
        className={cn(
          "rounded p-1 transition-colors",
          selected === "good"
            ? "text-blue-500"
            : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        )}
      >
        <ThumbsUp className="h-4 w-4" />
      </button>
      <button
        aria-label="bad"
        data-selected={selected === "bad"}
        onClick={() => handleClick("bad")}
        className={cn(
          "rounded p-1 transition-colors",
          selected === "bad"
            ? "text-red-500"
            : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        )}
      >
        <ThumbsDown className="h-4 w-4" />
      </button>
    </div>
  );
}
