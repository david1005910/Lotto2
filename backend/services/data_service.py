import requests
import pandas as pd
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime

from config import DHLOTTERY_API_URL, CURRENT_DRAW_NO
from services.excel_service import (
    excel_exists,
    load_from_excel,
    save_to_excel,
    append_to_excel,
    get_latest_draw_from_excel,
    get_total_draws_from_excel,
    get_all_results_from_excel,
    get_result_by_draw_no_from_excel
)


def fetch_lotto_result(draw_no: int) -> Optional[Dict[str, Any]]:
    """Fetch lotto result from DHLottery API."""
    try:
        response = requests.get(
            DHLOTTERY_API_URL,
            params={"method": "getLottoNumber", "drwNo": draw_no},
            timeout=10
        )
        data = response.json()

        if data.get("returnValue") == "success":
            return {
                "draw_no": data["drwNo"],
                "draw_date": data["drwNoDate"],
                "numbers": sorted([
                    data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                    data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                ]),
                "bonus": data["bnusNo"],
                "prize_1st": data.get("firstWinamnt", 0)
            }
        return None
    except Exception as e:
        print(f"Error fetching draw {draw_no}: {e}")
        return None


def update_data() -> Tuple[int, int]:
    """Update data by fetching new draws from API and saving to Excel."""
    latest_excel = get_latest_draw_from_excel() or 0
    new_results = []

    print(f"Current latest draw in Excel: {latest_excel}")
    print(f"Fetching new draws from {latest_excel + 1} to {CURRENT_DRAW_NO}...")

    for draw_no in range(latest_excel + 1, CURRENT_DRAW_NO + 1):
        result = fetch_lotto_result(draw_no)
        if result:
            new_results.append(result)

        if draw_no % 100 == 0:
            print(f"Fetched {draw_no} draws...")

    if new_results:
        append_to_excel(new_results)
        print(f"Updated {len(new_results)} new draws")
    else:
        print("No new draws to update")

    latest_draw = get_latest_draw_from_excel() or CURRENT_DRAW_NO
    return len(new_results), latest_draw


def sync_full() -> Tuple[int, int]:
    """Sync all draws from 1 to current (full sync) and save to Excel."""
    all_results = []

    print(f"Full sync: Fetching draws 1 to {CURRENT_DRAW_NO}...")

    for draw_no in range(1, CURRENT_DRAW_NO + 1):
        result = fetch_lotto_result(draw_no)
        if result:
            all_results.append(result)

        if draw_no % 100 == 0:
            print(f"Synced {draw_no} draws...")

    if all_results:
        # Convert to DataFrame and save
        rows = []
        for result in all_results:
            numbers = result["numbers"]
            rows.append({
                "draw_no": result["draw_no"],
                "draw_date": result["draw_date"],
                "num1": numbers[0],
                "num2": numbers[1],
                "num3": numbers[2],
                "num4": numbers[3],
                "num5": numbers[4],
                "num6": numbers[5],
                "bonus": result["bonus"],
                "prize_1st": result.get("prize_1st", 0)
            })

        df = pd.DataFrame(rows)
        df = df.sort_values('draw_no').reset_index(drop=True)
        save_to_excel(df)
        print(f"Saved {len(all_results)} draws to Excel")

    latest_draw = get_latest_draw_from_excel() or CURRENT_DRAW_NO
    return len(all_results), latest_draw


def sync_incremental() -> Tuple[int, int]:
    """Sync new draws only (incremental sync) - alias for update_data."""
    return update_data()


def get_results(
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
    from_draw: Optional[int] = None,
    to_draw: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """Get paginated lotto results from Excel."""
    df = load_from_excel()

    if df is None or len(df) == 0:
        return [], 0

    # Apply filters
    if from_draw is not None:
        df = df[df['draw_no'] >= from_draw]
    if to_draw is not None:
        df = df[df['draw_no'] <= to_draw]

    total = len(df)

    # Sort
    ascending = sort.lower() != "desc"
    df = df.sort_values('draw_no', ascending=ascending)

    # Paginate
    offset = (page - 1) * limit
    df = df.iloc[offset:offset + limit]

    # Convert to list of dicts
    results = []
    for _, row in df.iterrows():
        results.append({
            "draw_no": int(row["draw_no"]),
            "draw_date": str(row["draw_date"]),
            "numbers": [int(row["num1"]), int(row["num2"]), int(row["num3"]),
                       int(row["num4"]), int(row["num5"]), int(row["num6"])],
            "bonus": int(row["bonus"]),
            "prize_1st": int(row["prize_1st"]) if pd.notna(row["prize_1st"]) else 0
        })

    return results, total


def get_result_by_draw_no(draw_no: int) -> Optional[Dict[str, Any]]:
    """Get single lotto result by draw number from Excel."""
    return get_result_by_draw_no_from_excel(draw_no)


def get_all_results_df() -> pd.DataFrame:
    """Get all results as pandas DataFrame for ML processing."""
    return get_all_results_from_excel()


def get_total_draws() -> int:
    """Get total number of draws."""
    return get_total_draws_from_excel()


def get_latest_draw() -> Optional[int]:
    """Get latest draw number."""
    return get_latest_draw_from_excel()
