# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Korean Lotto (로또) ML prediction web application that collects historical winning numbers from the DHLottery API and provides ML-based number predictions and statistical analysis.

**Important Disclaimer**: Lotto is a random draw - ML predictions are for educational/entertainment purposes only (30-35% accuracy within ±3 range).

## Tech Stack

### Backend
- Python 3.11+, FastAPI 0.104+, Uvicorn
- SQLAlchemy 2.0+ with SQLite database
- Scikit-learn (Random Forest, Gradient Boosting, MLP)
- Pandas/NumPy for data processing
- Alembic for database migrations

### Frontend
- React 19 + TypeScript 5 + Vite 7
- Tailwind CSS 4, Recharts 3, Axios 1.13, React Router 7

## Build & Run Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
python database.py  # Initialize SQLite database
uvicorn main:app --reload --port 8000
# API docs: http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev
# App: http://localhost:5173

# Docker
docker-compose up --build -d
```

## Testing

```bash
# Backend tests
cd backend
pip install pytest httpx
pytest tests/ -v

# Frontend linting
cd frontend
npm run lint

# Manual API test
curl -X POST http://localhost:8000/api/v1/sync/full  # Sync data
curl -X POST http://localhost:8000/api/v1/train       # Train models
curl http://localhost:8000/api/v1/predict             # Get predictions

# Database operations
python migrate_to_db.py  # Migrate from Excel to database (if needed)
python load_real_data.py  # Load real historical data
```

## Architecture

```
React (Vite) → FastAPI → SQLite Database
                  ↓
              ML Models (.pkl files)
                  ↓
          DHLottery External API
```

**Key directories:**
- `backend/routers/` - API route handlers
- `backend/services/` - Business logic (data_service, db_service, ml_service, statistics_service, recommend_service)
- `backend/models/` - Database models and Pydantic schemas
- `backend/ml_models/` - Trained model files (.pkl)
- `backend/data/` - SQLite database file (lotto_data.db) and backup Excel files
- `backend/database.py` - SQLAlchemy models and database configuration
- `frontend/src/pages/` - Route pages (Home, Results, Statistics, Predict, Recommend, Admin)
- `frontend/src/components/` - Reusable components (LottoBall, Layout, Navbar)

**Data Layer Services:**
- `data_service.py` - Main data service using database
- `db_service.py` - Database operations with SQLAlchemy
- `excel_service.py` - Excel file operations (backup/migration)
- `*_excel_backup.py` - Legacy Excel-based service implementations

## API Design Conventions

- All endpoints prefixed with `/api/v1/`
- Response format: `{ "status": "success"|"error", "data": {...}, "message": "..." }`
- Lotto ball colors by number range:
  - 1-10: yellow (#FBC400)
  - 11-20: blue (#69C8F2)
  - 21-30: red (#FF7272)
  - 31-40: gray (#AAAAAA)
  - 41-45: green (#B0D840)

## ML Model Details

Three models with 79 features:
- Previous 5 draws (30 features)
- Odd/even ratio, high/low ratio (2 features)
- Mean/standard deviation (2 features)
- Per-number frequency 1-45 (45 features)

Model hyperparameters (optimized to prevent overfitting):
- Random Forest: n_estimators=100, max_depth=6, min_samples_split=10
- Gradient Boosting: n_estimators=50, max_depth=3, min_samples_split=10
- MLP: layers=(64,32), alpha=0.01, early_stopping=True

Model evaluation:
- Train/Test Split: 80/20
- Accuracy metric: ±3 range
- Test accuracy: ~35-37%

## Database Schema

**LottoResult table:**
- `draw_no` (int, unique) - Draw number (1, 2, 3...)
- `draw_date` (string) - Draw date in YYYY-MM-DD format
- `num1-num6` (int) - Main winning numbers (sorted 1-45)
- `bonus` (int) - Bonus number (1-45)
- `prize_1st` (bigint) - First prize amount in KRW

**SystemInfo table:**
- Key-value store for system configuration
- `last_sync_draw` - Last successfully synced draw number
- `ml_models_trained` - Whether ML models have been trained

## External API

DHLottery API: `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}`

## Code Style

- TypeScript: ESLint, strict types (minimize `any`)
- Python: PEP 8, type hints required
- Naming: PascalCase (components), camelCase (JS functions), snake_case (Python)
- File names: kebab-case (e.g., `statistics-chart.tsx`)

## Database Migration & Development Workflow

**For new database setup:**
1. Run `python database.py` to initialize SQLite database
2. Use `python load_real_data.py` to load historical data (1-1205 draws)
3. Run `python main.py` or `uvicorn main:app --reload` to start API

**For Excel-to-database migration:**
1. Run `python migrate_to_db.py` to migrate existing Excel data
2. Verify data integrity with API endpoints
3. Backup files are preserved in `*_excel_backup.py`

**Database operations:**
- Use `LottoDBService` class for all database operations
- Database session management through `get_db()` dependency injection
- Real-time data sync from DHLottery API with retry logic

## Key Constraints

- Never use jQuery or legacy JS libraries
- Use Tailwind CSS, not CSS-in-JS
- All prediction results must include disclaimer text
- Number validation: 1-45 range for all lotto numbers
- Always use database transactions for data integrity
- Prefer database operations over Excel file manipulation
