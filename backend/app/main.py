"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.models import Session, User  # Import models to register them
from app.routers import auth, users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown: cleanup if needed
    logger.info("Application shutting down")


# Create FastAPI application instance
app = FastAPI(
    title="SimpleCRM API",
    description="Simple CRM system for freelancers and solo consultants",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with consistent format."""
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = ".".join(str(x) for x in first_error["loc"][1:]) if len(first_error["loc"]) > 1 else None
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "message": first_error["msg"],
                    "field": field,
                    "code": "VALIDATION_ERROR"
                }
            }
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "message": "Validation error",
                "code": "VALIDATION_ERROR"
            }
        }
    )


# Register routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "ok", "message": "SimpleCRM API is running"}
