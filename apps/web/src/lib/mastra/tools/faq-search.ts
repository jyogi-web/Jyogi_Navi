import { createTool } from "@mastra/core/tools";
import { ModelRouterEmbeddingModel } from "@mastra/core/llm";
import { connect } from "@tidbcloud/serverless";
import { z } from "zod";

const embedder = new ModelRouterEmbeddingModel("google/gemini-embedding-001");

function getDb() {
  return connect({
    host: process.env.TIDB_HOST,
    username: process.env.TIDB_USER,
    password: process.env.TIDB_PASSWORD,
    database: process.env.TIDB_DATABASE,
  });
}

export const faqSearchTool = createTool({
  id: "faq-search",
  description:
    "じょぎ（情報技術研究部）に関するFAQをベクトル検索で調べる。入部方法・活動内容・費用などの質問に使う。",
  inputSchema: z.object({
    query: z.string().describe("検索するキーワードや質問文"),
  }),
  outputSchema: z.object({
    results: z.array(z.string()).describe("関連するFAQの本文（最大3件）"),
  }),
  execute: async (inputData) => {
    // クエリをベクトル化
    const { embeddings } = await embedder.doEmbed({ values: [inputData.query] });
    const vectorStr = `[${embeddings[0].join(",")}]`;

    // TiDB でコサイン距離順に TOP 3 取得
    const db = getDb();
    const rows = await db.execute(
      `SELECT content
       FROM faq_embeddings
       WHERE content_type = 'manual'
       ORDER BY VEC_COSINE_DISTANCE(embedding, ?)
       LIMIT 3`,
      [vectorStr]
    );

    const results = (rows as Array<{ content: string }>).map((r) => r.content);
    return { results };
  },
});
