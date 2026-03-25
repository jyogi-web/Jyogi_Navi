from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from exceptions import AppError
from middleware.request_id import RequestIDMiddleware
from routers import chat, consent, faq, feedback, health, usage_logs
from services.log_store import _emit_structured_log

app = FastAPI(title="Jyogi Navi API", version="0.1.0")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    trace_id: str = getattr(request.state, "trace_id", "")
    level = "ERROR" if exc.status_code >= 500 else "WARN"
    _emit_structured_log(
        level=level,
        action="error.handled",
        trace_id=trace_id,
        metadata={"error_code": exc.error_code, "status_code": exc.status_code},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "trace_id": trace_id,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    trace_id: str = getattr(request.state, "trace_id", "")
    _emit_structured_log(
        level="WARN",
        action="error.validation",
        trace_id=trace_id,
        metadata={"errors": str(exc.errors())},
    )
    return JSONResponse(
        status_code=400,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "入力内容を確認してください",
            "trace_id": trace_id,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id: str = getattr(request.state, "trace_id", "")
    _emit_structured_log(
        level="ERROR",
        action="error.unhandled",
        trace_id=trace_id,
        metadata={"exception": f"{type(exc).__name__}: {exc}"},
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "エラーが発生しました",
            "trace_id": trace_id,
        },
    )


app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(faq.router)
app.include_router(consent.router)
app.include_router(feedback.router)
app.include_router(usage_logs.router)
