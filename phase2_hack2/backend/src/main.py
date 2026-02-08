"""
FastAPI Authentication Backend - FRESH VERSION
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from datetime import datetime

from .core.config import settings
from .core.database import init_db, close_db
from .core.errors import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("\n" + "="*80)
    print("[START] FastAPI Authentication Backend - FRESH START")
    print("="*80)
    try:
        await init_db()
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {str(e)}")
        raise
    print("="*80 + "\n")
    yield
    # Shutdown
    print("\n" + "="*80)
    print("[STOP] Shutting down")
    print("="*80)
    try:
        await close_db()
    except Exception as e:
        print(f"[WARN] Database shutdown error: {str(e)}")
    print("="*80 + "\n")


# Create FastAPI application
app = FastAPI(
    title="Authentication API - NEW VERSION",
    description="JWT Authentication with Signup, Signin, and Me endpoints",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details if exc.details else None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    details = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'] if loc != 'body')
        details.append({
            "field": field,
            "message": error['msg']
        })
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": details
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - NEW VERSION."""
    return {
        "message": "Authentication API - NEW VERSION",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "signup": "/api/auth/signup",
            "signin": "/api/auth/signin",
            "me": "/api/auth/me"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Import and register AUTH ROUTER
from .api.routes import auth
from .api.routes import tasks

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])


# Startup event
@app.on_event("startup")
async def startup_message():
    """Print startup information."""
    print("\n" + "="*80)
    print("✅ AUTHENTICATION API STARTED - NEW VERSION")
    print("="*80)
    print("[INFO] Swagger UI: http://127.0.0.1:8001/docs")
    print("[INFO] Health Check: http://127.0.0.1:8001/health")
    print("")
    print("🔐 AUTHENTICATION ENDPOINTS:")
    print("   POST /api/auth/signup  - Register new user")
    print("   POST /api/auth/signin  - Login user")
    print("   GET  /api/auth/me      - Get current user (protected)")
    print("="*80 + "\n")
