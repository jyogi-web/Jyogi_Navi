# schema-sync

バックエンドのAPI変更をフロントエンドの型に反映するスキル。

## いつ使うか

以下のいずれかの作業をしたら必ず実行する：

- `apps/api/` 配下のルーター・Pydanticモデルを追加・変更・削除した
- フロントエンドでバックエンドAPIの型が必要になった（まずこれを実行してから実装する）

## 手順

### 1. スキーマ生成

```bash
pnpm openapi
```

これ1コマンドで以下が連続実行される：
- `pnpm --filter api openapi:export` → `apps/api/openapi.json` を更新
- `pnpm --filter web openapi:generate` → `packages/openapi/src/client/` 配下を更新

### 2. 生成物の確認

```bash
git diff packages/openapi/src/client/
```

追加・変更されたエンドポイントの型が反映されているか確認する。

### 3. フロントエンドでのimport

生成された型・関数は `packages/openapi/src/client/` からimportする：

```ts
// API型
import type { ChatRequest, ChatResponse } from "@/client";

// SDK関数（直接呼び出し）
import { chatApiChatPost } from "@/client";

// TanStack Query（推奨）
import { chatApiChatPostMutation } from "@/client";
import { useMutation } from "@tanstack/react-query";

const mutation = useMutation(chatApiChatPostMutation());
```

### 4. コミット対象

以下は**必ずコミットに含める**：

- `apps/api/openapi.json`
- `packages/openapi/src/client/` 配下の全ファイル

CIがスキーマドリフトを検知するため、コミット漏れがあるとPRのCIが失敗する。

## NG例

```ts
// ❌ 手書き型定義（絶対にやらない）
type ChatResponse = {
  answer: string;
  sources: string[];
};

// ✅ 生成型を使う
import type { ChatResponse } from "@/client";
```
