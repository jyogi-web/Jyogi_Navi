/**
 * faq_embeddings テーブルにテストデータを投入するスクリプト
 *
 * 実行方法:
 *   cd apps/web && npx tsx scripts/seed-faq.ts
 *
 * 必要な環境変数 (.env.local):
 *   GOOGLE_GENERATIVE_AI_API_KEY
 *   TIDB_HOST, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE
 */

import { config } from "dotenv";
import path from "path";

// .env.local を読み込む
config({ path: path.resolve(process.cwd(), ".env.local") });

import { connect } from "@tidbcloud/serverless";
import { ModelRouterEmbeddingModel } from "@mastra/core/llm";
import { randomUUID } from "node:crypto";

const faqs = [
  {
    content:
      "じょぎ（情報技術研究部）への入部方法は？毎年4月に新歓イベントを開催しています。部室に遊びに来るか、SNSのDMで連絡してください。入部届は部室でもらえます。",
    content_type: "manual",
  },
  {
    content:
      "活動日はいつですか？通常は週2回、火曜日と木曜日の放課後に活動しています。活動場所は情報棟3階の部室です。",
    content_type: "manual",
  },
  {
    content:
      "じょぎではどんな活動をしていますか？Web開発、アプリ開発、競技プログラミング、ゲーム開発、AI・機械学習など、ITに関する幅広い活動をしています。各自が興味のある分野を自由に取り組めます。",
    content_type: "manual",
  },
  {
    content: "部費はいくらですか？年間の部費は3000円です。新入生は入部後に部室で徴収します。",
    content_type: "manual",
  },
  {
    content:
      "プログラミング初心者でも入部できますか？もちろん大歓迎です！初心者向けの勉強会も定期的に開催しています。入部時点でのプログラミング経験は問いません。",
    content_type: "manual",
  },
  {
    content:
      "部員は何人いますか？現在は約30名が在籍しています。1年生から4年生まで幅広い学年のメンバーがいます。",
    content_type: "manual",
  },
  {
    content:
      "じょぎの部室はどこにありますか？情報棟3階の308号室が部室です。新歓期間中は毎日開放しています。",
    content_type: "manual",
  },
  {
    content:
      "文化祭や学祭での活動はありますか？はい、毎年学祭でゲームやWebアプリの展示・体験コーナーを出展しています。部員が作った作品を一般公開します。",
    content_type: "manual",
  },
];

async function main() {
  console.log("🚀 FAQ シードデータの投入を開始します...\n");

  // Embedding モデルの初期化
  const embedder = new ModelRouterEmbeddingModel("google/gemini-embedding-001");

  // TiDB 接続
  const db = connect({
    host: process.env.TIDB_HOST,
    username: process.env.TIDB_USER,
    password: process.env.TIDB_PASSWORD,
    database: process.env.TIDB_DATABASE,
  });

  for (const faq of faqs) {
    process.stdout.write(`  ベクトル化中: "${faq.content.slice(0, 30)}..." `);

    // ベクトル化
    const { embeddings } = await embedder.doEmbed({ values: [faq.content] });
    const vector = embeddings[0];
    const vectorStr = `[${vector.join(",")}]`;

    // INSERT
    const id = randomUUID();
    await db.execute(
      `INSERT INTO faq_embeddings (id, content, content_type, embedding)
       VALUES (?, ?, ?, ?)`,
      [id, faq.content, faq.content_type, vectorStr]
    );

    console.log("✅");
  }

  console.log(`\n✨ ${faqs.length} 件のFAQデータを投入しました。`);
}

main().catch((err) => {
  console.error("❌ エラーが発生しました:", err);
  process.exit(1);
});
