# 🐳 Dify セットアップ & 運用ガイド

**最終更新日:** 2026年3月6日  
**対象フェーズ:** Sprint 0 (MVP基盤構築)

---

## 📋 目次

1. [前提条件](#前提条件)
2. [初回セットアップ（5分）](#初回セットアップ)
3. [起動・停止方法](#起動・停止方法)
4. [トラブルシューティング](#トラブルシューティング)
5. [運用時のチェックリスト](#運用時のチェックリスト)

---

## 前提条件

- Docker & Docker Compose インストール済み
  - `docker --version` と `docker-compose --version` で確認
- **外部サービスアカウント作成済み:**
  - ✅ Supabase プロジェクト（PostgreSQL DB）
  - ✅ TiDB Serverless クラスター（Vector DB）
  - ✅ Upstash Redis インスタンス
  - ✅ Google Cloud API キー（Gemini）

> 💡 これらのセットアップ手順は [external-services-setup.md] を参照してください

---

## 初回セットアップ

### ステップ 1: 環境変数テンプレートをコピー

```bash
cd infra/dify

# テンプレートをコピー
cp .env.dify.example .env.dify
```

### ステップ 2: 環境変数を編集

```bash
# .env.dify を開いて各キーを入力
nano .env.dify  # または vim / VSCode で編集
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
UPSTASH_REDIS_URL=redis://:password@host:6379

# Google Gemini API
GOOGLE_API_KEY=AIzaSy...

# Secret keys（生成: python3 -c "import secrets; print(secrets.token_hex(32))"）
SECRET_KEY=your-random-string
DIFY_API_SECRET_KEY=your-api-secret-string
```

### ステップ 3: Secret Keys を生成（一度だけ）

```bash
# Python 3 で安全なランダム文字列生成
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('DIFY_API_SECRET_KEY=' + secrets.token_hex(32))"

# 出力をコピーして .env.dify に貼り付け
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

# バックグラウンドで起動
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
# dify-web            "npm run start"        Up 2 minutes        0.0.0.0:3000->3000/tcp
# dify-redis          "redis-server..."      Up 2 minutes        0.0.0.0:6379->6379/tcp
```

### 🌐 Dify UI にアクセス

ブラウザで開く:
```
http://localhost:3000
```

初回アクセス時:
1. **セットアップウィザードが表示される**
2. 管理者アカウントを作成
3. **API キーやチャット API を生成**（Next.js から呼び出す際に必要）

### 🛑 停止する

```bash
# コンテナを停止（データは保持）
docker-compose down

# ボリュームも削除（完全リセット。非推奨）
docker-compose down -v
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
cat .env.dify | grep SUPABASE

# 2. DB に ping を打つ（Linux/Mac）
psql -h db.xxxxxxxxxxxxx.supabase.co -U postgres -d postgres -c "SELECT 1;"

# 3. ファイアウォール: Supabase Dashboard で IP ホワイトリスト確認
```

解決方法:
```bash
# ログ確認
docker-compose logs dify-api | tail -50

# 環境変数を修正
nano .env.dify

# 再起動
docker-compose restart dify-api
```

### 🔴 「ベクトル検索エラー (TiDB)」

症状: Dify で「RAG 検索に失敗」

チェック:
```bash
# TiDB の接続文字列を確認
cat .env.dify | grep TIDB

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
nano .env.dify
# → UPSTASH_REDIS_URL に正しい URL を設定
```

### 🔴 「Gemini API キーが無効」

症状: LLM 回答生成で 「Invalid API key」

解決方法:
```bash
# 1. Google Cloud Console で API キー確認
#    https://console.cloud.google.com/apis/credentials

# 2. Gemini API が有効か確認
#    https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

# 3. .env.dify で GOOGLE_API_KEY を確認
cat .env.dify | grep GOOGLE_API_KEY

# 4. Dify UI > Model Provider > Google で キーを再設定
```

### 🔴 「ポート 3000 または 5001 が既に使用中」

症状: `Error: listen EADDRINUSE :::3000`

解決方法:
```bash
# 既存プロセスを確認（Linux/Mac）
lsof -i :3000
lsof -i :5001

# プロセス終了
kill -9 <PID>

# または docker-compose.yml でポート番号を変更
nano docker-compose.yml
# dify-web: ports: ["3001:3000"]  ← 3001 に変更
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

1. `.env.dify` に新しい環境変数を追加
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

## Next.js から Dify Chat API を呼び出す

Dify が起動したら、Next.js のチャットUI から Chat API を使用できます。

```typescript
// apps/web/src/lib/dify.ts

const DIFY_API_URL = process.env.NEXT_PUBLIC_DIFY_API_URL || 'http://localhost:5001';
const DIFY_API_KEY = process.env.NEXT_PUBLIC_DIFY_API_KEY; // Dify UI > Api Key で取得

export async function sendChatMessage(query: string) {
  const response = await fetch(`${DIFY_API_URL}/chat-messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${DIFY_API_KEY}`,
    },
    body: JSON.stringify({
      inputs: {},
      query: query,
      response_mode: 'streaming',
      user: 'user-123',
    }),
  });

  return response.body?.getReader(); // ストリーミング対応
}
```

詳細は [apps/web/src/lib/dify.ts] を参照してください。

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
    service: http://localhost:3000
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
```
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
