FROM python:3.13-slim

# uv をインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 依存関係インストール（pyproject.toml + uv.lock を先にコピーしてキャッシュ活用）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# アプリケーションコードコピー
COPY . .

# Cloud Run はポート 8080 を使用
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
