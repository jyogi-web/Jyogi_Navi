# 03_screen-flow

作成日時: 2026年3月1日 17:45
最終更新日時: 2026年3月1日 17:45
最終更新者: iseebi

# 🖥️ screen-flow.md テンプレート

---

# 0️⃣ 設計前提

| 項目 | 内容 |
| --- | --- |
| 対象ユーザー | **新入生（匿名）** / **部員（運用者）** |
| デバイス | Mobile / Desktop（Responsive） |
| 認証要否 | 新入生：不要（公開） / 管理：P1でDiscord OAuth |
| 権限制御 | P1：RBAC（部員ロール） |
| MVP範囲 | **P0：新入生チャット（オプトイン＋評価）**（管理画面はP1） |

---

# 1️⃣ 画面一覧（Screen Inventory）

| ID | 画面名 | 役割 | 認証 | 優先度 |
| --- | --- | --- | --- | --- |
| S-01 | ランディング | 入口 | 不要 | P0 |
| S-02 | ログイン | 認証 | 不要 | P0 |
| S-03 | ダッシュボード | 中核画面 | 必須 | P0 |
| S-04 | 一覧画面 | リソース一覧 | 必須 | P0 |
| S-05 | 詳細画面 | 個別閲覧 | 必須 | P0 |
| S-06 | 作成/編集画面 | データ変更 | 必須 | P0 |
| S-07 | 設定画面 | ユーザー設定 | 必須 | P1 |
| S-08 | 通知一覧 | 通知確認 | 必須 | P1 |
| S-09 | 管理画面 | 管理者専用 | 管理者 | P2 |

---

# 2️⃣ 全体遷移図（高レベル）

### 図1：システムアーキテクチャ図

```mermaid
graph TB
    A[新入生<br/>Webブラウザ] --> B[フロントエンド]
    B --> C[チャットUI]
    B --> D[VRM表示<br/>顔認識・目線追従]
    C --> E[バックエンドAPI]
    E --> F[RAGシステム]
    F --> G[Embedding処理]
    F --> H[ベクトルDB<br/>Pinecone/Chroma]
    F --> I[LLM<br/>OpenAI or Qwen]
    H --> J[データソース]
    J --> K[Discord<br/>ログ]
    J --> L[Notion<br/>資料]
    J --> M[GoogleDrive<br/>活動記録]
    E --> N[個人情報フィルタ]
    E --> O[会話ログ保存<br/>オプトイン]
```

### 図2：RAG処理フロー図

```mermaid
sequenceDiagram
    participant User as 新入生
    participant UI as チャットUI
    participant API as バックエンドAPI
    participant Embed as Embedding
    participant VDB as ベクトルDB
    participant LLM as LLM

    User->>UI: 質問入力
    UI->>API: 質問送信
    API->>Embed: テキストをベクトル化
    Embed->>VDB: 類似ベクトル検索
    VDB-->>API: 関連情報取得
    API->>LLM: プロンプト生成<br/>(質問+関連情報)
    LLM-->>API: 回答生成
    API->>API: 個人情報フィルタ
    API-->>UI: 回答返却
    UI-->>User: 回答表示 + うさこアニメーション
```

---

# 3️⃣ 認証フロー

```mermaid
flowchart LR
    Public[Public Page]
    AuthCheck{Authenticated?}
    Login[Login]
    App[App Home]

    Public --> AuthCheck
    AuthCheck -- No --> Login
    AuthCheck -- Yes --> App
    Login --> App
```

---

# 4️⃣ CRUD標準遷移テンプレ

```mermaid
flowchart LR
    List --> Detail
    Detail --> Edit
    List --> Create
    Edit --> Detail
    Create --> Detail
```

---

# 5️⃣ 状態別分岐（State-based Flow）

```mermaid
flowchart TD
    Detail --> StatusCheck{Status?}
    StatusCheck -->|Draft| Edit
    StatusCheck -->|Active| ViewOnly
    StatusCheck -->|Archived| ReadOnly
```

---

# 6️⃣ 権限別分岐（RBAC/ABAC）

```mermaid
flowchart TD
    Detail --> RoleCheck{User Role}
    RoleCheck -->|Viewer| ReadOnly
    RoleCheck -->|Editor| Edit
    RoleCheck -->|Admin| AdminPanel
```

---

# 7️⃣ モーダル・非同期操作

```mermaid
flowchart LR
    Detail --> ConfirmModal
    ConfirmModal -->|Cancel| Detail
    ConfirmModal -->|Confirm| Action
    Action --> ResultToast
```

---

# 8️⃣ エラーフロー

```mermaid
flowchart TD
    Submit --> API
    API -->|Success| SuccessState
    API -->|ValidationError| ShowFormError
    API -->|Unauthorized| RedirectLogin
    API -->|ServerError| ErrorPage
```

---

# 9️⃣ 空状態 / 初回体験

```mermaid
flowchart TD
    Dashboard --> HasData{Data exists?}
    HasData -->|No| Onboarding
    HasData -->|Yes| NormalView
```

---

# 🔟 モバイル考慮（任意）

| 項目 | Desktop | Mobile |
| --- | --- | --- |
| ナビゲーション | Sidebar | Bottom Nav |
| 詳細表示 | 2カラム | 1カラム |
| 編集 | ページ遷移 | フルスクリーン |

---

# 1⃣1⃣ URL設計テンプレ

```
/login
/dashboard
/entities
/entities/:id
/entities/:id/edit
/settings
/admin
```