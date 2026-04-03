import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { usakoAgent } from "@/lib/mastra/agents/usako";

const requestSchema = z.object({
  message: z.string().min(1),
  sessionId: z.string().uuid(),
});

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = requestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }

  const result = await usakoAgent.generate(parsed.data.message);

  return NextResponse.json({ answer: result.text });
}
