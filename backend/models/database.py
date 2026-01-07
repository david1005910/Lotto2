import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get SQLite database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotto_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_no INTEGER UNIQUE NOT NULL,
            draw_date TEXT NOT NULL,
            num1 INTEGER NOT NULL CHECK (num1 BETWEEN 1 AND 45),
            num2 INTEGER NOT NULL CHECK (num2 BETWEEN 1 AND 45),
            num3 INTEGER NOT NULL CHECK (num3 BETWEEN 1 AND 45),
            num4 INTEGER NOT NULL CHECK (num4 BETWEEN 1 AND 45),
            num5 INTEGER NOT NULL CHECK (num5 BETWEEN 1 AND 45),
            num6 INTEGER NOT NULL CHECK (num6 BETWEEN 1 AND 45),
            bonus INTEGER NOT NULL CHECK (bonus BETWEEN 1 AND 45),
            prize_1st INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_draw_no ON lotto_results(draw_no)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_draw_date ON lotto_results(draw_date)
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ml_model_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE NOT NULL,
            accuracy REAL,
            trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_total_draws() -> int:
    """Get total number of draws in database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lotto_results")
        result = cursor.fetchone()
        return result[0] if result else 0


def get_latest_draw() -> Optional[int]:
    """Get latest draw number in database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(draw_no) FROM lotto_results")
        result = cursor.fetchone()
        return result[0] if result and result[0] else None
