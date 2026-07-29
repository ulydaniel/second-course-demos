import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from app.config import settings
from app.db.seed import seed_all
from app.errors import error_response, register_exception_handlers
from app.rate_limit import limiter
from app.routes import api_router
from app.services import session_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_IS_DEV = settings.environment == "development"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Create tables + seed tenants/admins so credentials survive restarts.
    seed_all()
    session_store.purge_expired()
    yield


app = FastAPI(
    title="Second Course University Dashboard API",
    description="Backend for university admin metrics and exports.",
    version="0.1.0",
    lifespan=lifespan,
    # Only expose interactive docs in development.
    docs_url="/docs" if _IS_DEV else None,
    redoc_url="/redoc" if _IS_DEV else None,
    openapi_url="/openapi.json" if _IS_DEV else None,
)

register_exception_handlers(app)

# Rate limiting (slowapi): the limiter instance is read from app.state by the
# @limiter.limit decorators on the auth routes.
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, _exc: RateLimitExceeded) -> Response:
    return error_response(
        429,
        "rate_limited",
        "Too many requests. Please slow down and try again shortly.",
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if not _IS_DEV:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Second Course University Dashboard API"}
