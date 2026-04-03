# 11_mastra-poc-result

作成日時: 2026年4月3日
作成者: アリス

# Mastra SDK 移行検証（PoC）結果レポート

---

## 0️⃣ サマリー

| 項目 | 結果 |
|---|---|
| 検証期間 | 2026年4月1日 〜 2026年4月3日（約2日） |
| 検証ブランチ | `Alice/front-end` |
| 最終判定 | **⚠️ 条件付き Go（Cloudflare 本番デプロイ検証が残り）** |

Phase 1〜3 のローカル検証はすべて完了。  
Cloudflare Pages 本番環境での動作確認（Phase 3 最終ステップ）が **未完了**。

---

## 1️⃣ 検証結果サマリー

| Phase | 内容 | 結果 | 備考 |
|---|---|---|---|
| Phase 1 | 基礎セットアップ・型安全 API | ✅ 完了 | ローカル curl で JSON レスポンス確認済み |
| Phase 2 | RAG（TiDB ベクトル検索） | ✅ 完了 | ローカル curl で正確な回答を確認済み |
| Phase 3 | usage_logs 書き込み | ✅ 完了（ローカル） | TiDB で 587 tokens の記録を確認済み |
| Phase 3 | Cloudflare Pages 本番デプロイ | ❌ **未完了** | 環境変数設定 + `pnpm deploy` が残っている |

---

## 2️⃣ 検証手順（詳細）

### Phase 1: 基礎セットアップ・型安全 API

#### やったこと

1. `apps/web` に `@mastra/core@1.20.0` をインストール
2. `apps/web/src/lib/mastra/agents/usako.ts` を作成
3. `apps/web/src/app/api/mastra-chat/route.ts` を作成（Next.js App Router API Route）

#### ハマったこと・修正内容

| 問題 | 原因 | 解決策 |
|---|---|---|
| TypeScript エラー「id は必須」 | `Agent` コンストラクタに `id` フィールドが必要 | `id: 'usako'` を追加 |
| import エラー | `@mastra/core` ではなく `@mastra/core/agent` が正しい | import パスを修正 |
| `structuredOutput` でエラー | Gemini は function calling と JSON response mime type の同時使用不可 | `structuredOutput` を削除。`result.text` を返す形に変更 |
| UUID バリデーション失敗 | `00000000-...` 形式は UUID v4 として無効 | `123e4567-e89b-12d3-a456-426614174000` 形式を使用 |

#### 確認コマンドと結果

```bash
curl -X POST http://localhost:3000/api/mastra-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "じょぎって何するところ？", "sessionId": "123e4567-e89b-12d3-a456-426614174000"}'

# => {"answer":"じょぎはWeb開発、アプリ開発、競技プログラミングなど...","category":"活動内容"}
```

---

### Phase 2: RAG（TiDB ベクトル検索）

#### やったこと

1. `apps/web/src/lib/mastra/tools/faq-search.ts` を作成
   - `ModelRouterEmbeddingModel('google/gemini-embedding-001')` でクエリをベクトル化（3072次元）
   - TiDB に `VEC_COSINE_DISTANCE` でコサイン距離検索、TOP 3 取得
2. TiDB に `faq_embeddings` テーブルの `embedding` カラムを `VECTOR(3072)` で再構築
3. TiFlash レプリカを有効化（ベクトルインデックスの必須要件）
4. `apps/web/scripts/seed-faq.ts` を作成し、8件のFAQデータを投入

#### ハマったこと・修正内容

| 問題 | 原因 | 解決策 |
|---|---|---|
| ベクトル次元数ミスマッチ | `VECTOR(768)` で作ったが `gemini-embedding-001` は 3072 次元 | カラムを DROP → `VECTOR(3072)` で再作成 |
| `CREATE VECTOR INDEX` 失敗 | TiFlash レプリカなしではベクトルインデックス作成不可 | `ALTER TABLE faq_embeddings SET TIFLASH REPLICA 1;` を実行。`AVAILABLE=1` になるまで待機 |
| `execute` 引数の型エラー | Mastra 1.20.0 の `createTool` は `execute` の引数が `{ context }` ではなく直接 `inputData` | `execute: async (inputData) =>` に修正 |
| Discordデータが検索結果に混入 | 既存の Discord ingestion データが `faq_embeddings` に入っていた | `WHERE content_type = 'manual'` フィルタを追加 |
| `npx tsx` が見つからない | nix 環境でのパス問題 | `pnpm exec tsx` を使用 |

