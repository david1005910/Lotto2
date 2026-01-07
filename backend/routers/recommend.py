from fastapi import APIRouter

from models.schemas import APIResponse, RecommendResponse, Recommendation
from services.recommend_service import get_recommendations

router = APIRouter()


@router.get("/recommend", response_model=APIResponse[RecommendResponse])
async def get_recommend():
    """Get statistically-based number recommendations."""
    result = get_recommendations()

    recommendations = {
        strategy_name: Recommendation(
            numbers=rec_data["numbers"],
            description=rec_data["description"]
        )
        for strategy_name, rec_data in result["recommendations"].items()
    }

    return APIResponse(
        status="success",
        data=RecommendResponse(recommendations=recommendations)
    )
