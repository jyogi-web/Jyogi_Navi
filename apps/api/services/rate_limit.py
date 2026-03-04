# TODO: usage_logs を参照した日次トークンレート制限の実装
# - 1日の上限トークン数は config.py の DAILY_TOKEN_LIMIT を使用


def is_rate_limited(session_id: str) -> bool:
    """当日使用量が上限を超えている場合 True を返す。"""
    # TODO: 実装
    return False