#### TiDB 側の事前設定手順（重要）

```sql
-- 1. カラム再作成
ALTER TABLE faq_embeddings MODIFY COLUMN embedding VECTOR(3072);

-- 2. TiFlash レプリカ有効化
ALTER TABLE faq_embeddings SET TIFLASH REPLICA 1;

-- 3. 有効化を確認（AVAILABLE = 1 になるまで待つ）
SELECT TABLE_NAME, REPLICA_COUNT, AVAILABLE
FROM information_schema.tiflash_replica
WHERE TABLE_NAME = 'faq_embeddings';

-- 4. ベクトルインデックス作成
ALTER TABLE faq_embeddings
  ADD VECTOR INDEX idx_faq_embedding ((VEC_COSINE_DISTANCE(embedding)))
  USING HNSW;
```

#### シードデータ投入

```bash
cd apps/web && pnpm exec tsx scripts/seed-faq.ts
# => 8 件のFAQデータを投入しました。
```

#### 確認コマンドと結果

```bash
curl -X POST http://localhost:3000/api/mastra-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "活動日はいつ？", "sessionId": "123e4567-e89b-12d3-a456-426614174000"}'

# => {"answer":"じょぎの活動日は、通常は週2回、火曜日と木曜日の放課後だよ！活動場所は情報棟3階の部室です。..."}
```

サーバーログで `faq-search` ツールが呼ばれ、3件の FAQが取得されたことを確認。

---

### Phase 3: usage_logs 書き込み（ローカル検証済み）

#### やったこと

`apps/web/src/app/api/mastra-chat/route.ts` に以下を追加:
- `saveUsageLog()` 関数: `sessions` テーブルに `INSERT IGNORE`（FK制約対策）→ `usage_logs` に INSERT
- fire-and-forget パターン（`.catch(console.error)`）でレスポンスをブロックしない

#### ハマったこと・修正内容

| 問題 | 原因 | 解決策 |
|---|---|---|
| FK 制約エラー | `usage_logs.session_id → sessions.id` の外部キー制約 | `sessions` への `INSERT IGNORE` を先に実行 |
| `await result.usage` で TypeScript 警告 | `result.usage` は Promise ではなく直接アクセス可能 | `await` を削除 |

#### TiDB で確認した結果

```sql
SELECT * FROM usage_logs ORDER BY created_at DESC LIMIT 5;
-- id: xxx, session_id: 123e4567-..., tokens: 587, category: chat
```

トークン数（inputTokens + outputTokens = 587）が正しく記録されていることを確認。

---

## 3️⃣ 未検証項目

### ❌ Cloudflare Pages 本番デプロイ（最重要・未実施）

**残りの手順:**

1. Cloudflare Dashboard → Pages → `jyogi-navi-web` → Settings → Environment variables に以下を追加:
   ```
   GOOGLE_GENERATIVE_AI_API_KEY=...
   TIDB_HOST=...
   TIDB_USER=...
   TIDB_PASSWORD=...
   TIDB_DATABASE=...
   ```

2. デプロイ実行:
   ```bash
   cd apps/web && pnpm deploy
   ```

3. 本番 URL で curl して動作確認

4. TiDB で本番からの `usage_logs` レコードが記録されているか確認

**PoC 計画書の Exit Criteria「Cloudflare Pages 上でエラーを起こさずに完走すること」はまだ満たせていない。**

### その他 未検証の領域

| 項目 | 状況 | 補足 |
|---|---|---|
| レスポンス速度（10秒以内） | 未計測 | ローカルで体感 2〜5秒程度だが正確な計測なし |
| Gemini API コスト | 未計算 | 現行 Dify との比較なし |
| RAG 精度の定量評価 | 未実施 | 目視確認のみ |
| 同時リクエスト時の動作 | 未検証 | Cloudflare の Edge 環境でのキューイング挙動不明 |
| チームメンバーの DX 評価 | 未実施 | 「フロント側で型が効いて開発しやすいか」の合意未取得 |
| PII マスキング | 未実装 | ユーザー入力のリアルタイム PII 除去は未対応（現行 Dify も同様） |

---

## 4️⃣ 技術的な知見・制約のまとめ

### Mastra SDK (`@mastra/core` v1.20.0) で確認した制約

