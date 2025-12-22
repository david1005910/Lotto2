# 로또 Machine Learning 예측 웹 애플리케이션 - 기술 계획서 (Plan)

**Feature:** 001-lotto-ml-prediction  
**Branch:** 001-lotto-ml-prediction  
**작성일:** 2025-12-23  
**Spec 참조:** [spec.md](spec.md)

---

## 1. 기술 스택 상세 (Tech Stack Details)

### 1.1 프론트엔드 (Frontend)

| 기술 | 버전 | 용도 | 설치 명령어 |
|------|------|------|------------|
| React | 18.x | UI 컴포넌트 라이브러리 | (Vite 포함) |
| TypeScript | 5.x | 타입 안정성 | (Vite 포함) |
| Vite | 5.x | 빌드 도구 | `npm create vite@latest` |
| Recharts | 2.x | 데이터 시각화 차트 | `npm install recharts` |
| Tailwind CSS | 3.x | CSS 프레임워크 | `npm install -D tailwindcss postcss autoprefixer` |
| Axios | 1.x | HTTP 클라이언트 | `npm install axios` |
| React Router | 6.x | 라우팅 | `npm install react-router-dom` |

### 1.2 백엔드 (Backend)

| 기술 | 버전 | 용도 | 설치 명령어 |
|------|------|------|------------|
| Python | 3.11+ | 프로그래밍 언어 | - |
| FastAPI | 0.104+ | 웹 프레임워크 | `pip install fastapi` |
| Uvicorn | 0.24+ | ASGI 서버 | `pip install uvicorn[standard]` |
| Scikit-learn | 1.3+ | ML 모델 | `pip install scikit-learn` |
| Pandas | 2.0+ | 데이터 처리 | `pip install pandas` |
| NumPy | 1.26+ | 수치 연산 | `pip install numpy` |
| Requests | 2.31+ | HTTP 클라이언트 | `pip install requests` |
| Joblib | 1.3+ | 모델 저장/로드 | `pip install joblib` |

### 1.3 데이터베이스 (Database)

| 환경 | DB | 설명 |
|------|-----|------|
| 개발 | SQLite | `lotto_data.db` 파일 기반 |
| 운영 | PostgreSQL 15+ | 선택적 (환경변수로 전환) |

---

## 2. 시스템 아키텍처 (System Architecture)

### 2.1 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              React + TypeScript + Vite               │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │   │
│   │  │   Home   │ │ Results  │ │Statistics│ │Predict │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │   │
│   │  ┌──────────┐ ┌──────────┐                          │   │
│   │  │Recommend │ │  Admin   │      Tailwind + Recharts │   │
│   │  └──────────┘ └──────────┘                          │   │
│   └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP (REST API)
                             │ JSON
┌────────────────────────────▼────────────────────────────────┐
│                        SERVER                                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              FastAPI + Python 3.11+                  │   │
│   │  ┌──────────────────────────────────────────────┐   │   │
│   │  │                  Routers                      │   │   │
│   │  │  /results  /statistics  /predict  /recommend │   │   │
│   │  │  /sync     /train       /status              │   │   │
│   │  └──────────────────────────────────────────────┘   │   │
│   │  ┌──────────────────────────────────────────────┐   │   │
│   │  │                 Services                      │   │   │
│   │  │  DataService  MLService  StatisticsService   │   │   │
│   │  └──────────────────────────────────────────────┘   │   │
│   │  ┌──────────────────────────────────────────────┐   │   │
│   │  │              ML Models (Scikit-learn)         │   │   │
│   │  │  RandomForest  GradientBoosting  MLP         │   │   │
│   │  └──────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLite / PostgreSQL
┌────────────────────────────▼────────────────────────────────┐
│                       DATABASE                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   lotto_results                      │   │
│   │  id | draw_no | draw_date | num1-6 | bonus | prize  │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  ML Model Files                      │   │
│   │  scaler.pkl | rf.pkl | gb.pkl | mlp.pkl             │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   EXTERNAL API                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              동행복권 API                             │   │
│   │  GET /common.do?method=getLottoNumber&drwNo={n}     │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 데이터 흐름 (Data Flow)

```
[동행복권 API] → [DataService] → [SQLite DB]
                                      ↓
                              [StatisticsService]
                                      ↓
                                [MLService]
                                      ↓
                              [Model Files (.pkl)]
                                      ↓
                              [API Response]
                                      ↓
                              [React Frontend]
```

---

## 3. 프로젝트 구조 (Project Structure)

