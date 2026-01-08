from typing import Dict, List, Any, Tuple
import random
import numpy as np
from services.ml_service import predict_numbers, extract_features, _postprocess_prediction
from services.data_service import get_latest_draw, get_result_by_draw_no
import joblib
from pathlib import Path
from config import MODEL_PATH


def check_winner_rank(predicted_numbers: List[int], winning_numbers: List[int], bonus_number: int) -> int:
    """
    Check winner rank based on matching numbers.
    Returns:
    - 1: 6 matches (1st place)
    - 2: 5 matches + bonus (2nd place)
    - 3: 5 matches (3rd place)
    - 4: 4 matches (4th place)
    - 5: 3 matches (5th place)
    - 0: No prize
    """
    matches = len(set(predicted_numbers) & set(winning_numbers))
    has_bonus = bonus_number in predicted_numbers

    if matches == 6:
        return 1  # 1등
    elif matches == 5 and has_bonus:
        return 2  # 2등
    elif matches == 5:
        return 3  # 3등
    elif matches == 4:
        return 4  # 4등
    elif matches == 3:
        return 5  # 5등
    else:
        return 0  # 당첨되지 않음


def generate_single_prediction() -> List[int]:
    """Generate a single prediction using ML models (ensemble approach)."""
    try:
        # Get current predictions from all models
        predictions = predict_numbers()

        # Combine predictions from all models
        all_numbers = []
        for model_name, pred_data in predictions["predictions"].items():
            all_numbers.extend(pred_data["numbers"])

        # Count frequency of each number across all models
        number_freq = {}
        for num in all_numbers:
            number_freq[num] = number_freq.get(num, 0) + 1

        # Select top 6 most frequent numbers
        sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)
        selected_numbers = [num for num, _ in sorted_numbers[:6]]

        # If we have less than 6 numbers, fill with random numbers
        while len(selected_numbers) < 6:
            new_num = random.randint(1, 45)
            if new_num not in selected_numbers:
                selected_numbers.append(new_num)

        return sorted(selected_numbers[:6])

    except Exception as e:
        print(f"ML prediction failed: {e}, using fallback random generation")
        # Fallback to pure random if ML fails
        numbers = random.sample(range(1, 46), 6)
        return sorted(numbers)


def run_simulation(num_predictions: int = 1000) -> Dict[str, Any]:
    """
    Run lottery prediction simulation.

    Args:
        num_predictions: Number of prediction sets to generate (default: 1000)

    Returns:
        Dictionary containing simulation results with winner statistics
    """
    try:
        # Get the latest winning numbers for comparison
        latest_draw_no = get_latest_draw()
        if not latest_draw_no:
            raise ValueError("No winning numbers available for comparison")

        latest_result = get_result_by_draw_no(latest_draw_no)
        if not latest_result:
            raise ValueError("Failed to get latest winning numbers")

        winning_numbers = latest_result["numbers"]
        bonus_number = latest_result["bonus"]

        # Initialize winner statistics
        winner_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0}

        # Generate predictions and check winners
        predictions = []
        for i in range(num_predictions):
            predicted_numbers = generate_single_prediction()
            rank = check_winner_rank(predicted_numbers, winning_numbers, bonus_number)
            winner_stats[rank] += 1
            predictions.append(predicted_numbers)

        # Calculate percentages
        winner_percentages = {}
        for rank in [1, 2, 3, 4, 5]:
            winner_percentages[rank] = round((winner_stats[rank] / num_predictions) * 100, 2)

        return {
            "status": "success",
            "simulation_results": {
                "total_predictions": num_predictions,
                "winning_numbers": winning_numbers,
                "bonus_number": bonus_number,
                "draw_info": {
                    "draw_no": latest_result["draw_no"],
                    "draw_date": latest_result["draw_date"]
                },
                "winner_stats": {
                    "1st_place": {"count": winner_stats[1], "percentage": winner_percentages[1]},
                    "2nd_place": {"count": winner_stats[2], "percentage": winner_percentages[2]},
                    "3rd_place": {"count": winner_stats[3], "percentage": winner_percentages[3]},
                    "4th_place": {"count": winner_stats[4], "percentage": winner_percentages[4]},
                    "5th_place": {"count": winner_stats[5], "percentage": winner_percentages[5]},
                    "no_prize": {"count": winner_stats[0], "percentage": round((winner_stats[0] / num_predictions) * 100, 2)}
                },
                "sample_predictions": predictions[:10]  # Show first 10 predictions as examples
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Simulation failed: {str(e)}"
        }


def get_simulation_info() -> Dict[str, Any]:
    """Get information about simulation capabilities."""
    try:
        latest_draw_no = get_latest_draw()
        if not latest_draw_no:
            return {
                "status": "error",
                "message": "No winning data available for simulation"
            }

        latest_result = get_result_by_draw_no(latest_draw_no)
        if not latest_result:
            return {
                "status": "error",
                "message": "Failed to get latest winning data"
            }

        return {
            "status": "success",
            "info": {
                "available": True,
                "latest_draw": {
                    "draw_no": latest_result["draw_no"],
                    "draw_date": latest_result["draw_date"],
                    "winning_numbers": latest_result["numbers"],
                    "bonus_number": latest_result["bonus"]
                },
                "description": "예측 알고리즘으로 생성한 번호를 최신 당첨번호와 비교하여 당첨율을 분석합니다."
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get simulation info: {str(e)}"
        }