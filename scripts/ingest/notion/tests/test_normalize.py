"""
Notion normalize.py のテスト

各種 PII パターンの除去・ブロックタイプのフィルタリングを検証する。
"""

from pathlib import Path

import pytest

from normalize import (
    block_to_text,
    clean_text,
    extract_rich_text,
    format_for_dify,
    get_page_title,
    load_page,
    process_file,
    remove_pii,
    remove_urls,
)

SAMPLE_JSON = Path(__file__).parent / "sample_page.json"
SAMPLE_TXT = Path(__file__).parent / "sample_page.txt"


class TestExtractRichText:
    def test_single_text_item(self):
        rich_text = [{"plain_text": "こんにちは"}]
        assert extract_rich_text(rich_text) == "こんにちは"

    def test_multiple_items_concatenated(self):
        rich_text = [
            {"plain_text": "Hello "},
            {"plain_text": "World"},
        ]
        assert extract_rich_text(rich_text) == "Hello World"

    def test_empty_list_returns_empty(self):
        assert extract_rich_text([]) == ""

    def test_missing_plain_text_skipped(self):
        rich_text = [{"type": "text"}, {"plain_text": "有効"}]
        assert extract_rich_text(rich_text) == "有効"


class TestGetPageTitle:
    def test_extracts_title(self):
        page = {
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "活動記録"}],
                }
            }
        }
        assert get_page_title(page) == "活動記録"

    def test_missing_properties_returns_untitled(self):
        assert get_page_title({}) == "Untitled"

    def test_empty_title_returns_untitled(self):
        page = {
            "properties": {
                "title": {
                    "type": "title",
                    "title": [],
                }
            }
        }
        assert get_page_title(page) == "Untitled"


class TestBlockToText:
    def test_paragraph(self):
        block = {
            "type": "paragraph",
            "paragraph": {"rich_text": [{"plain_text": "本文テキスト"}]},
        }
        assert block_to_text(block) == "本文テキスト"

    def test_heading_1_has_prefix(self):
        block = {
            "type": "heading_1",
            "heading_1": {"rich_text": [{"plain_text": "大見出し"}]},
        }
        assert block_to_text(block) == "# 大見出し"

    def test_heading_2_has_prefix(self):
        block = {
            "type": "heading_2",
            "heading_2": {"rich_text": [{"plain_text": "中見出し"}]},
        }
        assert block_to_text(block) == "## 中見出し"

    def test_heading_3_has_prefix(self):
        block = {
            "type": "heading_3",
            "heading_3": {"rich_text": [{"plain_text": "小見出し"}]},
        }
        assert block_to_text(block) == "### 小見出し"

    def test_bulleted_list_item(self):
        block = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"plain_text": "箇条書き項目"}]},
        }
        assert block_to_text(block) == "箇条書き項目"

    def test_numbered_list_item(self):
        block = {
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": [{"plain_text": "番号付き項目"}]},
        }
        assert block_to_text(block) == "番号付き項目"

    def test_quote(self):
        block = {
            "type": "quote",
            "quote": {"rich_text": [{"plain_text": "引用文"}]},
        }
        assert block_to_text(block) == "引用文"

    def test_empty_rich_text_returns_none(self):
        block = {
            "type": "paragraph",
            "paragraph": {"rich_text": []},
        }
        assert block_to_text(block) is None

    def test_whitespace_only_text_returns_none(self):
        block = {
            "type": "paragraph",
            "paragraph": {"rich_text": [{"plain_text": "   "}]},
        }
        assert block_to_text(block) is None

    def test_unsupported_block_type_returns_none(self):
        block = {
            "type": "image",
            "image": {"type": "external", "external": {"url": "https://example.com/img.png"}},
        }
        assert block_to_text(block) is None

    def test_divider_returns_none(self):
        block = {"type": "divider", "divider": {}}
        assert block_to_text(block) is None


class TestRemovePii:
    def test_email_masked(self):
        text = "担当: admin@example.com"
        result = remove_pii(text)
        assert "admin@example.com" not in result
        assert "[email]" in result

    def test_discord_user_mention_removed(self):
        text = "<@!111> さん確認ください"
        result = remove_pii(text)
        assert "<@" not in result
        assert "[mention]" in result

    def test_multiple_emails_masked(self):
        text = "担当A: a@example.com 担当B: b@example.com"
        result = remove_pii(text)
        assert "a@example.com" not in result
        assert "b@example.com" not in result
        assert result.count("[email]") == 2

    def test_clean_text_unchanged(self):
        text = "個人情報なしのテキスト"
        assert remove_pii(text) == text


class TestRemoveUrls:
    def test_https_url_removed(self):
        text = "詳細は https://example.com/schedule を確認"
        result = remove_urls(text)
        assert "https://" not in result

    def test_no_url_unchanged(self):
        text = "URLなし"
        assert remove_urls(text) == text


class TestCleanText:
    def test_email_masked(self):
        text = "問い合わせ: contact@example.com"
        result = clean_text(text)
        assert "contact@example.com" not in result
        assert "[email]" in result

    def test_url_removed(self):
        text = "参照: https://example.com/docs"
        result = clean_text(text)
        assert "https://" not in result

    def test_consecutive_spaces_compressed(self):
        # URL除去後に生じる連続スペースの圧縮
        text = "詳細は  を確認"
        result = clean_text(text)
        assert "  " not in result


class TestLoadPage:
    def test_loads_page_and_blocks(self):
        page, blocks = load_page(SAMPLE_JSON)
        assert page != {}
        assert len(blocks) == 9

    def test_page_has_properties(self):
        page, _ = load_page(SAMPLE_JSON)
        assert "properties" in page

    def test_blocks_is_list(self):
        _, blocks = load_page(SAMPLE_JSON)
        assert isinstance(blocks, list)


class TestProcessFile:
    def test_output_matches_expected(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)

        expected = SAMPLE_TXT.read_text(encoding="utf-8").strip()
        actual = output_file.read_text(encoding="utf-8").strip()
        assert actual == expected

    def test_email_masked_in_output(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        assert "admin@example.com" not in result
        assert "[email]" in result

    def test_urls_removed_in_output(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        assert "https://" not in result

    def test_image_block_excluded(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        # image ブロックはテキストを持たないため除外される
        assert "image.png" not in result

    def test_empty_block_excluded(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8").splitlines()
        # 空の paragraph は出力されない
        assert "" not in [line for line in result if result.index(line) > 1]

    def test_page_title_in_output(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        assert "# 活動記録 2024年1月" in result

    def test_content_block_count(self, tmp_path):
        output_file = tmp_path / "output.txt"
        count = process_file(SAMPLE_JSON, output_file)
        # 9ブロック中: 空paragraph(1) + image(1) = 2件スキップ → 7件
        assert count == 7

    def test_output_file_created(self, tmp_path):
        output_file = tmp_path / "subdir" / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        assert output_file.exists()


class TestFormatForDify:
    def test_starts_with_page_title(self):
        page = {
            "properties": {
                "title": {"type": "title", "title": [{"plain_text": "テストページ"}]}
            }
        }
        result = format_for_dify(page, [])
        assert result.startswith("# テストページ")

    def test_pii_removed_from_blocks(self):
        page = {"properties": {"title": {"type": "title", "title": [{"plain_text": "P"}]}}}
        blocks = [
            {
                "type": "paragraph",
                "paragraph": {"rich_text": [{"plain_text": "連絡先: test@example.com"}]},
            }
        ]
        result = format_for_dify(page, blocks)
        assert "test@example.com" not in result
        assert "[email]" in result
