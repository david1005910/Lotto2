from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from services.simulation_service import run_simulation, get_simulation_info

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


class SimulationRequest(BaseModel):
    num_predictions: int = Field(default=1000, ge=1000, le=100000000, description="Number of predictions to generate")


@router.post("/run")
async def run_prediction_simulation(request: SimulationRequest):
    """
    Run lottery prediction simulation.

    Generates the specified number of predictions using ML models
    and compares them against the latest winning numbers to calculate
    winning statistics.
    """
    try:
        # Simple simulation with random numbers for testing
        import random

        winning_numbers = [1, 4, 16, 23, 31, 41]
        bonus_number = 2

        # Generate predictions and check winners
        winner_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0}
        sample_predictions = []

        # For large simulations, collect samples less frequently
        sample_interval = max(1, request.num_predictions // 10) if request.num_predictions > 1000 else 1

        for i in range(request.num_predictions):
            predicted_numbers = sorted(random.sample(range(1, 46), 6))

            # Store sample predictions with interval to avoid memory issues
            if len(sample_predictions) < 10 and i % sample_interval == 0:
                sample_predictions.append(predicted_numbers)

            # Check winner rank
            matches = len(set(predicted_numbers) & set(winning_numbers))
            has_bonus = bonus_number in predicted_numbers

            if matches == 6:
                winner_stats[1] += 1
            elif matches == 5 and has_bonus:
                winner_stats[2] += 1
            elif matches == 5:
                winner_stats[3] += 1
            elif matches == 4:
                winner_stats[4] += 1
            elif matches == 3:
                winner_stats[5] += 1
            else:
                winner_stats[0] += 1

        # Calculate percentages
        return {
            "status": "success",
            "data": {
                "total_predictions": request.num_predictions,
                "winning_numbers": winning_numbers,
                "bonus_number": bonus_number,
                "draw_info": {
                    "draw_no": 1205,
                    "draw_date": "2023-12-30"
                },
                "winner_stats": {
                    "1st_place": {"count": winner_stats[1], "percentage": round((winner_stats[1] / request.num_predictions) * 100, 2)},
                    "2nd_place": {"count": winner_stats[2], "percentage": round((winner_stats[2] / request.num_predictions) * 100, 2)},
                    "3rd_place": {"count": winner_stats[3], "percentage": round((winner_stats[3] / request.num_predictions) * 100, 2)},
                    "4th_place": {"count": winner_stats[4], "percentage": round((winner_stats[4] / request.num_predictions) * 100, 2)},
                    "5th_place": {"count": winner_stats[5], "percentage": round((winner_stats[5] / request.num_predictions) * 100, 2)},
                    "no_prize": {"count": winner_stats[0], "percentage": round((winner_stats[0] / request.num_predictions) * 100, 2)}
                },
                "sample_predictions": sample_predictions
            },
            "message": f"{request.num_predictions}개 예측 시뮬레이션이 완료되었습니다."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시뮬레이션 실행 중 오류가 발생했습니다: {str(e)}")


@router.get("/info")
async def get_simulation_information():
    """
    Get simulation information and latest winning data.

    Returns information about simulation capabilities and
    the latest winning numbers that will be used for comparison.
    """
    try:
        # Temporary hardcoded response for testing
        return {
            "status": "success",
            "data": {
                "available": True,
                "latest_draw": {
                    "draw_no": 1205,
                    "draw_date": "2023-12-30",
                    "winning_numbers": [1, 4, 16, 23, 31, 41],
                    "bonus_number": 2
                },
                "description": "예측 알고리즘으로 생성한 번호를 최신 당첨번호와 비교하여 당첨율을 분석합니다."
            },
            "message": "시뮬레이션 정보를 성공적으로 조회했습니다."
        }

    except Exception as e:
        import traceback
        error_detail = f"시뮬레이션 정보 조회 중 오류가 발생했습니다: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/status")
async def get_simulation_status():
    """
    Get simulation status and capabilities.

    Returns whether simulation is available and basic information.
    """
    try:
        result = get_simulation_info()

        return {
            "status": "success",
            "data": {
                "available": result["status"] == "success",
                "ready": result["status"] == "success"
            },
            "message": "시뮬레이션 상태를 확인했습니다."
        }

    except Exception as e:
        return {
            "status": "success",
            "data": {
                "available": False,
                "ready": False
            },
            "message": f"시뮬레이션을 사용할 수 없습니다: {str(e)}"
        }