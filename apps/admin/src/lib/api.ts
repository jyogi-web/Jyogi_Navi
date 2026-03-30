import type { DailyCount, AdminStatsResponse, FeedbackItem, FeedbackListResponse } from "@jyogi-navi/openapi/types";

export type { DailyCount, FeedbackItem, FeedbackListResponse };
export type AdminStats = AdminStatsResponse;

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

function generateMockStats(): AdminStats {
  const days: DailyCount[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const day = d.toISOString().slice(0, 10);
    days.push({ date: day, count: Math.floor(Math.random() * 40) + 1 });
  }
  const total_tokens = days.reduce((sum, d) => sum + d.count * 800, 0);
  return { daily_counts: days, total_tokens, good_rate: 0 };
}


export async function fetchFeedbacks(
  limit = 50,
  offset = 0,
): Promise<FeedbackListResponse> {
  const res = await fetch(
    `${API_BASE_URL}/api/admin/feedbacks?limit=${limit}&offset=${offset}`,
    { cache: "no-store", credentials: "include" },
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch feedbacks: ${res.status}`);
  }
  return res.json() as Promise<FeedbackListResponse>;
}

export async function fetchAdminStats(): Promise<AdminStats> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    return generateMockStats();
  }
  const res = await fetch(`${API_BASE_URL}/api/admin/stats`, {
    cache: "no-store",
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch admin stats: ${res.status}`);
  }
  return res.json() as Promise<AdminStats>;
}
