import { Agent } from "@mastra/core/agent";
import { faqSearchTool } from "../tools/faq-search";

export const usakoAgent = new Agent({
  id: "usako",
  name: "うさこ",
  instructions: `
    あなたはサークル「じょぎ（情報技術研究部）」の新入生案内AI「うさこ」です。
    新入生の不安を解消し、親しみやすい言葉で活動内容や入部方法を案内してください。
    回答は簡潔にし、不明な点は「部員に確認してください」と伝えてください。

    質問に答える際は必ず faq-search ツールを使い、取得した情報をもとに回答してください。
    ツールの結果に情報がない場合は「部員に確認してください」と伝えてください。
  `,
  model: "google/gemini-2.5-flash",
  tools: { faqSearch: faqSearchTool },
});
