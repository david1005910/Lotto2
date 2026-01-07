#!/usr/bin/env python3
"""
Load real lotto data from Excel file to database.
Replaces sample data with actual Korean lotto results from round 1 to 1205.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_database
from services.db_service import LottoDBService


def load_excel_data() -> pd.DataFrame:
    """Load real lotto data from Excel file."""
    excel_file = "data/lotto_real_data.xlsx"

    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Excel file not found: {excel_file}")

    print(f"Loading Excel file: {excel_file}")

    # Try different sheet names and structures
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"Excel file shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())

        return df

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise


def convert_to_lotto_format(df: pd.DataFrame) -> list:
    """Convert Excel data to lotto format."""
    lotto_data = []

    print("Converting Excel data to lotto format...")
    print(f"Available columns: {list(df.columns)}")

    # Try to identify columns
    # Common patterns in Korean lotto Excel files
    possible_draw_cols = ['회차', '회', 'draw', 'draw_no', 'Round', 'round']
    possible_date_cols = ['날짜', '추첨일', 'date', 'draw_date', 'Date']
    possible_num_cols = ['당첨번호', '번호', 'numbers']
    possible_bonus_cols = ['보너스', 'bonus', 'Bonus']

    # Find actual column names
    draw_col = None
    date_col = None
    num_cols = []
    bonus_col = None

    for col in df.columns:
        col_str = str(col).lower()
        if any(pattern in col_str for pattern in ['회차', '회', 'draw']):
            draw_col = col
        elif any(pattern in col_str for pattern in ['날짜', '추첨일', 'date']):
            date_col = col
        elif any(pattern in col_str for pattern in ['보너스', 'bonus']):
            bonus_col = col
        elif any(char.isdigit() for char in col_str) or 'num' in col_str or '번호' in col_str:
            if len(num_cols) < 6:
                num_cols.append(col)

    print(f"Detected columns:")
    print(f"  Draw: {draw_col}")
    print(f"  Date: {date_col}")
    print(f"  Numbers: {num_cols}")
    print(f"  Bonus: {bonus_col}")

    # If direct columns not found, try positional approach
    if not draw_col and len(df.columns) > 0:
        draw_col = df.columns[0]
        print(f"Using first column as draw: {draw_col}")

    if not date_col and len(df.columns) > 1:
        date_col = df.columns[1]
        print(f"Using second column as date: {date_col}")

    # If number columns not identified, use sequential columns
    if len(num_cols) < 6 and len(df.columns) >= 8:
        num_cols = df.columns[2:8].tolist()  # Typically columns 2-7
        print(f"Using positional columns for numbers: {num_cols}")

    if not bonus_col and len(df.columns) > 8:
        bonus_col = df.columns[8]
        print(f"Using column as bonus: {bonus_col}")

    # Process each row
    for idx, row in df.iterrows():
        try:
            # Skip if row is empty or invalid
            if pd.isna(row[draw_col]) or row[draw_col] == '':
                continue

            # Extract draw number
            draw_no = int(row[draw_col])

            # Extract date
            draw_date = row[date_col]
            if pd.isna(draw_date):
                draw_date = f"2024-01-01"  # Default date
            else:
                # Convert to string format YYYY-MM-DD
                if isinstance(draw_date, pd.Timestamp):
                    draw_date = draw_date.strftime("%Y-%m-%d")
                else:
                    draw_date = str(draw_date)

            # Extract numbers
            numbers = []
            for col in num_cols:
                if col in row and not pd.isna(row[col]):
                    num = int(row[col])
                    if 1 <= num <= 45:  # Valid lotto number
                        numbers.append(num)

            # Need exactly 6 numbers
            if len(numbers) != 6:
                print(f"Warning: Draw {draw_no} has {len(numbers)} numbers instead of 6, skipping")
                continue

            # Extract bonus
            bonus = 1  # Default bonus
            if bonus_col and bonus_col in row and not pd.isna(row[bonus_col]):
                bonus = int(row[bonus_col])
                if not (1 <= bonus <= 45):
                    bonus = 1

            lotto_data.append({
                "draw_no": draw_no,
                "draw_date": draw_date,
                "numbers": numbers,
                "bonus": bonus,
                "prize_1st": 0  # Will be 0 since prize info might not be in this format
            })

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue

    print(f"Successfully converted {len(lotto_data)} draws")
    return lotto_data


def load_real_data_to_database():
    """Load real lotto data to database."""
    print("Starting real lotto data loading...")

    # Initialize database
    init_database()

    db = SessionLocal()
    try:
        # Load Excel data
        df = load_excel_data()

        # Convert to lotto format
        lotto_data = convert_to_lotto_format(df)

        if not lotto_data:
            print("No valid lotto data found in Excel file!")
            return

        # Clear existing data
        print("\nClearing existing sample data...")
        cleared_count = LottoDBService.clear_all_draws(db)
        print(f"Cleared {cleared_count} existing draws")

        # Load real data
        print(f"\nLoading {len(lotto_data)} real lotto draws...")

        success_count = 0
        error_count = 0

        for draw_data in lotto_data:
            try:
                LottoDBService.add_draw(db, draw_data)
                success_count += 1

                if success_count % 100 == 0:
                    print(f"Loaded {success_count} draws...")

            except Exception as e:
                error_count += 1
                print(f"Error adding draw {draw_data.get('draw_no', 'unknown')}: {e}")
                db.rollback()

        # Final status
        final_total = LottoDBService.get_total_draws(db)
        final_latest = LottoDBService.get_latest_draw_no(db)

        print(f"\n{'='*60}")
        print(f"REAL DATA LOADING COMPLETE!")
        print(f"{'='*60}")
        print(f"  Successfully loaded: {success_count} draws")
        print(f"  Errors encountered: {error_count} draws")
        print(f"  Database total draws: {final_total}")
        print(f"  Latest draw number: {final_latest}")

        if success_count > 1000:
            print(f"🎉 SUCCESS: Loaded {success_count} real lotto draws!")
        else:
            print(f"⚠️  WARNING: Only loaded {success_count} draws")

    except Exception as e:
        print(f"Critical error during loading: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        load_real_data_to_database()
        print("Real lotto data loading completed!")
    except KeyboardInterrupt:
        print("\nLoading interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Loading failed with error: {e}")
        sys.exit(1)