```
lotto-ml-web/
├── .specify/                    # Spec-Kit 문서
│   ├── memory/
│   │   └── constitution.md
│   ├── specs/
│   │   └── 001-lotto-ml-prediction/
│   │       ├── spec.md
│   │       ├── plan.md
│   │       └── tasks.md
│   └── templates/
│
├── backend/                     # FastAPI 백엔드
│   ├── main.py                  # 애플리케이션 진입점
│   ├── requirements.txt         # Python 의존성
│   ├── config.py                # 설정 관리
│   │
│   ├── routers/                 # API 라우터
│   │   ├── __init__.py
│   │   ├── results.py           # 당첨번호 API
│   │   ├── statistics.py        # 통계 API
│   │   ├── predict.py           # 예측 API
│   │   ├── recommend.py         # 추천 API
│   │   └── admin.py             # 관리 API (sync, train)
│   │
│   ├── services/                # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── data_service.py      # 데이터 수집/저장
│   │   ├── statistics_service.py # 통계 계산
│   │   ├── ml_service.py        # ML 학습/예측
│   │   └── recommend_service.py # 추천 로직
│   │
│   ├── models/                  # 데이터 모델
│   │   ├── __init__.py
│   │   ├── schemas.py           # Pydantic 스키마
│   │   └── database.py          # DB 연결/테이블
│   │
│   ├── ml_models/               # 학습된 ML 모델 저장
│   │   ├── scaler.pkl
│   │   ├── random_forest.pkl
│   │   ├── gradient_boosting.pkl
│   │   └── neural_network.pkl
│   │
│   ├── data/                    # 데이터 저장
│   │   └── lotto_data.db        # SQLite 데이터베이스
│   │
│   └── tests/                   # 테스트
│       ├── __init__.py
│       ├── test_results.py
│       └── test_ml.py
│
├── frontend/                    # React 프론트엔드
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   │
│   ├── src/
│   │   ├── main.tsx             # 엔트리 포인트
│   │   ├── App.tsx              # 메인 컴포넌트
│   │   ├── index.css            # 글로벌 스타일 (Tailwind)
│   │   │
│   │   ├── components/          # 재사용 컴포넌트
│   │   │   ├── Layout.tsx       # 레이아웃
│   │   │   ├── Navbar.tsx       # 네비게이션 바
│   │   │   ├── LottoBall.tsx    # 로또 공 컴포넌트
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   │
│   │   ├── pages/               # 페이지 컴포넌트
│   │   │   ├── Home.tsx
│   │   │   ├── Results.tsx
│   │   │   ├── Statistics.tsx
│   │   │   ├── Predict.tsx
│   │   │   ├── Recommend.tsx
│   │   │   └── Admin.tsx
│   │   │
│   │   ├── services/            # API 호출
│   │   │   └── api.ts
│   │   │
│   │   └── types/               # TypeScript 타입
│   │       └── index.ts
│   │
│   └── public/                  # 정적 파일
│       └── favicon.ico
│
├── docker-compose.yml           # Docker 구성
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example                 # 환경변수 예시
├── .gitignore
└── README.md
```

---

## 4. API 설계 상세 (API Design Details)

### 4.1 GET /api/v1/results

**설명:** 당첨번호 목록 조회

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | N | 페이지 번호 (기본: 1) |
| limit | int | N | 페이지당 항목 수 (기본: 20, 최대: 100) |
| sort | string | N | 정렬 순서 (desc/asc, 기본: desc) |
| from_draw | int | N | 시작 회차 |
| to_draw | int | N | 종료 회차 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "draw_no": 1202,
        "draw_date": "2025-12-20",
        "numbers": [3, 12, 18, 24, 35, 41],
        "bonus": 7,
        "prize_1st": 2543000000
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1202,
      "total_pages": 61
    }
  }
}
```

### 4.2 GET /api/v1/results/{draw_no}

**설명:** 특정 회차 조회

**Path Parameters:**
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| draw_no | int | 회차 번호 |

**Response:**
```json
{
  "status": "success",
  "data": {
    "draw_no": 1202,
    "draw_date": "2025-12-20",
    "numbers": [3, 12, 18, 24, 35, 41],
    "bonus": 7,
    "prize_1st": 2543000000
  }
}
```

### 4.3 GET /api/v1/statistics

**설명:** 전체 통계 조회

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| recent | int | N | 최근 N회차만 (기본: 전체) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "number_frequency": {
      "1": 150, "2": 145, ... "45": 138
    },
    "odd_even_distribution": {
      "0_odd": 5, "1_odd": 25, "2_odd": 150, "3_odd": 520, "4_odd": 350, "5_odd": 120, "6_odd": 32
    },
    "sum_distribution": {
      "ranges": ["61-80", "81-100", "101-120", "121-140", "141-160", "161-180", "181-200"],
      "counts": [15, 85, 250, 452, 280, 95, 25]
    },
    "consecutive_stats": {
      "has_consecutive": 650,
      "no_consecutive": 552
    },
    "section_distribution": {
      "low_1_15": {"avg": 2.1, "distribution": {...}},
      "mid_16_30": {"avg": 2.0, "distribution": {...}},
      "high_31_45": {"avg": 1.9, "distribution": {...}}
    },
    "total_draws": 1202
  }
}
```

