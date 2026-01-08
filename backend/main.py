from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, API_HOST, API_PORT, DEBUG
from services.excel_service import ensure_data_dir
from routers import (
    results_router,
    statistics_router,
    predict_router,
    recommend_router,
    admin_router
)
from routers.simulation import router as simulation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup - ensure data directory exists
    ensure_data_dir()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="로또 Machine Learning 예측 API",
    description="머신러닝 기반 로또 번호 예측 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(results_router, prefix="/api/v1", tags=["results"])
app.include_router(statistics_router, prefix="/api/v1", tags=["statistics"])
app.include_router(predict_router, prefix="/api/v1", tags=["predict"])
app.include_router(recommend_router, prefix="/api/v1", tags=["recommend"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(simulation_router, tags=["simulation"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "로또 Machine Learning 예측 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    )
