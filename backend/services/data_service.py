"""
Updated data service using SQLite database instead of Excel files.
Provides the same API interface but with database backend.
"""

from typing import Optional, Dict, List, Tuple, Any
from sqlalchemy.orm import Session
from database import get_db
from services.db_service import LottoDBService
import pandas as pd


# Database session dependency
def get_db_session():
    """Get database session."""
    db = next(get_db())
    try:
        return db
    finally:
        pass  # Session will be closed by the context manager


def fetch_lotto_result(draw_no: int) -> Optional[Dict[str, Any]]:
    """Fetch lotto result from DHLottery API."""
    return LottoDBService.fetch_lotto_result_from_api(draw_no)


def update_data() -> Tuple[int, int]:
    """Update data by fetching new draws from API and saving to database."""
    db = next(get_db())
    try:
        latest_draw = LottoDBService.get_latest_draw_no(db) or 0
        current_draw = 1200  # Approximate current draw number

        print(f"Current latest draw in database: {latest_draw}")
        print(f"Fetching new draws from {latest_draw + 1} to {current_draw}...")

        synced_count, final_latest = LottoDBService.sync_from_api(
            db,
            start_draw=latest_draw + 1,
            end_draw=current_draw
        )

        return synced_count, final_latest

    finally:
        db.close()


def sync_full() -> Tuple[int, int]:
    """Sync all draws from 1 to current (full sync) and save to database."""
    db = next(get_db())
    try:
        current_draw = 1200  # Approximate current draw number
        print(f"Full sync: Fetching draws 1 to {current_draw}...")

        synced_count, latest_draw = LottoDBService.sync_from_api(
            db,
            start_draw=1,
            end_draw=current_draw
        )

        return synced_count, latest_draw

    finally:
        db.close()


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
    """Get paginated lotto results from database."""
    db = next(get_db())
    try:
        results, total = LottoDBService.get_draws_paginated(
            db, page=page, limit=limit, sort=sort,
            from_draw=from_draw, to_draw=to_draw
        )

        # Convert to dictionaries
        results_dict = [result.to_dict() for result in results]
        return results_dict, total

    finally:
        db.close()


def get_result_by_draw_no(draw_no: int) -> Optional[Dict[str, Any]]:
    """Get single lotto result by draw number from database."""
    db = next(get_db())
    try:
        result = LottoDBService.get_draw_by_number(db, draw_no)
        return result.to_dict() if result else None

    finally:
        db.close()


def get_all_results_df() -> pd.DataFrame:
    """Get all results as pandas DataFrame for ML processing."""
    db = next(get_db())
    try:
        return LottoDBService.get_all_draws_for_ml(db)

    finally:
        db.close()


def get_total_draws() -> int:
    """Get total number of draws."""
    db = next(get_db())
    try:
        return LottoDBService.get_total_draws(db)

    finally:
        db.close()


def get_latest_draw() -> Optional[int]:
    """Get latest draw number."""
    db = next(get_db())
    try:
        return LottoDBService.get_latest_draw_no(db)

    finally:
        db.close()


# New database-specific functions
def get_statistics() -> Dict[str, Any]:
    """Get comprehensive lotto statistics."""
    db = next(get_db())
    try:
        return LottoDBService.get_statistics(db)

    finally:
        db.close()


def get_number_frequency() -> Dict[int, int]:
    """Get frequency of each lotto number."""
    db = next(get_db())
    try:
        return LottoDBService.get_number_frequency(db)

    finally:
        db.close()