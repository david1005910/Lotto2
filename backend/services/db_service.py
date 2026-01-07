"""
Database service for Lotto ML application.
Handles CRUD operations for lotto data using SQLAlchemy.
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_
from database import LottoResult, SystemInfo, get_db
import pandas as pd
from datetime import datetime
import requests
from config import DHLOTTERY_API_URL


class LottoDBService:
    """Service class for database operations."""

    @staticmethod
    def get_total_draws(db: Session) -> int:
        """Get total number of draws in database."""
        return db.query(LottoResult).count()

    @staticmethod
    def get_latest_draw_no(db: Session) -> Optional[int]:
        """Get latest draw number in database."""
        result = db.query(LottoResult).order_by(desc(LottoResult.draw_no)).first()
        return result.draw_no if result else None

    @staticmethod
    def get_draw_by_number(db: Session, draw_no: int) -> Optional[LottoResult]:
        """Get specific draw by number."""
        return db.query(LottoResult).filter(LottoResult.draw_no == draw_no).first()

    @staticmethod
    def get_draws_paginated(
        db: Session,
        page: int = 1,
        limit: int = 20,
        sort: str = "desc",
        from_draw: Optional[int] = None,
        to_draw: Optional[int] = None
    ) -> Tuple[List[LottoResult], int]:
        """Get paginated lotto results."""
        query = db.query(LottoResult)

        # Apply filters
        if from_draw is not None:
            query = query.filter(LottoResult.draw_no >= from_draw)
        if to_draw is not None:
            query = query.filter(LottoResult.draw_no <= to_draw)

        total = query.count()

        # Apply sorting
        if sort.lower() == "desc":
            query = query.order_by(desc(LottoResult.draw_no))
        else:
            query = query.order_by(asc(LottoResult.draw_no))

        # Apply pagination
        offset = (page - 1) * limit
        results = query.offset(offset).limit(limit).all()

        return results, total

    @staticmethod
    def get_all_draws_for_ml(db: Session) -> pd.DataFrame:
        """Get all draws as pandas DataFrame for ML processing."""
        results = db.query(LottoResult).order_by(asc(LottoResult.draw_no)).all()

        if not results:
            return pd.DataFrame()

        data = []
        for result in results:
            data.append({
                'draw_no': result.draw_no,
                'draw_date': result.draw_date,
                'num1': result.num1,
                'num2': result.num2,
                'num3': result.num3,
                'num4': result.num4,
                'num5': result.num5,
                'num6': result.num6,
                'bonus': result.bonus,
                'prize_1st': result.prize_1st
            })

        return pd.DataFrame(data)

    @staticmethod
    def add_draw(db: Session, draw_data: Dict[str, Any]) -> LottoResult:
        """Add a new draw to database."""
        # Sort main numbers
        numbers = sorted([
            draw_data["numbers"][0], draw_data["numbers"][1], draw_data["numbers"][2],
            draw_data["numbers"][3], draw_data["numbers"][4], draw_data["numbers"][5]
        ])

        draw = LottoResult(
            draw_no=draw_data["draw_no"],
            draw_date=draw_data["draw_date"],
            num1=numbers[0],
            num2=numbers[1],
            num3=numbers[2],
            num4=numbers[3],
            num5=numbers[4],
            num6=numbers[5],
            bonus=draw_data["bonus"],
            prize_1st=draw_data.get("prize_1st", 0)
        )

        db.add(draw)
        db.commit()
        db.refresh(draw)
        return draw

    @staticmethod
    def add_multiple_draws(db: Session, draws_data: List[Dict[str, Any]]) -> int:
        """Add multiple draws to database."""
        added_count = 0

        for draw_data in draws_data:
            try:
                # Check if draw already exists
                existing = db.query(LottoResult).filter(
                    LottoResult.draw_no == draw_data["draw_no"]
                ).first()

                if not existing:
                    LottoDBService.add_draw(db, draw_data)
                    added_count += 1
            except Exception as e:
                print(f"Error adding draw {draw_data.get('draw_no', 'unknown')}: {e}")
                db.rollback()

        return added_count

    @staticmethod
    def fetch_lotto_result_from_api(draw_no: int) -> Optional[Dict[str, Any]]:
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
                    "numbers": [
                        data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                        data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                    ],
                    "bonus": data["bnusNo"],
                    "prize_1st": data.get("firstWinamnt", 0)
                }
            return None
        except Exception as e:
            print(f"Error fetching draw {draw_no} from API: {e}")
            return None

    @staticmethod
    def sync_from_api(db: Session, start_draw: int = 1, end_draw: int = 1200) -> Tuple[int, int]:
        """Sync lotto data from DHLottery API."""
        synced_count = 0
        errors = 0

        print(f"Syncing draws {start_draw} to {end_draw} from DHLottery API...")

        for draw_no in range(start_draw, end_draw + 1):
            try:
                # Check if draw already exists
                existing = db.query(LottoResult).filter(
                    LottoResult.draw_no == draw_no
                ).first()

                if existing:
                    continue

                # Fetch from API
                draw_data = LottoDBService.fetch_lotto_result_from_api(draw_no)
                if draw_data:
                    LottoDBService.add_draw(db, draw_data)
                    synced_count += 1

                    if synced_count % 100 == 0:
                        print(f"Synced {synced_count} draws...")
                else:
                    errors += 1

            except Exception as e:
                print(f"Error syncing draw {draw_no}: {e}")
                errors += 1
                db.rollback()

        latest_draw = LottoDBService.get_latest_draw_no(db)
        print(f"Sync complete! Added {synced_count} draws, {errors} errors")
        return synced_count, latest_draw or 0

    @staticmethod
    def get_system_info(db: Session, key: str) -> Optional[str]:
        """Get system information by key."""
        info = db.query(SystemInfo).filter(SystemInfo.key == key).first()
        return info.value if info else None

    @staticmethod
    def set_system_info(db: Session, key: str, value: str, description: str = None):
        """Set system information."""
        info = db.query(SystemInfo).filter(SystemInfo.key == key).first()
        if info:
            info.value = value
            info.updated_at = datetime.utcnow()
        else:
            info = SystemInfo(key=key, value=value, description=description)
            db.add(info)

        db.commit()

    @staticmethod
    def get_number_frequency(db: Session) -> Dict[int, int]:
        """Get frequency of each lotto number (1-45)."""
        frequency = {}

        # Count each number position
        for i in range(1, 7):  # num1 to num6
            column = getattr(LottoResult, f'num{i}')
            results = db.query(column).all()
            for result in results:
                number = result[0]
                frequency[number] = frequency.get(number, 0) + 1

        return frequency

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """Get comprehensive lotto statistics."""
        total_draws = LottoDBService.get_total_draws(db)
        latest_draw = LottoDBService.get_latest_draw_no(db)
        latest_result = None

        if latest_draw:
            latest_result = LottoDBService.get_draw_by_number(db, latest_draw)

        number_frequency = LottoDBService.get_number_frequency(db)

        return {
            "total_draws": total_draws,
            "latest_draw": latest_draw,
            "latest_result": latest_result.to_dict() if latest_result else None,
            "number_frequency": number_frequency,
            "most_frequent_numbers": sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "least_frequent_numbers": sorted(number_frequency.items(), key=lambda x: x[1])[:10]
        }

    @staticmethod
    def clear_all_draws(db: Session) -> int:
        """Clear all lotto draws from database."""
        try:
            deleted_count = db.query(LottoResult).count()
            db.query(LottoResult).delete()
            db.commit()
            print(f"Cleared {deleted_count} draws from database")
            return deleted_count
        except Exception as e:
            print(f"Error clearing draws: {e}")
            db.rollback()
            return 0

    @staticmethod
    def delete_draw_by_number(db: Session, draw_no: int) -> bool:
        """Delete specific draw by number."""
        try:
            draw = db.query(LottoResult).filter(LottoResult.draw_no == draw_no).first()
            if draw:
                db.delete(draw)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting draw {draw_no}: {e}")
            db.rollback()
            return False