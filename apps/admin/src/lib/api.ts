import type { DailyCount, AdminStatsResponse } from "@jyogi-navi/openapi/types";

export type { DailyCount };
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

export async function fetchAdminStats(): Promise<AdminStats> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    return generateMockStats();
  }
  const res = await fetch(`${API_BASE_URL}/api/admin/stats`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch admin stats: ${res.status}`);
  }
  return res.json() as Promise<AdminStats>;
}
