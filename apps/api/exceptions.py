"""アプリケーション例外クラス。"""


class AppError(Exception):
    """アプリケーション例外の基底クラス。"""

    def __init__(self, status_code: int, error_code: str, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class RateLimitExceeded(AppError):
    """レート制限超過。"""

    def __init__(self) -> None:
        super().__init__(429, "RATE_LIMIT_EXCEEDED", "本日の質問上限に達しました")


class ExternalServiceError(AppError):
    """外部サービス(Dify/LLM)障害。"""

    def __init__(self, error_code: str = "EXTERNAL_SERVICE_ERROR") -> None:
        super().__init__(503, error_code, "現在サービスが混雑しています")


class ValidationError(AppError):
    """バリデーションエラー。"""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            400, "VALIDATION_ERROR", message or "入力内容を確認してください"
        )


class InternalError(AppError):
    """サーバー内部エラー。"""

    def __init__(self, error_code: str = "INTERNAL_ERROR") -> None:
        super().__init__(500, error_code, "エラーが発生しました")
