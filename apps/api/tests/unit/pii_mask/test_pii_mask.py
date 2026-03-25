from services.pii_mask import mask


def test_メールアドレスがマスクされる():
    result = mask("連絡先はtest@example.comです")
    assert result == "連絡先は[EMAIL]です"


def test_電話番号ハイフンありがマスクされる():
    result = mask("電話番号は090-1234-5678です")
    assert "[PHONE]" in result


def test_電話番号ハイフンなしがマスクされる():
    result = mask("電話番号は09012345678です")
    assert "[PHONE]" in result


def test_郵便番号ハイフンありがマスクされる():
    result = mask("住所は〒123-4567です")
    assert "[ZIPCODE]" in result


def test_PIIがない場合はそのまま返す():
    text = "じょぎナビについて教えてください"
    assert mask(text) == text


def test_クレジットカード番号ハイフンありがマスクされる():
    result = mask("カード番号は1234-5678-9012-3456です")
    assert "[CREDIT_CARD]" in result


def test_クレジットカード番号16桁連続がマスクされる():
    result = mask("カード番号は1234567890123456です")
    assert "[CREDIT_CARD]" in result


def test_複数のPIIが同時にマスクされる():
    result = mask("メール: foo@bar.com 電話: 080-9876-5432")
    assert "[EMAIL]" in result
    assert "[PHONE]" in result
