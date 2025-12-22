from fastapi import APIRouter, HTTPException

from models.schemas import (
    APIResponse,
    SyncResponse,
    TrainResponse,
    StatusResponse,
    DatabaseStatus,
    MLModelStatus,
    ModelTrainResult
)
from models.database import get_total_draws, get_latest_draw, get_db
from services.data_service import sync_incremental, sync_full
from services.ml_service import train_models, get_model_status

router = APIRouter()


@router.post("/sync", response_model=APIResponse[SyncResponse])
async def sync_data():
    """Sync new lotto results (incremental sync)."""
    try:
        synced_count, latest_draw = sync_incremental()

        return APIResponse(
            status="success",
            data=SyncResponse(
                synced_count=synced_count,
                latest_draw=latest_draw
            ),
            message=f"{synced_count}개 회차 동기화 완료"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"동기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/sync/full", response_model=APIResponse[SyncResponse])
async def sync_data_full():
    """Sync all lotto results from draw 1 (full sync)."""
    try:
        synced_count, latest_draw = sync_full()

        return APIResponse(
            status="success",
            data=SyncResponse(
                synced_count=synced_count,
                latest_draw=latest_draw
            ),
            message=f"전체 {synced_count}개 회차 동기화 완료"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"동기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/train", response_model=APIResponse[TrainResponse])
async def train():
    """Train all ML models."""
    try:
        result = train_models()

        models = {
            model_name: ModelTrainResult(
                accuracy=model_data["accuracy"],
                trained=model_data["trained"]
            )
            for model_name, model_data in result["models"].items()
        }

        return APIResponse(
            status="success",
            data=TrainResponse(
                models=models,
                trained_at=result["trained_at"],
                training_samples=result["training_samples"]
            ),
            message="모델 학습 완료"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 학습 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/status", response_model=APIResponse[StatusResponse])
async def get_status():
    """Get system status."""
    total_draws = get_total_draws()
    latest_draw = get_latest_draw()

    # Get latest date
    latest_date = None
    if latest_draw:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT draw_date FROM lotto_results WHERE draw_no = ?",
                (latest_draw,)
            )
            row = cursor.fetchone()
            if row:
                latest_date = row["draw_date"]

    ml_status = get_model_status()

    return APIResponse(
        status="success",
        data=StatusResponse(
            database=DatabaseStatus(
                total_draws=total_draws,
                latest_draw=latest_draw,
                latest_date=latest_date
            ),
            ml_models=MLModelStatus(
                trained=ml_status["trained"],
                last_trained=ml_status.get("last_trained"),
                models_available=ml_status.get("models_available", [])
            )
        )
    )
