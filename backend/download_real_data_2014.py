#!/usr/bin/env python3
"""
Download real lotto data from DHLottery API to database up to draw 2014.
This script replaces sample data with actual historical lottery data.
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


def fetch_lotto_result_with_retry(draw_no: int, max_retries: int = 5) -> dict:
    """Fetch lotto result with enhanced retry logic."""

    # Different API endpoints to try
    api_urls = [
        "https://www.dhlottery.co.kr/common.do",
        "https://dhlottery.co.kr/common.do"
    ]

    for attempt in range(max_retries):
        for api_url in api_urls:
            try:
                print(f"Fetching draw {draw_no} (attempt {attempt + 1}/{max_retries}, API: {api_url[:30]}...)")

                response = requests.get(
                    api_url,
                    params={"method": "getLottoNumber", "drwNo": draw_no},
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                        'Referer': 'https://www.dhlottery.co.kr/',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                )

                print(f"  HTTP Status: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()

                        if data.get("returnValue") == "success":
                            result = {
                                "draw_no": data["drwNo"],
                                "draw_date": data["drwNoDate"],
                                "numbers": [
                                    data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                                    data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                                ],
                                "bonus": data["bnusNo"],
                                "prize_1st": data.get("firstWinamnt", 0)
                            }
                            print(f"  SUCCESS: {result['numbers']} + {result['bonus']}")
                            return result
                        else:
                            print(f"  API returned failure for draw {draw_no}: {data.get('returnValue')}")

                    except Exception as json_error:
                        print(f"  JSON parsing error: {json_error}")
                        print(f"  Response content (first 200 chars): {response.text[:200]}")

                else:
                    print(f"  HTTP error for draw {draw_no}: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"  Timeout for draw {draw_no} (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError as e:
                print(f"  Connection error for draw {draw_no}: {e}")
            except Exception as e:
                print(f"  Unexpected error fetching draw {draw_no}: {e}")

        if attempt < max_retries - 1:
            sleep_time = min(10, 2 ** attempt)  # Cap at 10 seconds
            print(f"  Waiting {sleep_time} seconds before retry...")
            time.sleep(sleep_time)

    return None


def clear_sample_data(db):
    """Clear existing sample data from database."""
    print("Clearing existing sample data...")
    try:
        deleted_count = LottoDBService.clear_all_draws(db)
        print(f"Cleared {deleted_count} sample draws from database")
        return deleted_count
    except Exception as e:
        print(f"Error clearing sample data: {e}")
        return 0


def download_real_data_to_2014():
    """Download real lotto data from draw 1 to 2014."""
    print("Starting download of real lotto data (draws 1-2014)...")

    # Initialize database
    init_database()

    db = SessionLocal()
    try:
        # Clear existing sample data
        clear_sample_data(db)

        # Start downloading from draw 1 to 2014
        target_draw = 2014
        batch_size = 50  # Smaller batches for better reliability
        total_success = 0
        total_errors = 0

        for batch_start in range(1, target_draw + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, target_draw)

            print(f"\n{'='*60}")
            print(f"BATCH: Downloading draws {batch_start} to {batch_end}")
            print(f"{'='*60}")

            batch_success = 0
            batch_errors = 0

            for draw_no in range(batch_start, batch_end + 1):
                try:
                    # Check if draw already exists (in case of resume)
                    existing = LottoDBService.get_draw_by_number(db, draw_no)
                    if existing:
                        print(f"  Draw {draw_no} already exists, skipping")
                        batch_success += 1
                        continue

                    # Fetch from API
                    draw_data = fetch_lotto_result_with_retry(draw_no, max_retries=3)

                    if draw_data:
                        LottoDBService.add_draw(db, draw_data)
                        batch_success += 1
                        total_success += 1

                        # Progress indicator
                        if total_success % 100 == 0:
                            print(f"\n*** MILESTONE: {total_success} draws successfully downloaded! ***\n")

                    else:
                        batch_errors += 1
                        total_errors += 1
                        print(f"  FAILED to fetch draw {draw_no}")

                    # Rate limiting - be nice to the API
                    time.sleep(1.0)

                except Exception as e:
                    batch_errors += 1
                    total_errors += 1
                    print(f"  ERROR processing draw {draw_no}: {e}")
                    db.rollback()

            print(f"\nBatch {batch_start}-{batch_end} complete: {batch_success} success, {batch_errors} errors")

            # Longer break between batches
            if batch_end < target_draw:
                print("Taking a 10-second break between batches...")
                time.sleep(10)

        # Final status
        final_total = LottoDBService.get_total_draws(db)
        final_latest = LottoDBService.get_latest_draw_no(db)

        print(f"\n{'='*60}")
        print(f"DOWNLOAD COMPLETE!")
        print(f"{'='*60}")
        print(f"  Successfully downloaded: {total_success} draws")
        print(f"  Errors encountered: {total_errors} draws")
        print(f"  Database total draws: {final_total}")
        print(f"  Latest draw number: {final_latest}")
        print(f"  Target was: {target_draw}")

        if final_latest == target_draw:
            print(f"🎉 SUCCESS: All {target_draw} draws downloaded!")
        else:
            print(f"⚠️  WARNING: Only reached draw {final_latest} out of target {target_draw}")

    except Exception as e:
        print(f"Critical error during download: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        download_real_data_to_2014()
        print("Real lotto data download to draw 2014 completed!")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Download failed with error: {e}")
        sys.exit(1)