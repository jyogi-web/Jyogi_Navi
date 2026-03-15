.PHONY: lint format check fix help

help:
	@echo "Usage:"
	@echo "  make lint    - Ruffでlintチェック（修正なし）"
	@echo "  make format  - Ruffでフォーマットチェック（修正なし）"
	@echo "  make check   - lint + format を両方チェック（CI用）"
	@echo "  make fix     - lint自動修正 + フォーマット適用（開発用）"

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

check: lint format

fix:
	uv run ruff check --fix .
	uv run ruff format .
