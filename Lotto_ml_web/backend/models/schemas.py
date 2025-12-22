from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None


class LottoResultCreate(BaseModel):
    """Schema for creating a lotto result."""
    draw_no: int = Field(..., ge=1, description="Draw number")
    draw_date: str = Field(..., description="Draw date (YYYY-MM-DD)")
    numbers: List[int] = Field(..., min_length=6, max_length=6, description="6 winning numbers")
    bonus: int = Field(..., ge=1, le=45, description="Bonus number")
    prize_1st: Optional[int] = Field(None, description="1st prize amount")


class LottoResult(BaseModel):
    """Schema for a lotto result."""
    draw_no: int
    draw_date: str
    numbers: List[int]
    bonus: int
    prize_1st: Optional[int] = None


class LottoResultResponse(BaseModel):
    """Schema for lotto result API response."""
    draw_no: int
    draw_date: str
    numbers: List[int]
    bonus: int
    prize_1st: Optional[int] = None


class Pagination(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResults(BaseModel):
    """Paginated results response."""
    results: List[LottoResultResponse]
    pagination: Pagination


class NumberFrequency(BaseModel):
    """Number frequency data."""
    frequencies: Dict[str, int]


class OddEvenDistribution(BaseModel):
    """Odd/even distribution data."""
    distribution: Dict[str, int]


class SumDistribution(BaseModel):
    """Sum distribution data."""
    ranges: List[str]
    counts: List[int]


class ConsecutiveStats(BaseModel):
    """Consecutive number statistics."""
    has_consecutive: int
    no_consecutive: int


class SectionDistribution(BaseModel):
    """Section distribution data."""
    low_1_15: Dict[str, Any]
    mid_16_30: Dict[str, Any]
    high_31_45: Dict[str, Any]


class StatisticsResponse(BaseModel):
    """Statistics API response."""
    number_frequency: Dict[str, int]
    odd_even_distribution: Dict[str, int]
    sum_distribution: SumDistribution
    consecutive_stats: ConsecutiveStats
    section_distribution: Dict[str, Any]
    total_draws: int


class ModelPrediction(BaseModel):
    """Single model prediction."""
    numbers: List[int]
    accuracy: float


class PredictionResponse(BaseModel):
    """Prediction API response."""
    predictions: Dict[str, ModelPrediction]
    disclaimer: str = "로또는 무작위 추첨이므로 예측이 불가능합니다. 이 결과는 참고용입니다."
    last_trained: Optional[str] = None


class Recommendation(BaseModel):
    """Single recommendation."""
    numbers: List[int]
    description: str


class RecommendResponse(BaseModel):
    """Recommend API response."""
    recommendations: Dict[str, Recommendation]


class DatabaseStatus(BaseModel):
    """Database status info."""
    total_draws: int
    latest_draw: Optional[int]
    latest_date: Optional[str]


class MLModelStatus(BaseModel):
    """ML model status info."""
    trained: bool
    last_trained: Optional[str]
    models_available: List[str]


class StatusResponse(BaseModel):
    """System status API response."""
    database: DatabaseStatus
    ml_models: MLModelStatus
    last_sync: Optional[str] = None


class SyncResponse(BaseModel):
    """Sync API response."""
    synced_count: int
    latest_draw: int


class ModelTrainResult(BaseModel):
    """Single model training result."""
    accuracy: float
    trained: bool


class TrainResponse(BaseModel):
    """Train API response."""
    models: Dict[str, ModelTrainResult]
    trained_at: str
    training_samples: int
