from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from app.config import settings
from app.utils.logger import setup_logging
from app.db.database import create_tables
from app.core.scheduler import start_scheduler, stop_scheduler, load_all_schedules
from app.api.routes_auth import router as auth_router
from app.api.routes_accounts import router as accounts_router
from app.api.routes_tasks import router as tasks_router

setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("app.startup", version=settings.APP_VERSION)
    await create_tables()
    start_scheduler()
    await load_all_schedules()
    yield
    # Shutdown
    stop_scheduler()
    logger.info("app.shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration:.2f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Routers
app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(tasks_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}