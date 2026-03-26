"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAdminStats } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin", "stats"],
    queryFn: fetchAdminStats,
    refetchInterval: 5 * 60 * 1000,
  });

  return (
    <div className="min-h-screen bg-muted/40">
      <header className="border-b bg-background px-6 py-4">
        <h1 className="text-xl font-semibold">Jyogi Navi 管理ダッシュボード</h1>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 p-6">
        {isError && (
          <div className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            データの取得に失敗しました。APIサーバーの接続を確認してください。
          </div>
        )}

        {/* 総トークン消費量 */}
        <Card>
          <CardHeader>
            <CardTitle>総トークン消費量</CardTitle>
            <CardDescription>累計のトークン消費数</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-10 w-40 animate-pulse rounded bg-muted" />
            ) : (
              <p className="text-4xl font-bold tabular-nums">
                {data?.total_tokens.toLocaleString("ja-JP") ?? "—"}
                <span className="ml-2 text-lg font-normal text-muted-foreground">tokens</span>
              </p>
            )}
          </CardContent>
        </Card>

        {/* 👍率 */}
        <Card>
          <CardHeader>
            <CardTitle>👍 率</CardTitle>
            <CardDescription>フィードバックに占める「良い」の割合</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-10 w-40 animate-pulse rounded bg-muted" />
            ) : (
              <p className="text-4xl font-bold tabular-nums">
                {data?.good_rate != null ? `${data.good_rate.toFixed(1)}` : "—"}
                <span className="ml-2 text-lg font-normal text-muted-foreground">%</span>
              </p>
            )}
          </CardContent>
        </Card>

        {/* 日別質問数 */}
        <Card>
          <CardHeader>
            <CardTitle>日別質問数</CardTitle>
            <CardDescription>日ごとのusage_logsレコード数</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-8 animate-pulse rounded bg-muted" />
                ))}
              </div>
            ) : !data || data.daily_counts.length === 0 ? (
              <p className="text-sm text-muted-foreground">データがありません</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="pb-2 font-medium text-muted-foreground">日付</th>
                      <th className="pb-2 text-right font-medium text-muted-foreground">質問数</th>
                      <th className="pb-2 pl-4 font-medium text-muted-foreground">グラフ</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {(() => {
                      const maxCount = Math.max(...data.daily_counts.map((d) => d.count));
                      return data.daily_counts.map(({ date, count }) => {
                      const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                      return (
                        <tr key={date}>
                          <td className="py-2 font-mono text-xs">{date}</td>
                          <td className="py-2 text-right tabular-nums">{count.toLocaleString("ja-JP")}</td>
                          <td className="py-2 pl-4">
                            <div className="h-4 w-48 rounded bg-muted">
                              <div
                                className="h-4 rounded bg-primary"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </td>
                        </tr>
                      );
                    });
                    })()}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
