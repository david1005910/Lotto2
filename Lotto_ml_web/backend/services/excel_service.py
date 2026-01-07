import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from config import EXCEL_DATA_PATH


def ensure_data_dir():
    """Ensure data directory exists."""
    EXCEL_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def excel_exists() -> bool:
    """Check if Excel data file exists."""
    return EXCEL_DATA_PATH.exists()


def save_to_excel(df: pd.DataFrame) -> bool:
    """Save DataFrame to Excel file."""
    try:
        ensure_data_dir()
        df.to_excel(EXCEL_DATA_PATH, index=False, engine='openpyxl')
        print(f"Data saved to {EXCEL_DATA_PATH}")
        return True
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return False


def load_from_excel() -> Optional[pd.DataFrame]:
    """Load DataFrame from Excel file."""
    try:
        if not excel_exists():
            return None
        df = pd.read_excel(EXCEL_DATA_PATH, engine='openpyxl')
        print(f"Loaded {len(df)} records from Excel")
        return df
    except Exception as e:
        print(f"Error loading from Excel: {e}")
        return None


def get_latest_draw_from_excel() -> Optional[int]:
    """Get latest draw number from Excel file."""
    df = load_from_excel()
    if df is not None and len(df) > 0:
        return int(df['draw_no'].max())
    return None


def get_total_draws_from_excel() -> int:
    """Get total number of draws from Excel file."""
    df = load_from_excel()
    if df is not None:
        return len(df)
    return 0


def append_to_excel(new_results: List[Dict[str, Any]]) -> bool:
    """Append new results to existing Excel file."""
    try:
        ensure_data_dir()

        # Load existing data
        existing_df = load_from_excel()

        # Convert new results to DataFrame
        new_rows = []
        for result in new_results:
            numbers = result["numbers"]
            new_rows.append({
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

        new_df = pd.DataFrame(new_rows)

        if existing_df is not None and len(existing_df) > 0:
            # Filter out duplicates
            existing_draws = set(existing_df['draw_no'].tolist())
            new_df = new_df[~new_df['draw_no'].isin(existing_draws)]

            if len(new_df) > 0:
                # Append new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df = combined_df.sort_values('draw_no').reset_index(drop=True)
                save_to_excel(combined_df)
                print(f"Appended {len(new_df)} new records")
            else:
                print("No new records to append")
        else:
            # First time save
            new_df = new_df.sort_values('draw_no').reset_index(drop=True)
            save_to_excel(new_df)
            print(f"Created Excel with {len(new_df)} records")

        return True
    except Exception as e:
        print(f"Error appending to Excel: {e}")
        return False


def get_all_results_from_excel() -> pd.DataFrame:
    """Get all results as DataFrame from Excel."""
    df = load_from_excel()
    if df is None:
        return pd.DataFrame()
    return df.sort_values('draw_no').reset_index(drop=True)


def get_result_by_draw_no_from_excel(draw_no: int) -> Optional[Dict[str, Any]]:
    """Get single result by draw number from Excel."""
    df = load_from_excel()
    if df is None:
        return None

    row = df[df['draw_no'] == draw_no]
    if len(row) == 0:
        return None

    row = row.iloc[0]
    return {
        "draw_no": int(row["draw_no"]),
        "draw_date": str(row["draw_date"]),
        "numbers": [int(row["num1"]), int(row["num2"]), int(row["num3"]),
                   int(row["num4"]), int(row["num5"]), int(row["num6"])],
        "bonus": int(row["bonus"]),
        "prize_1st": int(row["prize_1st"]) if pd.notna(row["prize_1st"]) else 0
    }
