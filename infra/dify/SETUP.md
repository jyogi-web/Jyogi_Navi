# 🐳 Dify セットアップ & 運用ガイド

**最終更新日:** 2026年3月6日  
**対象フェーズ:** Sprint 0 (MVP基盤構築)

---

## 📋 目次

1. [前提条件](#前提条件)
2. [初回セットアップ](#初回セットアップ)
3. [起動・停止方法](#起動・停止方法)
4. [トラブルシューティング](#トラブルシューティング)
5. [運用時のチェックリスト](#運用時のチェックリスト)

---

## 前提条件

- Docker & Docker Compose インストール済み
  - `docker --version` と `docker-compose --version` で確認
- Docker Desktop / Docker Engine が起動しており、`/var/run/docker.sock` が利用可能
  - plugin runtime の起動に必要（Model Provider の資格情報検証で使用）
- **外部サービスアカウント作成済み:**
  - ✅ Supabase プロジェクト（PostgreSQL DB）
  - ✅ TiDB Serverless クラスター（Vector DB）
  - ✅ Upstash Redis インスタンス
  - ✅ Google Cloud API キー（Gemini）

### 使用イメージタグ（固定）

- `langgenius/dify-api:1.13.3`
- `langgenius/dify-web:1.13.3`

再現性のため `latest` は使いません。バージョン更新時は `infra/dify/docker-compose.yml` と本ドキュメントを同時更新してください。

> 💡 外部サービスの接続情報は [.env.example](./.env.example) を参照してください

---

## 初回セットアップ

### ステップ 1: 環境変数テンプレートをコピー

```bash
cd infra/dify

# テンプレートをコピー
cp .env.example .env
```

### ステップ 2: 環境変数を編集

```bash
# .env を開いて各キーを入力
nano .env  # または vim / VSCode で編集
```

**最小限必須の設定:**

```env
# Supabase DB (Dify内部DB)
SUPABASE_DB_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password
SUPABASE_DB_NAME=postgres

# TiDB Serverless (Vector DB)
TIDB_HOST=gateway01.us-west-2.prod.aws.tidbcloud.com
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DATABASE=dify

# Upstash Redis
UPSTASH_REDIS_URL=rediss://default:password@host:6379

# ローカルRedisを使う場合（UPSTASH_REDIS_URLを空のままにする）
REDIS_PASSWORD=set-a-strong-random-secret

# Google Gemini API
GOOGLE_API_KEY=AIzaSy...

# Secret keys（生成: python3 -c "import secrets; print(secrets.token_hex(32))"）
SECRET_KEY=your-random-string
DIFY_API_SECRET_KEY=your-api-secret-string

# Dify Web ポート（競合時は変更可）
DIFY_WEB_PORT=3101

# 永続ストレージ（private key を保持）
DIFY_STORAGE_PATH=./data/storage
DIFY_PLUGIN_STORAGE_PATH=./data/plugin-daemon-storage
STORAGE_LOCAL_PATH=/app/storage

# ローカルUIから API(5001) を叩くための CORS 許可
CORS_ORIGINS=http://127.0.0.1:3101
```

### ステップ 3: Secret Keys を生成（一度だけ）

```bash
# Python 3 で安全なランダム文字列生成
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('DIFY_API_SECRET_KEY=' + secrets.token_hex(32))"

# 出力をコピーして .env に貼り付け
```

### ステップ 4: 起動確認

```bash
# docker-compose のバージョン確認
docker-compose --version

# きちんと読み込まれるか確認（構文チェック）
docker-compose config > /dev/null && echo "✅ OK"
```

---

## 起動・停止方法

### 🚀 起動する

```bash
cd infra/dify

# ローカルRedisを使う場合（UPSTASH_REDIS_URL を未設定にする）
docker-compose up -d

# Upstash Redisを使う場合（UPSTASH_REDIS_URLを設定して起動）
docker-compose up -d

# ログをリアルタイム確認（オプション）
docker-compose logs -f

# または別のターミナルで
docker-compose logs -f dify-api    # API のみ監視
docker-compose logs -f dify-web    # Web UI のみ監視
```

### ✅ 起動確認

```bash
# コンテナが running 状態か確認
docker-compose ps

# 出力例:
# NAME                COMMAND                STATUS              PORTS
# dify-api            "python  -m dify...."  Up 2 minutes        0.0.0.0:5001->5001/tcp
# dify-web            "npm run start"        Up 2 minutes        0.0.0.0:3101->3000/tcp
# dify-worker         "python -m celery..."   Up 2 minutes        5001/tcp
# dify-worker-beat    "python -m celery..."   Up 2 minutes        5001/tcp
# dify-plugin-daemon  "./main"               Up 2 minutes        5002/tcp
# dify-redis          "redis-server..."      Up 2 minutes        0.0.0.0:6379->6379/tcp
# dify-sandbox        "./entrypoint.sh"      Up 2 minutes        8194/tcp
# dify-ssrf-proxy     "squid ..."            Up 2 minutes        3128/tcp
```

必須確認:
- `dify-worker` / `dify-worker-beat` が起動していること（非同期ジョブ）
- `dify-sandbox` / `dify-ssrf-proxy` が起動していること（ツール実行系）

### 🌐 Dify UI にアクセス

ブラウザで開く:
```text
http://127.0.0.1:3101
```

重要:
- `localhost` と `127.0.0.1` を混在させないでください（ログイン後に `apps` から `signin` へ戻る原因になります）。
- API/APP は両方とも `127.0.0.1` に統一してください。

初回アクセス時:
1. **セットアップウィザードが表示される**
2. 管理者アカウントを作成
3. **API キーやチャット API を生成**（Next.js から呼び出す際に必要）

### 🛑 停止する

```bash
# コンテナを停止（データは保持）
docker-compose down

# ボリュームも削除（完全リセット。非推奨）
# 注意: 過去の named volume 構成では private key も消えるため、
# provider credentials の復号に失敗して 500 が再発します。
docker-compose down -v
```

### 🔁 既存 named volume から bind mount への移行（初回のみ）

`PrivkeyNotFoundError` の再発防止のため、既存データを `./data/storage` へ退避してから再起動します。

```bash
cd infra/dify

# 1) バックアップ先ディレクトリ作成
mkdir -p ./data/storage ./data/plugin-daemon-storage

# 2) 旧 named volume からデータをコピー
docker run --rm -v dify_dify-storage:/from -v "$(pwd)/data/storage:/to" alpine sh -c "cp -a /from/. /to/"
docker run --rm -v dify_dify-plugin-daemon-storage:/from -v "$(pwd)/data/plugin-daemon-storage:/to" alpine sh -c "cp -a /from/. /to/"

# 3) 反映
docker-compose up -d --force-recreate
```

---

## トラブルシューティング

### 🔴 「Docker daemon is not running」

```bash
# Docker Desktop を起動してください（Windows/Mac）
# または Linux の場合:
sudo systemctl start docker
```

### 🔴 「Supabase DB 接続エラー」

症状: `dify-api` コンテナが起動失敗

原因チェック:
```bash
# 1. 環境変数が正しいか確認
cat .env | grep SUPABASE

# 2. DB に ping を打つ（Linux/Mac）
psql -h db.xxxxxxxxxxxxx.supabase.co -U postgres -d postgres -c "SELECT 1;"

# 3. ファイアウォール: Supabase Dashboard で IP ホワイトリスト確認
```

解決方法:
```bash
# ログ確認
docker-compose logs dify-api | tail -50

# 環境変数を修正
nano .env

# 再起動
docker-compose restart dify-api
```

### 🔴 「ベクトル検索エラー (TiDB)」

症状: Dify で「RAG 検索に失敗」

チェック:
```bash
# TiDB の接続文字列を確認
cat .env | grep TIDB

# TiDB Cloud Dashboard で接続状態を確認
# Settings > Connection Strings でホスト/ポート確認
```

解決方法:
```bash
# TiDB ホスト名の書き間違いなし か確認
# 例: gateway01.us-west-2.prod.aws.tidbcloud.com

# ファイアウォール確認: TiDB Desktop > Network ACL
# 自身の IP アドレスをホワイトリストに追加
```

### 🔴 「Redis 接続失敗」

症状: `CELERY_BROKER_URL connection refused`

チェック:
```bash
# Redis が起動しているか
docker-compose ps | grep redis

# Redis ポート確認
docker-compose exec dify-redis redis-cli ping
```

解決方法:
```bash
# Redis を再起動
docker-compose restart dify-redis

# または Upstash を使用していれば:
nano .env
# → UPSTASH_REDIS_URL に正しい URL を設定
```

### 🔴 「CORSエラーに見えるが実際はログイン500になる」

症状:
- ブラウザで CORS エラー表示
- 同時に `/console/api/login` が 500

原因:
- `dify-api` が Supabase に接続できず、認証処理が内部エラー化している
- `.env` の `SUPABASE_DB_HOST` などがプレースホルダのまま

確認方法:
```bash
docker-compose logs --tail=150 dify-api
```

以下のようなエラーが出る場合は DB 接続設定が未完了:
```text
psycopg2.OperationalError: could not translate host name "db.xxxxxxxxxxxxx.supabase.co"
```

解決方法:
```bash
# 1) .env の Supabase 接続情報を実値に更新
nano .env

# 2) API を再起動
docker-compose up -d dify-api

# 3) ブラウザをハードリロード
```

### 🔴 「Failed to request plugin daemon / ConnectError [Errno 111]」

症状: `dify-api` ログに `Failed to request plugin daemon` が大量に出る

原因:
- `dify-plugin-daemon` が未起動
- `PLUGIN_DAEMON_URL` と `PLUGIN_DAEMON_KEY` が不一致
- plugin-daemon の DB が Supabase transaction pooler(6543) へ接続され、`prepared statement already exists (42P05)` でクラッシュ

チェック:
```bash
docker-compose ps
docker-compose logs -f dify-plugin-daemon
docker-compose exec dify-api sh -lc 'echo "$PLUGIN_DAEMON_URL"; echo "$PLUGIN_DAEMON_KEY"'
docker-compose exec dify-plugin-daemon sh -lc 'echo "$DB_HOST:$DB_PORT/$DB_DATABASE"'
```

解決方法:
```bash
# plugin-daemon は DB を専用設定にする（既定 5432）
# .env 例:
# DB_PLUGIN_HOST=aws-1-ap-southeast-1.pooler.supabase.com
# DB_PLUGIN_PORT=5432
# DB_PLUGIN_USER=postgres.<project-ref>
# DB_PLUGIN_PASSWORD=<db-password>
# DB_PLUGIN_DATABASE=dify_plugin

# plugin daemon を含めて再起動
docker-compose up -d

# 反映後に API を再起動
docker-compose restart dify-api
```

### 🔴 「Gemini API キーが無効」

症状: LLM 回答生成で 「Invalid API key」

解決方法:
```bash
# 1. Google Cloud Console で API キー確認
#    https://console.cloud.google.com/apis/credentials

# 2. Gemini API が有効か確認
#    https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

# 3. .env で GOOGLE_API_KEY を確認
cat .env | grep GOOGLE_API_KEY

# 3.1 プレースホルダのままになっていないか確認
# NG例: GOOGLE_API_KEY=AIzaSy...(your-gemini-api-key)

# 4. Dify UI > Model Provider > Google で キーを再設定
```

### 🔴 「ポート 3101 または 5001 が既に使用中」

症状: `Error: listen EADDRINUSE :::3101`

解決方法:
```bash
# 既存プロセスを確認（Linux/Mac）
lsof -i :3101
lsof -i :5001

# プロセス終了
kill -9 <PID>

# または docker-compose.yml でポート番号を変更
nano docker-compose.yml
# dify-web: ports: ["${DIFY_WEB_PORT:-3101}:3000"]
# .env の DIFY_WEB_PORT=3201 などに変更して再起動
```

### 🔴 「メモリ不足 (Out of Memory)」

症状: コンテナが勝手に停止

解決方法:
```bash
# Docker メモリ上限を確認
docker stats

# CPU/メモリ割り当てを増やす（Desktop の Settings > Resources）

# または コンテナの memory limit を設定
docker-compose.yml に以下を追加:
# dify-api:
#   deploy:
#     resources:
#       limits:
#         memory: 2G
#       reservations:
#         memory: 1G
```

### 📝 ログから詳細を確認

```bash
# すべてのコンテナログを確認
docker-compose logs

# 特定コンテナのみ
docker-compose logs dify-api --tail=100

# タイムスタンプ付き
docker-compose logs -t dify-api

# リアルタイム監視
docker-compose logs -f dify-api
```

---

## 運用時のチェックリスト

### 📅 毎日

- [ ] `docker-compose ps` で全コンテナが `Up` 状態か確認
- [ ] ログにエラーがないか確認: `docker-compose logs | grep ERROR`

### 📆 毎週

- [ ] Dify UI から質問をテスト送信
- [ ] RAG 検索が正常に動作しているか確認
- [ ] TiDB データベース容量確認（TiDB Cloud > Cluster Dashboard）

### 📅 毎月

- [ ] Google Gemini API の課金状況確認
- [ ] Upstash Redis の使用量確認
- [ ] ログサイズ確認、古いログを削除
```bash
# ログクリア（必要に応じて）
docker-compose exec dify-api rm -rf /var/log/dify/*
```

### 🚀 新機能を追加したとき

1. `.env` に新しい環境変数を追加
2. `docker-compose.yml` の `dify-api` environment セクションを更新
3. Dify UI から Model Provider 設定を確認
4. テスト送信で動作確認

---

## デバッグお役立ちコマンド

```bash
# コンテナに入る（API）
docker-compose exec dify-api bash

# Dify のバージョン確認
docker-compose exec dify-api dify --version

# DB 接続テスト
docker-compose exec dify-api python3 -c "from sqlalchemy import create_engine; create_engine('postgresql://...').connect()"

# Redis 接続テスト
docker-compose exec dify-redis redis-cli -p 6379 ping

# ディスク使用量確認
docker system df

# 古いイメージ・コンテナのクリーンアップ
docker system prune -a
```

---

## Next.js から Dify Chat API を安全に呼び出す

Dify APIキーはクライアントへ公開せず、サーバー側でのみ使用します。

### 1) サーバー側 API Route で中継する

```typescript
// apps/web/src/app/api/chat/route.ts
import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  const { query, user } = await req.json();
  const difyApiUrl = process.env.DIFY_API_URL || 'http://localhost:5001';
  const difyApiKey = process.env.DIFY_API_KEY;

  if (!difyApiKey) {
    return new Response('DIFY_API_KEY is not set', { status: 500 });
  }

  const response = await fetch(`${difyApiUrl}/chat-messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${difyApiKey}`,
    },
    body: JSON.stringify({
      inputs: {},
      query,
      response_mode: 'streaming',
      user,
    }),
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
```

### 2) クライアントは `/api/chat` のみ呼び出す

```typescript
// apps/web/src/lib/chat.ts
export async function sendChatMessage(query: string, user: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, user }),
  });

  return response.body?.getReader();
}
```

`DIFY_API_KEY` はサーバー環境変数として管理し、`NEXT_PUBLIC_` プレフィックス付きで公開しないでください。

---

## 本番環境へのデプロイ（Cloudflare Tunnel）

自宅PC で Dify を運用する場合、以下で HTTPS 公開します:

### 1. Cloudflare Account を作成

https://dash.cloudflare.com ログイン

### 2. Tunnel を作成

```bash
# cloudflared をインストール（Mac/Linux）
brew install cloudflare/cloudflare/cloudflared
# または手動: https://developers.cloudflare.com/cloudflare-one/downloads/

cloudflared tunnel login  # Cloudflare アカウントでログイン
cloudflared tunnel create dify-jyogi  # Tunnel 作成
```

### 3. Tunnel の設定ファイル

```yaml
# ~/.cloudflared/config.yml または ~/.config/cloudflared/config.yml

tunnel: dify-jyogi
credentials-file: /root/.cloudflared/dify-jyogi.json

ingress:
  - hostname: dify.yourdomain.com
    service: http://localhost:5001
  - hostname: yourdomain.com
    service: http://localhost:3101
  - service: http_status:404
```

### 4. Tunnel を起動

```bash
# フォアグラウンド（テスト用）
cloudflared tunnel run dify-jyogi

# バックグラウンド（運用）
nohup cloudflared tunnel run dify-jyogi &
```

### 5. DNS を設定

Cloudflare Dashboard > DNS > Add Record
```text
Type: CNAME
Name: dify
Content: dify-jyogi.cfargotunnel.com
```

アクセス: `https://dify.yourdomain.com`

---

## 参考リンク

- [Dify 公式ドキュメント](https://docs.dify.ai/)
- [Dify GitHub](https://github.com/langgenius/dify)
- [Supabase ドキュメント](https://supabase.com/docs)
- [TiDB Serverless ドキュメント](https://docs.pingcap.com/tidbcloud/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/)

---

**質問やトラブルがあれば、このドキュメントの該当セクションを確認するか、チーム Slack で質問してください。**
