from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware.request_id import RequestIDMiddleware
from routers import consent, feedback, health

app = FastAPI(title="Jyogi Navi API", version="0.1.0")

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(consent.router)
app.include_router(feedback.router)
