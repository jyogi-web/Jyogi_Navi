"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import type { FeedbackItem } from "@jyogi-navi/openapi/types";
import { fetchFeedbacks } from "@/lib/api";

function RatingBadge({ rating }: { rating: FeedbackItem["rating"] }) {
  if (rating === "good") {
    return <span className="text-lg" title="良い">👍</span>;
  }
  return <span className="text-lg" title="悪い">👎</span>;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function FeedbacksPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin", "feedbacks"],
    queryFn: () => fetchFeedbacks(),
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">フィードバック一覧</h1>
          {data && (
            <p className="mt-1 text-sm text-gray-500">全 {data.total} 件</p>
          )}
        </div>
        <Link
          href="/dashboard"
          className="text-sm text-indigo-600 hover:text-indigo-800"
        >
          ← ダッシュボードに戻る
        </Link>
      </div>

      {isError && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
          データの取得に失敗しました。APIサーバーの接続を確認してください。
        </div>
      )}

      {isLoading && (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-14 animate-pulse rounded-lg bg-gray-100" />
          ))}
        </div>
      )}

      {data && data.feedbacks.length === 0 && (
        <p className="text-center text-gray-500 py-12">フィードバックはまだありません。</p>
      )}

      {data && data.feedbacks.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">評価</th>
                <th className="px-4 py-3">コメント</th>
                <th className="px-4 py-3">セッション ID</th>
                <th className="px-4 py-3">日時</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.feedbacks.map((fb) => (
                <tr key={fb.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <RatingBadge rating={fb.rating} />
                  </td>
                  <td className="px-4 py-3 text-gray-700 max-w-xs truncate">
                    {fb.comment ?? <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-500">
                    {fb.session_id.slice(0, 8)}
                  </td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                    {formatDate(fb.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