| 制約 | 内容 |
|---|---|
| Gemini × structuredOutput × tools | **同時使用不可**。function calling と `application/json` response mime type は排他的。tools を使う場合は `result.text` を返すしかない |
| `ModelRouterEmbeddingModel` の次元数 | `google/gemini-embedding-001` は 3072 次元。768 次元の既存カラムとは互換なし |
| `createTool` の execute 引数 | v1.20.0 では `{ context }` ではなく引数直接（`inputData`）でアクセス |
| Cloudflare Workers 対応 | `@tidbcloud/serverless`（HTTP ドライバ）が必須。TCP ソケット（`mysql2` 等）は不可 |

### TiDB Serverless で確認した制約

| 制約 | 内容 |
|---|---|
| TiFlash レプリカ必須 | ベクトルインデックス（HNSW）の作成には TiFlash レプリカの有効化が前提 |
| AVAILABLE=1 待機 | `SET TIFLASH REPLICA 1` 後、すぐにはインデックスが使えない |

---

## 5️⃣ 結論：Dify → Mastra SDK への移行判断

### Go / No-Go 評価

| 評価項目（PoC 計画書より） | 必須条件 | 現状 |
|---|---|---|
| 開発体験 (DX) | 型安全 API でチームが合意 | ⚠️ 技術的には動作確認済みだが、チームの合意未取得 |
| RAG 精度 | Dify と同等以上の回答精度 | ✅ ローカルで確認。`content_type = 'manual'` フィルタで精度を担保 |
| インフラ制約 | Cloudflare Pages でエラーなし | ❌ **本番デプロイ未実施** |
| 運用要件 | usage_logs への非同期書き込み | ✅ ローカルで確認済み |

### 移行するべきか？

**現時点では「本番デプロイ確認後に判断」が正確な回答。ただし技術的な懸念はほぼ解消されており、Go になる可能性が高い。**

#### Mastra SDK への移行メリット

1. **Dify 自宅 PC 依存からの脱却**  
   現行の最大リスク（担当者が離脱すると運用停止）を解消できる。Mastra は Cloudflare Pages に統合できる。

2. **プロンプトの Git 管理**  
   `agents/usako.ts` として TypeScript で記述するため、変更履歴・レビューが可能になる。Dify の GUI 設定は Git 管理できない。

3. **型安全の完結**  
   現行は Dify Chat API → FastAPI → Next.js という経路で型変換が発生。Mastra なら Next.js 内で完結し、Zod スキーマが直接効く。

4. **インフラの統合・シンプル化**  
   Dify（自宅PC）+ Cloudflare Tunnel + FastAPI（Cloud Run）の複雑な構成を、Cloudflare Pages 単体に集約できる。

5. **コスト 0 円継続**  
   `@tidbcloud/serverless` + Gemini API（無料枠）の組み合わせで、現行と同等のコストで動作する見込み。

#### Mastra SDK への移行デメリット・残リスク

1. **Cloudflare 本番での動作が未確認**  
   Edge ランタイム固有のタイムアウト・未対応モジュールのリスクがゼロではない。

2. **RAG 精度の定量評価が未実施**  
   現行 Dify との比較テストが行われていない。「体感で同等」は根拠として弱い。

3. **Gemini の `structuredOutput` が使えない**  
   tools 利用時に JSON スキーマ強制ができないため、レスポンス形式の一貫性が LLM の気分に依存する部分がある。

4. **ライブラリが比較的新しい**  
   `@mastra/core` は v1.x。API が今後変わる可能性があり、長期メンテコストは未知数。

#### 推奨アクション

```
1. [今すぐ] Cloudflare Pages に環境変数を設定して pnpm deploy を実行
2. [デプロイ後] 本番 URL で curl して動作確認 → usage_logs に記録されているか TiDB で確認
3. [確認できたら] チームに Draft PR を出し、DX 評価の合意を取る
4. [合意後] Dify 依存のコード（FastAPI の /chat エンドポイント等）を段階的に削除
```

Cloudflare 本番でエラーが出なければ、移行する技術的な根拠は十分に揃っている。

---

## 6️⃣ 実装ファイル一覧

| ファイル | 操作 | 状態 |
|---|---|---|
| `apps/web/src/lib/mastra/agents/usako.ts` | 新規作成 | ✅ 動作確認済み |
| `apps/web/src/lib/mastra/tools/faq-search.ts` | 新規作成 | ✅ 動作確認済み |
| `apps/web/src/app/api/mastra-chat/route.ts` | 新規作成 | ✅ 動作確認済み |
| `apps/web/scripts/seed-faq.ts` | 新規作成 | ✅ 投入済み（8件） |
| `apps/web/package.json` | `@mastra/core` を追加 | ✅ |
