from typing import Optional
from fastapi import APIRouter, Query

from models.schemas import APIResponse, StatisticsResponse, SumDistribution, ConsecutiveStats
from services.statistics_service import calculate_statistics

router = APIRouter()


@router.get("/statistics", response_model=APIResponse[StatisticsResponse])
async def get_statistics(
    recent: Optional[int] = Query(
        None,
        ge=1,
        description="Number of recent draws to analyze (default: all)"
    )
):
    """Get comprehensive lotto statistics."""
    stats = calculate_statistics(recent=recent)

    return APIResponse(
        status="success",
        data=StatisticsResponse(
            number_frequency=stats["number_frequency"],
            odd_even_distribution=stats["odd_even_distribution"],
            sum_distribution=SumDistribution(
                ranges=stats["sum_distribution"]["ranges"],
                counts=stats["sum_distribution"]["counts"]
            ),
            consecutive_stats=ConsecutiveStats(
                has_consecutive=stats["consecutive_stats"]["has_consecutive"],
                no_consecutive=stats["consecutive_stats"]["no_consecutive"]
            ),
            section_distribution=stats["section_distribution"],
            total_draws=stats["total_draws"]
        )
    )
