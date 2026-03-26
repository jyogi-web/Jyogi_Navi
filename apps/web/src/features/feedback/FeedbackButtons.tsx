"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { createFeedbackApiFeedbackPost } from "@jyogi-navi/openapi/sdk";
import { cn } from "@/lib/utils";

interface FeedbackButtonsProps {
  sessionId: string;
}

export function FeedbackButtons({ sessionId }: FeedbackButtonsProps) {
  const [selected, setSelected] = useState<"good" | "bad" | null>(null);

  const { mutate } = useMutation({
    mutationFn: (rating: "good" | "bad") =>
      createFeedbackApiFeedbackPost({
        body: { session_id: sessionId, rating },
      }),
  });

  const handleClick = (rating: "good" | "bad") => {
    if (selected === rating) {
      // TODO: 選択解除時のサーバー同期（DELETE or UPDATE with null rating）
      // 対応には feedback DELETE API エンドポイントの実装が必要
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
