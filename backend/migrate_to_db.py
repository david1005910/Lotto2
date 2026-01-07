#!/usr/bin/env python3
"""
Migration script to move data from Excel to Database.
This script migrates existing lotto data from Excel format to SQLite database.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_database
from services.db_service import LottoDBService
from services.excel_service import load_from_excel


def migrate_excel_to_db():
    """Migrate data from Excel file to database."""
    print("Starting migration from Excel to Database...")

    # Initialize database
    init_database()

    # Load existing Excel data
    print("Loading Excel data...")
    df = load_from_excel()

    if df is None or len(df) == 0:
        print("No Excel data found. Skipping migration.")
        return

    print(f"Found {len(df)} records in Excel file")

    # Convert DataFrame to list of dictionaries
    draws_data = []
    for _, row in df.iterrows():
        draw_data = {
            "draw_no": int(row["draw_no"]),
            "draw_date": str(row["draw_date"]),
            "numbers": [
                int(row["num1"]), int(row["num2"]), int(row["num3"]),
                int(row["num4"]), int(row["num5"]), int(row["num6"])
            ],
            "bonus": int(row["bonus"]),
            "prize_1st": int(row["prize_1st"]) if pd.notna(row["prize_1st"]) else 0
        }
        draws_data.append(draw_data)

    # Insert into database
    print("Inserting data into database...")
    db = SessionLocal()
    try:
        added_count = LottoDBService.add_multiple_draws(db, draws_data)
        print(f"Successfully migrated {added_count} draws to database")

        # Verify migration
        total_in_db = LottoDBService.get_total_draws(db)
        latest_draw = LottoDBService.get_latest_draw_no(db)
        print(f"Database now contains {total_in_db} draws")
        print(f"Latest draw number: {latest_draw}")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()


def test_database_operations():
    """Test basic database operations."""
    print("\nTesting database operations...")

    db = SessionLocal()
    try:
        # Test basic queries
        total = LottoDBService.get_total_draws(db)
        latest = LottoDBService.get_latest_draw_no(db)
        print(f"Total draws: {total}")
        print(f"Latest draw: {latest}")

        if latest:
            # Get latest draw details
            latest_result = LottoDBService.get_draw_by_number(db, latest)
            if latest_result:
                print(f"Latest result: {latest_result.to_dict()}")

        # Test pagination
        results, total_paginated = LottoDBService.get_draws_paginated(db, page=1, limit=5)
        print(f"First 5 draws (paginated): {len(results)} results")

        # Test statistics
        stats = LottoDBService.get_statistics(db)
        print(f"Statistics: {stats['total_draws']} draws, latest: {stats['latest_draw']}")

        print("Database operations test completed successfully!")

    except Exception as e:
        print(f"Error during database test: {e}")
    finally:
        db.close()


def main():
    """Main migration function."""
    try:
        # Run migration
        migrate_excel_to_db()

        # Test database
        test_database_operations()

        print("\nMigration completed successfully!")
        print("The application can now use the database instead of Excel files.")

    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()