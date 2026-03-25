"""
Discord normalize.py のテスト

各種 PII パターンの除去・フィルタリングを検証する。
"""

from pathlib import Path

import pytest

from normalize import (
    clean_content,
    format_timestamp,
    is_bot_message,
    is_stamp_only,
    load_messages,
    process_file,
    remove_pii,
    remove_urls,
)

SAMPLE_JSON = Path(__file__).parent / "sample_channel.json"
SAMPLE_TXT = Path(__file__).parent / "sample_channel.txt"


class TestIsBotMessage:
    def test_bot_returns_true(self):
        msg = {"author": {"isBot": True, "name": "NotifyBot"}}
        assert is_bot_message(msg) is True

    def test_human_returns_false(self):
        msg = {"author": {"isBot": False, "name": "Alice"}}
        assert is_bot_message(msg) is False

    def test_missing_isbot_field_returns_false(self):
        msg = {"author": {"name": "Alice"}}
        assert is_bot_message(msg) is False

    def test_missing_author_returns_false(self):
        msg = {}
        assert is_bot_message(msg) is False


class TestIsStampOnly:
    def test_empty_content_returns_true(self):
        msg = {"content": ""}
        assert is_stamp_only(msg) is True

    def test_whitespace_only_returns_true(self):
        msg = {"content": "   "}
        assert is_stamp_only(msg) is True

    def test_single_emoji_returns_true(self):
        msg = {"content": "👍"}
        assert is_stamp_only(msg) is True

    def test_multiple_emoji_returns_true(self):
        msg = {"content": "😀🎉👏"}
        assert is_stamp_only(msg) is True

    def test_text_content_returns_false(self):
        msg = {"content": "こんにちは"}
        assert is_stamp_only(msg) is False

    def test_text_with_emoji_returns_false(self):
        msg = {"content": "いいね👍"}
        assert is_stamp_only(msg) is False

    def test_missing_content_returns_true(self):
        msg = {}
        assert is_stamp_only(msg) is True


class TestRemovePii:
    def test_user_mention_removed(self):
        text = "<@!111> ありがとう"
        result = remove_pii(text)
        assert "<@" not in result
        assert "[mention]" in result

    def test_user_mention_without_exclamation_removed(self):
        text = "<@111> こんにちは"
        result = remove_pii(text)
        assert "<@111>" not in result
        assert "[mention]" in result

    def test_channel_mention_removed(self):
        text = "詳細は <#999> を確認してください"
        result = remove_pii(text)
        assert "<#" not in result
        assert "[mention]" in result

    def test_role_mention_removed(self):
        text = "<@&777> 全員注目"
        result = remove_pii(text)
        assert "<@&" not in result
        assert "[mention]" in result

    def test_email_masked(self):
        text = "問い合わせは dave@example.com まで"
        result = remove_pii(text)
        assert "dave@example.com" not in result
        assert "[email]" in result

    def test_subdomain_email_masked(self):
        text = "連絡先: user@mail.example.co.jp"
        result = remove_pii(text)
        assert "user@mail.example.co.jp" not in result
        assert "[email]" in result

    def test_multiple_pii_removed(self):
        text = "<@!111> のメール: alice@example.com"
        result = remove_pii(text)
        assert "<@" not in result
        assert "alice@example.com" not in result
        assert "[mention]" in result
        assert "[email]" in result

    def test_clean_text_unchanged(self):
        text = "普通のメッセージです"
        result = remove_pii(text)
        assert result == text


class TestRemoveUrls:
    def test_http_url_removed(self):
        text = "資料は http://example.com/slides を確認"
        result = remove_urls(text)
        assert "http://" not in result

    def test_https_url_removed(self):
        text = "詳細は https://example.com/docs"
        result = remove_urls(text)
        assert "https://" not in result

    def test_url_with_query_removed(self):
        text = "参照: https://example.com/page?id=123&token=abc"
        result = remove_urls(text)
        assert "https://" not in result
        assert "token=abc" not in result

    def test_no_url_unchanged(self):
        text = "URLのないメッセージ"
        result = remove_urls(text)
        assert result == text


class TestCleanContent:
    def test_mention_removed(self):
        text = "<@!111> ありがとうございます！確認しました。"
        result = clean_content(text)
        assert "<@" not in result
        assert "[mention]" in result

    def test_url_removed(self):
        text = "資料ここに置いておきます。 https://example.com/slides"
        result = clean_content(text)
        assert "https://" not in result

    def test_email_masked(self):
        text = "問い合わせは dave@example.com までお願いします。"
        result = clean_content(text)
        assert "dave@example.com" not in result
        assert "[email]" in result

    def test_extra_spaces_compressed(self):
        text = "前  後"
        result = clean_content(text)
        assert "  " not in result

    def test_mention_and_url_combined(self):
        text = "<@!111> 資料は https://example.com/slides です"
        result = clean_content(text)
        assert "<@" not in result
        assert "https://" not in result


class TestFormatTimestamp:
    def test_iso_8601_with_timezone(self):
        ts = "2024-01-15T10:30:00+09:00"
        assert format_timestamp(ts) == "2024-01-15 10:30"

    def test_iso_8601_utc(self):
        ts = "2024-01-15T01:00:00+00:00"
        assert format_timestamp(ts) == "2024-01-15 01:00"

    def test_short_string_returned_as_is(self):
        ts = "bad"
        assert format_timestamp(ts) == "bad"


class TestLoadMessages:
    def test_loads_channel_name(self):
        channel_name, _ = load_messages(SAMPLE_JSON)
        assert channel_name == "general-members"

    def test_loads_all_messages(self):
        _, messages = load_messages(SAMPLE_JSON)
        assert len(messages) == 7

    def test_messages_have_required_fields(self):
        _, messages = load_messages(SAMPLE_JSON)
        for msg in messages:
            assert "id" in msg
            assert "timestamp" in msg
            assert "author" in msg
            assert "content" in msg


class TestProcessFile:
    def test_output_matches_expected(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)

        expected = SAMPLE_TXT.read_text(encoding="utf-8").strip()
        actual = output_file.read_text(encoding="utf-8").strip()
        assert actual == expected

    def test_bot_messages_excluded(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        assert "NotifyBot" not in result
        assert "リマインダー" not in result

    def test_stamp_only_messages_excluded(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        # Charlie の 👍 メッセージは除外される
        assert "Charlie" not in result

    def test_empty_messages_excluded(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        # Eve の空メッセージは除外される
        assert "Eve" not in result

    def test_message_count_correct(self, tmp_path):
        output_file = tmp_path / "output.txt"
        count = process_file(SAMPLE_JSON, output_file)
        # 7件中: Bot(1) + 絵文字のみ(1) + 空(1) = 3件除外 → 4件残る
        assert count == 4

    def test_pii_removed_in_output(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        # メンションIDとメールアドレスは除去済み
        assert "<@" not in result
        assert "dave@example.com" not in result
        assert "[mention]" in result
        assert "[email]" in result

    def test_urls_removed_in_output(self, tmp_path):
        output_file = tmp_path / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        result = output_file.read_text(encoding="utf-8")
        assert "https://" not in result

    def test_output_file_created(self, tmp_path):
        output_file = tmp_path / "subdir" / "output.txt"
        process_file(SAMPLE_JSON, output_file)
        assert output_file.exists()
