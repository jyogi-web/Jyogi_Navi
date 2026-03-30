# AGENTS.md

このリポジトリで作業する AI エージェントへの指示です。

## ドキュメントの参照

作業を開始する前に、必ず `docs/` ディレクトリ以下のドキュメントをすべて読んでください。

| ファイル | 内容 |
|---|---|
| `docs/01_feature-list.md` | 機能一覧 |
| `docs/02_tech-stack.md` | 技術スタック |
| `docs/03_screen-flow.md` | 画面フロー |
| `docs/04_permission-design.md` | 権限設計 |
| `docs/05_erd.md` | ER 図 |
| `docs/06_directory.md` | ディレクトリ構成 |
| `docs/07_infrastructure.md` | インフラ構成 |
| `docs/08_logging.md` | ログ設計 |
| `docs/09_schedule_and_issues.md` | スケジュールと課題 |
| `docs/iac.md` | IaC（Infrastructure as Code） |

これらのドキュメントはプロジェクトの仕様・設計の唯一の情報源です。実装方針や設計判断は必ずこれらのドキュメントに基づいてください。

## 型定義のルール

フロントエンド（`apps/admin` 等）で型を定義する際は、`packages/openapi` に同等の型が存在しないか必ず確認してください。

- バックエンドのレスポンス型は `@jyogi-navi/openapi/types` からインポートして使用する
- 独自に再定義しない（バックエンドとの乖離・二重管理を防ぐため）
- `packages/openapi` の型は `openapi-ts` でバックエンドの OpenAPI スキーマから自動生成される

```ts
// Good
import type { UserResponse, UserRole } from "@jyogi-navi/openapi/types";

// Bad
export type UserRole = "ADMIN" | "MEMBER"; // 再定義しない
```
