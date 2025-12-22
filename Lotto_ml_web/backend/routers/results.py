from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from models.schemas import APIResponse, LottoResultResponse, PaginatedResults, Pagination
from services.data_service import get_results, get_result_by_draw_no

router = APIRouter()


@router.get("/results", response_model=APIResponse[PaginatedResults])
async def list_results(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    from_draw: Optional[int] = Query(None, ge=1, description="Start draw number"),
    to_draw: Optional[int] = Query(None, ge=1, description="End draw number")
):
    """Get paginated lotto results."""
    results, total = get_results(
        page=page,
        limit=limit,
        sort=sort,
        from_draw=from_draw,
        to_draw=to_draw
    )

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    response_results = [
        LottoResultResponse(**result) for result in results
    ]

    return APIResponse(
        status="success",
        data=PaginatedResults(
            results=response_results,
            pagination=Pagination(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages
            )
        )
    )


@router.get("/results/{draw_no}", response_model=APIResponse[LottoResultResponse])
async def get_result(draw_no: int):
    """Get single lotto result by draw number."""
    result = get_result_by_draw_no(draw_no)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"회차 {draw_no}을(를) 찾을 수 없습니다."
        )

    return APIResponse(
        status="success",
        data=LottoResultResponse(**result)
    )
