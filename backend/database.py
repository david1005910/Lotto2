"""
Database configuration and models for Lotto ML application.
Using SQLAlchemy with SQLite for data persistence.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{DATA_DIR}/lotto_data.db"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class LottoResult(Base):
    """
    Lotto result model storing historical lottery data.
    """
    __tablename__ = "lotto_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draw_no = Column(Integer, unique=True, nullable=False, index=True)
    draw_date = Column(String(10), nullable=False)  # YYYY-MM-DD format

    # Main numbers (6 numbers, 1-45)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    num4 = Column(Integer, nullable=False)
    num5 = Column(Integer, nullable=False)
    num6 = Column(Integer, nullable=False)

    # Bonus number (1-45)
    bonus = Column(Integer, nullable=False)

    # Prize information
    prize_1st = Column(BigInteger, default=0)  # 1st place prize amount in KRW

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LottoResult(draw_no={self.draw_no}, numbers=[{self.num1},{self.num2},{self.num3},{self.num4},{self.num5},{self.num6}], bonus={self.bonus})>"

    def get_main_numbers(self):
        """Get main numbers as a sorted list."""
        return sorted([self.num1, self.num2, self.num3, self.num4, self.num5, self.num6])

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "draw_no": self.draw_no,
            "draw_date": self.draw_date,
            "numbers": self.get_main_numbers(),
            "bonus": self.bonus,
            "prize_1st": self.prize_1st,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class SystemInfo(Base):
    """
    System information and configuration storage.
    """
    __tablename__ = "system_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(String(500), nullable=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemInfo(key={self.key}, value={self.value})>"


# Create indexes for better performance
Index('idx_lotto_draw_date', LottoResult.draw_date)
Index('idx_lotto_numbers', LottoResult.num1, LottoResult.num2, LottoResult.num3, LottoResult.num4, LottoResult.num5, LottoResult.num6)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def get_db():
    """
    Dependency to get database session.
    Use this in FastAPI endpoints with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database with tables and default data."""
    create_tables()

    # Add default system info
    db = SessionLocal()
    try:
        # Check if system info already exists
        existing = db.query(SystemInfo).filter(SystemInfo.key == "last_sync_draw").first()
        if not existing:
            system_info = SystemInfo(
                key="last_sync_draw",
                value="0",
                description="Last successfully synced draw number"
            )
            db.add(system_info)

            model_status = SystemInfo(
                key="ml_models_trained",
                value="false",
                description="Whether ML models have been trained"
            )
            db.add(model_status)

            db.commit()
            print("Default system information added!")
    except Exception as e:
        print(f"Error initializing system info: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing Lotto database...")
    init_database()
    print("Database initialization complete!")