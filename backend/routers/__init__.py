from .results import router as results_router
from .statistics import router as statistics_router
from .predict import router as predict_router
from .recommend import router as recommend_router
from .admin import router as admin_router

__all__ = [
    "results_router",
    "statistics_router",
    "predict_router",
    "recommend_router",
    "admin_router",
]
