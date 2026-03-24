# Discord ログ取り込み手順

JYOGIのDiscordメンバーチャンネルから直近3ヶ月分のログを取得し、Difyへ自動アップロードします。

## 対象チャンネル

| チャンネル名 | Channel ID |
|---|---|
| 雑談 | 1215894284428120170 |
| 何でも質問 | 1215901602456539146 |

## スクリプト構成

```
scripts/ingest/discord/
├── fetch.py         # Discord REST API からメッセージ取得
├── normalize.py     # 個人情報・ノイズ除去・Dify用フォーマット変換
├── upload_dify.py   # Dify ナレッジベースへアップロード
├── run.py           # パイプライン全体を実行するエントリーポイント
├── requirements.txt # Python 依存パッケージ
└── export.md        # このファイル
```

## 事前準備

### 1. Discord Bot の作成とトークン取得

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」でアプリを作成
3. 「Bot」タブ → 「Add Bot」
4. 「Privileged Gateway Intents」で **Message Content Intent** を有効化
5. 「Bot」タブ → 「Token」→「Reset Token」でトークンを取得
6. **絶対にトークンをリポジトリにコミットしないこと**

### 2. BotをサーバーにInvite

1. 「OAuth2」→「URL Generator」
2. Scopes: `bot` にチェック
3. Bot Permissions: `Read Message History`、`View Channels` にチェック
4. 生成されたURLでBotをJYOGI Discordサーバーに招待

### 3. Dify の情報を確認

| 項目 | 確認場所 |
|---|---|
| `DIFY_API_URL` | `infra/dify/.env` の `DIFY_API_URL` |
| `DIFY_API_KEY` | Dify 管理画面 → Knowledge → API キー |
| `DIFY_DATASET_ID` | Dify 管理画面 → Knowledge → 対象ナレッジベースのURL末尾のID |

## ローカル実行

```bash
cd scripts/ingest/discord
pip install -r requirements.txt

export DISCORD_BOT_TOKEN="your_bot_token"
export DISCORD_CHANNEL_IDS="1215894284428120170,1215901602456539146"
export DIFY_API_URL="https://your-dify-url"
export DIFY_API_KEY="your_dify_api_key"
export DIFY_DATASET_ID="your_dataset_id"

python run.py
```

## GitHub Actions による定期実行

`.github/workflows/discord-ingest.yml` で **毎週月曜 09:00 JST** に自動実行されます。

手動実行も可能です（Actions タブ →「Discord Log Ingest」→「Run workflow」）。

### GitHub Secrets の設定

リポジトリの「Settings → Secrets and variables → Actions」に以下を登録してください。

| Secret 名 | 値 |
|---|---|
| `DISCORD_BOT_TOKEN` | Discord Bot のトークン |
| `DISCORD_CHANNEL_IDS` | `1215894284428120170,1215901602456539146` |
| `DIFY_API_URL` | Dify の公開URL |
| `DIFY_API_KEY` | Dify Dataset API キー |
| `DIFY_DATASET_ID` | 対象ナレッジベースのID |

## 注意事項

- Botトークンは秘密情報です。`.env` ファイルや環境変数で管理し、絶対にリポジトリにコミットしないでください。
- 取り込み対象はJYOGIのメンバーチャンネルのみです。DM等は対象外です。
- チャンネルを追加する場合は、上記テーブルに追記し `DISCORD_CHANNEL_IDS` の Secret も更新してください。
