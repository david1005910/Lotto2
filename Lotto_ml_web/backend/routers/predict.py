from fastapi import APIRouter, HTTPException

from models.schemas import APIResponse, PredictionResponse, ModelPrediction
from services.ml_service import predict_numbers

router = APIRouter()


@router.get("/predict", response_model=APIResponse[PredictionResponse])
async def get_predictions():
    """Get ML model predictions for next draw."""
    try:
        result = predict_numbers()

        predictions = {
            model_name: ModelPrediction(
                numbers=pred_data["numbers"],
                accuracy=pred_data["accuracy"]
            )
            for model_name, pred_data in result["predictions"].items()
        }

        return APIResponse(
            status="success",
            data=PredictionResponse(
                predictions=predictions,
                disclaimer=result["disclaimer"],
                last_trained=result.get("last_trained")
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"예측 중 오류가 발생했습니다: {str(e)}"
        )
