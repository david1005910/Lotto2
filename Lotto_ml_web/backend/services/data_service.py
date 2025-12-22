import requests
import pandas as pd
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime

from config import DHLOTTERY_API_URL, CURRENT_DRAW_NO
from models.database import get_db, get_latest_draw, get_total_draws


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
                "prize_1st": data.get("firstWinamnt")
            }
        return None
    except Exception as e:
        print(f"Error fetching draw {draw_no}: {e}")
        return None


def save_result(result: Dict[str, Any]) -> bool:
    """Save lotto result to database."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            numbers = result["numbers"]
            cursor.execute('''
                INSERT OR IGNORE INTO lotto_results
                (draw_no, draw_date, num1, num2, num3, num4, num5, num6, bonus, prize_1st)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result["draw_no"],
                result["draw_date"],
                numbers[0], numbers[1], numbers[2],
                numbers[3], numbers[4], numbers[5],
                result["bonus"],
                result["prize_1st"]
            ))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error saving result: {e}")
        return False


def sync_incremental() -> Tuple[int, int]:
    """Sync new draws only (incremental sync)."""
    latest_db = get_latest_draw() or 0
    synced_count = 0

    for draw_no in range(latest_db + 1, CURRENT_DRAW_NO + 1):
        result = fetch_lotto_result(draw_no)
        if result and save_result(result):
            synced_count += 1

    latest_draw = get_latest_draw() or CURRENT_DRAW_NO
    return synced_count, latest_draw


def sync_full() -> Tuple[int, int]:
    """Sync all draws from 1 to current (full sync)."""
    synced_count = 0

    for draw_no in range(1, CURRENT_DRAW_NO + 1):
        result = fetch_lotto_result(draw_no)
        if result and save_result(result):
            synced_count += 1

        if draw_no % 100 == 0:
            print(f"Synced {draw_no} draws...")

    latest_draw = get_latest_draw() or CURRENT_DRAW_NO
    return synced_count, latest_draw


def get_results(
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
    from_draw: Optional[int] = None,
    to_draw: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """Get paginated lotto results."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Build query
        where_clauses = []
        params: List[Any] = []

        if from_draw is not None:
            where_clauses.append("draw_no >= ?")
            params.append(from_draw)
        if to_draw is not None:
            where_clauses.append("draw_no <= ?")
            params.append(to_draw)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM lotto_results {where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        order = "DESC" if sort.lower() == "desc" else "ASC"
        offset = (page - 1) * limit

        query_sql = f'''
            SELECT draw_no, draw_date, num1, num2, num3, num4, num5, num6, bonus, prize_1st
            FROM lotto_results
            {where_sql}
            ORDER BY draw_no {order}
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])

        cursor.execute(query_sql, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "draw_no": row["draw_no"],
                "draw_date": row["draw_date"],
                "numbers": [row["num1"], row["num2"], row["num3"],
                           row["num4"], row["num5"], row["num6"]],
                "bonus": row["bonus"],
                "prize_1st": row["prize_1st"]
            })

        return results, total


def get_result_by_draw_no(draw_no: int) -> Optional[Dict[str, Any]]:
    """Get single lotto result by draw number."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT draw_no, draw_date, num1, num2, num3, num4, num5, num6, bonus, prize_1st
            FROM lotto_results
            WHERE draw_no = ?
        ''', (draw_no,))
        row = cursor.fetchone()

        if row:
            return {
                "draw_no": row["draw_no"],
                "draw_date": row["draw_date"],
                "numbers": [row["num1"], row["num2"], row["num3"],
                           row["num4"], row["num5"], row["num6"]],
                "bonus": row["bonus"],
                "prize_1st": row["prize_1st"]
            }
        return None


def get_all_results_df() -> pd.DataFrame:
    """Get all results as pandas DataFrame for ML processing."""
    with get_db() as conn:
        df = pd.read_sql_query('''
            SELECT draw_no, draw_date, num1, num2, num3, num4, num5, num6, bonus, prize_1st
            FROM lotto_results
            ORDER BY draw_no ASC
        ''', conn)
    return df