### 4.4 POST /api/v1/sync

**설명:** 증분 데이터 동기화 (새 회차만)

**Response:**
```json
{
  "status": "success",
  "data": {
    "synced_count": 5,
    "latest_draw": 1202
  },
  "message": "5개 회차 동기화 완료"
}
```

### 4.5 POST /api/v1/sync/full

**설명:** 전체 데이터 동기화 (1회~현재)

**Response:**
```json
{
  "status": "success",
  "data": {
    "synced_count": 1202,
    "latest_draw": 1202
  },
  "message": "전체 1202개 회차 동기화 완료"
}
```

### 4.6 POST /api/v1/train

**설명:** ML 모델 학습

**Response:**
```json
{
  "status": "success",
  "data": {
    "models": {
      "random_forest": {"accuracy": 0.32, "trained": true},
      "gradient_boosting": {"accuracy": 0.31, "trained": true},
      "neural_network": {"accuracy": 0.33, "trained": true}
    },
    "trained_at": "2025-12-23T10:30:00Z",
    "training_samples": 1197
  },
  "message": "모델 학습 완료"
}
```

### 4.7 GET /api/v1/predict

**설명:** ML 모델 예측

**Response:**
```json
{
  "status": "success",
  "data": {
    "predictions": {
      "random_forest": {
        "numbers": [7, 14, 23, 31, 38, 42],
        "accuracy": 0.32
      },
      "gradient_boosting": {
        "numbers": [5, 12, 21, 29, 36, 44],
        "accuracy": 0.31
      },
      "neural_network": {
        "numbers": [3, 18, 25, 33, 40, 45],
        "accuracy": 0.33
      }
    },
    "disclaimer": "로또는 무작위 추첨이므로 예측이 불가능합니다. 이 결과는 참고용입니다.",
    "last_trained": "2025-12-23T10:30:00Z"
  }
}
```

### 4.8 GET /api/v1/recommend

**설명:** 통계 기반 번호 추천

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": {
      "high_frequency": {
        "numbers": [34, 17, 27, 1, 12, 43],
        "description": "역대 출현 빈도가 높은 번호 조합"
      },
      "low_frequency": {
        "numbers": [9, 22, 39, 4, 29, 15],
        "description": "최근 오래 출현하지 않은 번호 조합"
      },
      "balanced_odd_even": {
        "numbers": [3, 17, 25, 8, 22, 40],
        "description": "홀수 3개, 짝수 3개 균형 조합"
      },
      "section_spread": {
        "numbers": [7, 14, 19, 26, 35, 42],
        "description": "저/중/고 구간 균등 분포 조합"
      },
      "optimal_sum": {
        "numbers": [11, 18, 23, 29, 35, 41],
        "description": "합계 130-150 범위 최적 조합"
      }
    }
  }
}
```

### 4.9 GET /api/v1/status

**설명:** 시스템 상태 확인

**Response:**
```json
{
  "status": "success",
  "data": {
    "database": {
      "total_draws": 1202,
      "latest_draw": 1202,
      "latest_date": "2025-12-20"
    },
    "ml_models": {
      "trained": true,
      "last_trained": "2025-12-23T10:30:00Z",
      "models_available": ["random_forest", "gradient_boosting", "neural_network"]
    },
    "last_sync": "2025-12-23T10:00:00Z"
  }
}
```

---

## 5. ML 모델 설계 상세

### 5.1 특성 엔지니어링 (Feature Engineering)

**총 79개 특성:**

```python
def extract_features(df, idx):
    features = []
    
    # 1. 이전 5회차 당첨번호 (30개)
    for i in range(1, 6):
        prev_row = df.iloc[idx - i]
        for j in range(1, 7):
            features.append(prev_row[f'num{j}'])
    
    # 2. 이전 회차 홀짝 비율 (1개)
    prev_nums = [prev_row[f'num{j}'] for j in range(1, 7)]
    odd_ratio = sum(1 for n in prev_nums if n % 2 == 1) / 6
    features.append(odd_ratio)
    
    # 3. 이전 회차 고저 비율 (1개) - 기준: 23
    high_ratio = sum(1 for n in prev_nums if n > 23) / 6
    features.append(high_ratio)
    
    # 4. 이전 회차 평균/표준편차 (2개)
    features.append(np.mean(prev_nums))
    features.append(np.std(prev_nums))
    
    # 5. 각 번호(1-45)의 최근 100회차 출현 빈도 (45개)
    recent_100 = df.iloc[max(0, idx-100):idx]
    for num in range(1, 46):
        count = sum(
            (recent_100[f'num{j}'] == num).sum() 
            for j in range(1, 7)
        )
        features.append(count / min(100, idx) if idx > 0 else 0)
    
    return features  # 총 79개
