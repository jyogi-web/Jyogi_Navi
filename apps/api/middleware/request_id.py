import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """各リクエストに trace_id を付与するミドルウェア。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = trace_id
        return response
