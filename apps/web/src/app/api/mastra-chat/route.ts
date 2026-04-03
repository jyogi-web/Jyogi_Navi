import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { connect } from "@tidbcloud/serverless";
import { randomUUID } from "node:crypto";
import { usakoAgent } from "@/lib/mastra/agents/usako";

const requestSchema = z.object({
  message: z.string().min(1),
  sessionId: z.string().uuid(),
});

function getDb() {
  return connect({
    host: process.env.TIDB_HOST,
    username: process.env.TIDB_USER,
    password: process.env.TIDB_PASSWORD,
    database: process.env.TIDB_DATABASE,
  });
}

async function saveUsageLog(sessionId: string, tokens: number, category: string) {
  const db = getDb();
  // セッションが存在しない場合は作成（ゲストセッション）
  await db.execute(
    `INSERT IGNORE INTO sessions (id, is_guest, consented) VALUES (?, TRUE, FALSE)`,
    [sessionId]
  );
  await db.execute(
    `INSERT INTO usage_logs (id, session_id, tokens, category) VALUES (?, ?, ?, ?)`,
    [randomUUID(), sessionId, tokens, category]
  );
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = requestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }

  const result = await usakoAgent.generate(parsed.data.message);
  const usage = result.usage;
  const tokens = (usage?.inputTokens ?? 0) + (usage?.outputTokens ?? 0);

  // レスポンスを先に返し、ログ書き込みはバックグラウンドで実行
  saveUsageLog(parsed.data.sessionId, tokens, "chat").catch(console.error);

  return NextResponse.json({ answer: result.text });
}
