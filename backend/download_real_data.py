#!/usr/bin/env python3
"""
Download real lotto data from DHLottery API to database.
This script downloads historical lottery data with improved error handling and retry logic.
"""

import requests
import sys
import os
import time
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_database
from services.db_service import LottoDBService
from config import DHLOTTERY_API_URL


def fetch_lotto_result_with_retry(draw_no: int, max_retries: int = 3) -> dict:
    """Fetch lotto result with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"Fetching draw {draw_no} (attempt {attempt + 1}/{max_retries})...")

            response = requests.get(
                DHLOTTERY_API_URL,
                params={"method": "getLottoNumber", "drwNo": draw_no},
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            if response.status_code == 200:
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
                else:
                    print(f"  API returned failure for draw {draw_no}: {data.get('returnValue')}")
                    return None
            else:
                print(f"  HTTP error for draw {draw_no}: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"  Timeout for draw {draw_no} (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError:
            print(f"  Connection error for draw {draw_no} (attempt {attempt + 1})")
        except Exception as e:
            print(f"  Error fetching draw {draw_no}: {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    return None


def find_current_draw_number() -> int:
    """Find the current draw number by checking recent draws."""
    print("Finding current draw number...")

    # Start from a known recent number and work backwards
    for draw_no in range(1200, 1100, -1):
        result = fetch_lotto_result_with_retry(draw_no, max_retries=2)
        if result:
            print(f"Found current draw: {draw_no}")
            return draw_no

    # Default fallback
    print("Using default current draw: 1200")
    return 1200


def download_range(db, start_draw: int, end_draw: int) -> tuple:
    """Download a range of draws."""
    success_count = 0
    error_count = 0

    print(f"Downloading draws {start_draw} to {end_draw}...")

    for draw_no in range(start_draw, end_draw + 1):
        try:
            # Check if draw already exists
            existing = LottoDBService.get_draw_by_number(db, draw_no)
            if existing:
                print(f"  Draw {draw_no} already exists, skipping")
                continue

            # Fetch from API
            draw_data = fetch_lotto_result_with_retry(draw_no)

            if draw_data:
                LottoDBService.add_draw(db, draw_data)
                success_count += 1
                print(f"  Successfully added draw {draw_no}")

                # Progress indicator
                if success_count % 50 == 0:
                    print(f"Progress: {success_count} draws downloaded...")
            else:
                error_count += 1
                print(f"  Failed to fetch draw {draw_no}")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            error_count += 1
            print(f"  Error processing draw {draw_no}: {e}")
            db.rollback()

    return success_count, error_count


def download_real_lotto_data():
    """Main function to download real lotto data."""
    print("Starting real lotto data download...")

    # Initialize database
    init_database()

    db = SessionLocal()
    try:
        # Check current state
        current_db_draw = LottoDBService.get_latest_draw_no(db) or 0
        total_db_draws = LottoDBService.get_total_draws(db)

        print(f"Database status:")
        print(f"  Total draws: {total_db_draws}")
        print(f"  Latest draw: {current_db_draw}")

        # Find current draw number from API
        current_api_draw = find_current_draw_number()

        if current_db_draw >= current_api_draw:
            print("Database is already up to date!")
            return

        # Download strategy
        if current_db_draw == 0:
            # Full download from draw 1
            print("Performing full download from draw 1...")
            start_draw = 1
        else:
            # Incremental download
            print("Performing incremental download...")
            start_draw = current_db_draw + 1

        # Download in batches to avoid overwhelming the API
        batch_size = 100
        total_success = 0
        total_errors = 0

        for batch_start in range(start_draw, current_api_draw + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, current_api_draw)

            print(f"\nDownloading batch: draws {batch_start} to {batch_end}")
            success, errors = download_range(db, batch_start, batch_end)

            total_success += success
            total_errors += errors

            print(f"Batch complete: {success} success, {errors} errors")

            # Short break between batches
            if batch_end < current_api_draw:
                print("Short break between batches...")
                time.sleep(5)

        # Final status
        final_total = LottoDBService.get_total_draws(db)
        final_latest = LottoDBService.get_latest_draw_no(db)

        print(f"\nDownload complete!")
        print(f"  Downloaded: {total_success} draws")
        print(f"  Errors: {total_errors} draws")
        print(f"  Database total: {final_total} draws")
        print(f"  Latest draw: {final_latest}")

    except Exception as e:
        print(f"Error during download: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        download_real_lotto_data()
        print("Real lotto data download completed!")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)