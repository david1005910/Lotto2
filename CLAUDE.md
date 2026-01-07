# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Korean Lotto (로또) ML prediction web application that collects historical winning numbers from the DHLottery API and provides ML-based number predictions and statistical analysis.

**Important Disclaimer**: Lotto is a random draw - ML predictions are for educational/entertainment purposes only (30-35% accuracy within ±3 range).

## Tech Stack

### Backend
- Python 3.11+, FastAPI 0.104+, Uvicorn
- Scikit-learn (Random Forest, Gradient Boosting, MLP)
- Pandas/NumPy for data processing
- Excel (.xlsx) via openpyxl for data storage

### Frontend
- React 19 + TypeScript 5 + Vite 7
- Tailwind CSS 4, Recharts 3, Axios 1.13, React Router 7

## Build & Run Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
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
```

## Architecture

```
React (Vite) → FastAPI → Excel (.xlsx)
                  ↓
              ML Models (.pkl files)
                  ↓
          DHLottery External API
```

**Key directories:**
- `backend/routers/` - API route handlers
- `backend/services/` - Business logic (data_service, excel_service, ml_service, statistics_service, recommend_service)
- `backend/models/` - Pydantic schemas
- `backend/ml_models/` - Trained model files (.pkl)
- `backend/data/` - Excel data file (lotto_data.xlsx)
- `frontend/src/pages/` - Route pages (Home, Results, Statistics, Predict, Recommend, Admin)
- `frontend/src/components/` - Reusable components (LottoBall, Layout, Navbar)

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

## External API

DHLottery API: `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}`

## Code Style

- TypeScript: ESLint, strict types (minimize `any`)
- Python: PEP 8, type hints required
- Naming: PascalCase (components), camelCase (JS functions), snake_case (Python)
- File names: kebab-case (e.g., `statistics-chart.tsx`)

## Key Constraints

- Never use jQuery or legacy JS libraries
- Use Tailwind CSS, not CSS-in-JS
- All prediction results must include disclaimer text
- Number validation: 1-45 range for all lotto numbers