```

### 5.2 모델 구성

```python
# Random Forest
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

# Gradient Boosting
gb_model = GradientBoostingRegressor(
    n_estimators=50,
    max_depth=5,
    random_state=42
)

# Neural Network (MLP)
mlp_model = MLPRegressor(
    hidden_layer_sizes=(128, 64, 32),
    activation='relu',
    max_iter=500,
    random_state=42
)
```

### 5.3 예측 프로세스

```python
def predict_numbers(model, scaler, features):
    # 1. 특성 스케일링
    scaled_features = scaler.transform([features])
    
    # 2. 6개 번호 각각 예측
    predictions = []
    for i in range(6):
        pred = model.predict(scaled_features)[0]
        # 번호 범위 보정 (1-45)
        pred = max(1, min(45, round(pred)))
        predictions.append(pred)
    
    # 3. 중복 제거 및 정렬
    predictions = list(set(predictions))
    while len(predictions) < 6:
        new_num = random.randint(1, 45)
        if new_num not in predictions:
            predictions.append(new_num)
    
    return sorted(predictions[:6])
```

---

## 6. 프론트엔드 컴포넌트 설계

### 6.1 컴포넌트 계층 구조

```
App
├── Layout
│   ├── Navbar
│   └── Main Content
│       ├── Home
│       │   ├── StatusCard
│       │   ├── LatestResults
│       │   └── QuickActions
│       │
│       ├── Results
│       │   ├── SearchFilter
│       │   ├── ResultsTable
│       │   ├── LottoBall (repeated)
│       │   └── Pagination
│       │
│       ├── Statistics
│       │   ├── FrequencyChart
│       │   ├── OddEvenChart
│       │   ├── SumDistributionChart
│       │   └── SectionChart
│       │
│       ├── Predict
│       │   ├── PredictionCard (x3)
│       │   ├── LottoBall (repeated)
│       │   └── Disclaimer
│       │
│       ├── Recommend
│       │   ├── RecommendCard (x5)
│       │   └── LottoBall (repeated)
│       │
│       └── Admin
│           ├── SyncButton
│           ├── TrainButton
│           └── StatusInfo
```

### 6.2 주요 컴포넌트 Props/State

```typescript
// LottoBall.tsx
interface LottoBallProps {
  number: number;
  size?: 'sm' | 'md' | 'lg';
  isBonus?: boolean;
}

// ResultsTable.tsx
interface ResultsTableProps {
  results: LottoResult[];
  loading: boolean;
}

// FrequencyChart.tsx
interface FrequencyChartProps {
  data: NumberFrequency;
  recent?: number;
}

// PredictionCard.tsx
interface PredictionCardProps {
  modelName: string;
  numbers: number[];
  accuracy: number;
}
```

---

## 7. 데이터베이스 마이그레이션

### 7.1 초기 테이블 생성

```sql
-- V1: 초기 스키마
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
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_draw_no ON lotto_results(draw_no);
CREATE INDEX IF NOT EXISTS idx_draw_date ON lotto_results(draw_date);
```

---

## 8. 환경 변수

### 8.1 .env.example

```bash
# Database
DATABASE_URL=sqlite:///./data/lotto_data.db
# PostgreSQL 예시: postgresql://user:password@localhost:5432/lotto

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# External API
DHLOTTERY_API_URL=https://www.dhlottery.co.kr/common.do
CURRENT_DRAW_NO=1202

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# ML Models
MODEL_PATH=./ml_models
```

---

## 9. 품질 게이트 (Quality Gates)

### 9.1 Specification → Planning ✅
- [x] 모든 User Story 정의 완료
- [x] 기능/비기능 요구사항 명세 완료
- [x] 데이터 모델 정의 완료
- [x] API 엔드포인트 목록 정의 완료

### 9.2 Planning → Tasks
- [ ] 기술 스택 확정
- [ ] 시스템 아키텍처 확정
- [ ] 프로젝트 구조 확정
- [ ] API 상세 설계 완료
- [ ] ML 모델 설계 완료

### 9.3 Tasks → Implementation
- [ ] 태스크 분류 완료
- [ ] 의존성 확인 완료
- [ ] 예상 소요 시간 산정

---

## 10. 릴리즈 계획 (Release Plan)

| Phase | 기간 | 목표 |
|-------|------|------|
| Phase 1 | 2일 | 프로젝트 초기화, DB 설계, 데이터 수집 |
| Phase 2 | 3일 | 백엔드 API 개발 |
| Phase 3 | 2일 | ML 모델 개발 및 통합 |
| Phase 4 | 3일 | 프론트엔드 개발 |
| Phase 5 | 1일 | 테스트 및 배포 |

**총 예상 기간:** 약 11일

---

**문서 끝**
