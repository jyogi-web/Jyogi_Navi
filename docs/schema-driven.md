# スキーマ駆動開発フロー

FastAPIのPydanticモデルからOpenAPIスキーマを生成し、TypeScript APIクライアントを自動生成する仕組みの説明。

## 概要

バックエンドの変更が即座にフロントエンドの型エラーとして検知されるDXを実現する。

```
apps/api (FastAPI)
  └─ openapi.json  ←  pnpm export-openapi で生成
        ↓
apps/web/src/client/  ← pnpm generate:api で生成
  ├─ types.gen.ts
  ├─ schemas.gen.ts
  ├─ sdk.gen.ts
  └─ client.gen.ts
```

## 使用ツール

- **[`@hey-api/openapi-ts`](https://heyapi.dev/)** v0.94.2
  - TanStack Query v5の`queryOptions`パターン準拠
  - プラグインアーキテクチャで必要な機能だけ選択可能
  - Zodプラグインでプロジェクト既存のZodと統合

## コマンド

### ローカル開発

```bash
# OpenAPIスキーマを生成（apps/api/openapi.json に出力）
pnpm --filter api export-openapi

# TypeScript APIクライアントを生成（apps/web/src/client/ に出力）
pnpm --filter web generate:api

# 上記を一気通貫で実行（ルートから）
pnpm generate
```

### 生成物の確認

```bash
# 生成されたファイルを確認
ls apps/web/src/client/
```

## 運用方針

**ローカルで生成物をコミット → CIで再生成して差分チェック**

1. バックエンドのモデル・ルーターを変更したら `pnpm generate` を実行
2. 生成された `apps/api/openapi.json` と `apps/web/src/client/` をコミット
3. PRを作成するとCIが再生成して差分をチェック
4. 差分があればCI失敗 → コミットし忘れを検知

## ファイル構成

| ファイル | 説明 |
|---|---|
| `apps/api/scripts/export_openapi.py` | OpenAPIスキーマ出力スクリプト |
| `apps/api/openapi.json` | 生成されたOpenAPIスキーマ（コミット対象） |
| `apps/web/openapi-ts.config.ts` | hey-api設定ファイル |
| `apps/web/src/client/` | 生成されたAPIクライアント（コミット対象） |
| `.github/workflows/check-openapi.yml` | スキーマドリフト検知CI |

## APIクライアントの使い方

### セットアップ

`apps/web/src/lib/api.ts` でクライアントの設定を行っている。
アプリケーションのエントリーポイントでインポートしてbaseUrlを設定する。

```ts
import "@/lib/api";
```

### 生成されたSDKの利用例

```ts
import { getHealth } from "@/client/sdk.gen";
import { useQuery } from "@tanstack/react-query";
import { healthCheckOptions } from "@/client/sdk.gen";  // TanStack Query対応の場合

// 直接呼び出し
const response = await getHealth();

// TanStack Query経由
const { data } = useQuery(healthCheckOptions());
```

## 注意事項

- `@hey-api/openapi-ts` はv0.x台のためAPIの破壊的変更リスクあり。`pnpm-lock.yaml` でバージョン固定して対応。
- バージョンアップ時は[CHANGELOGを確認](https://github.com/hey-api/openapi-ts/blob/main/CHANGELOG.md)すること。
