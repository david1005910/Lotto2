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
- SQLite (dev) / PostgreSQL (prod)

### Frontend
- React 18 + TypeScript 5 + Vite 5
- Tailwind CSS 3, Recharts 2, Axios, React Router 6

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

# Manual API test
curl -X POST http://localhost:8000/api/v1/sync/full  # Sync data
curl -X POST http://localhost:8000/api/v1/train       # Train models
curl http://localhost:8000/api/v1/predict             # Get predictions
```

## Architecture

```
React (Vite) → FastAPI → SQLite/PostgreSQL
                  ↓
              ML Models (.pkl files)
                  ↓
          DHLottery External API
```

**Key directories:**
- `backend/routers/` - API route handlers
- `backend/services/` - Business logic (data_service, ml_service, statistics_service, recommend_service)
- `backend/models/` - Database models and Pydantic schemas
- `backend/ml_models/` - Trained model files (.pkl)
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

Model hyperparameters:
- Random Forest: n_estimators=100, max_depth=10
- Gradient Boosting: n_estimators=50, max_depth=5
- MLP: layers=(128,64,32), activation=ReLU

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
