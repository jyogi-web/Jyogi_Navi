import { feedbackListApiAdminFeedbacksGet, adminStatsApiAdminStatsGet } from "@jyogi-navi/openapi/sdk";
import type { DailyCount, AdminStatsResponse, FeedbackListResponse } from "@jyogi-navi/openapi/types";


function generateMockStats(): AdminStatsResponse {
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
  const { data, error } = await feedbackListApiAdminFeedbacksGet({
    query: { limit, offset },
    credentials: "include",
    cache: "no-store",
  });
  if (error) throw new Error("Failed to fetch feedbacks");
  return data!;
}

export async function fetchAdminStats(): Promise<AdminStatsResponse> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    return generateMockStats();
  }
  const { data, error } = await adminStatsApiAdminStatsGet({
    credentials: "include",
    cache: "no-store",
  });
  if (error) throw new Error("Failed to fetch admin stats");
  return data!;
}
