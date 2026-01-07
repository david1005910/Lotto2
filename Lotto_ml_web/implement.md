# 로또 Machine Learning 예측 웹 애플리케이션 - 구현 가이드 (Implement)

**Feature:** 001-lotto-ml-prediction  
**작성일:** 2025-12-23  
**Tasks 참조:** [tasks.md](tasks.md)

---

## 1. 구현 시작 전 체크리스트

### 1.1 필수 확인 사항
- [ ] constitution.md 원칙 숙지
- [ ] spec.md 기능 요구사항 확인
- [ ] plan.md 기술 설계 확인
- [ ] tasks.md 의존성 확인

### 1.2 개발 환경 요구사항
```bash
# Python 버전 확인
python --version  # 3.11+

# Node.js 버전 확인
node --version    # 18+
npm --version     # 9+
```

---

## 2. 구현 순서 가이드

### 2.1 권장 구현 순서

```
1. Phase 1: 프로젝트 초기화
   ├── 백엔드 구조 생성 (Task 1.1.1)
   ├── 의존성 설치 (Task 1.1.2)
   └── 프론트엔드 구조 생성 (Task 1.3.1~1.3.3) [병렬 가능]

2. Phase 2: 백엔드 핵심 기능
   ├── DB 설정 → 데이터 수집 → 통계 → 추천
   └── API 라우터 통합

3. Phase 3: ML 모델
   ├── 특성 추출 → 모델 학습 → 예측
   └── API 통합

4. Phase 4: 프론트엔드
   ├── 공통 컴포넌트 → API 클라이언트
   └── 페이지별 구현

5. Phase 5: 테스트 및 배포
```

---

## 3. 핵심 구현 코드 가이드

### 3.1 백엔드 main.py 구조

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import results, statistics, predict, recommend, admin
from models.database import init_db

app = FastAPI(
    title="로또 Machine Learning 예측 API",
    description="머신러닝 기반 로또 번호 예측 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(results.router, prefix="/api/v1", tags=["results"])
app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])
app.include_router(predict.router, prefix="/api/v1", tags=["predict"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommend"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])

@app.on_event("startup")
async def startup():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.2 데이터베이스 초기화

```python
# backend/models/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "lotto_data.db"

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotto_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_no INTEGER UNIQUE NOT NULL,
            draw_date TEXT NOT NULL,
            num1 INTEGER NOT NULL,
            num2 INTEGER NOT NULL,
            num3 INTEGER NOT NULL,
            num4 INTEGER NOT NULL,
            num5 INTEGER NOT NULL,
            num6 INTEGER NOT NULL,
            bonus INTEGER NOT NULL,
            prize_1st INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
```

### 3.3 동행복권 API 호출

```python
# backend/services/data_service.py
import requests
from typing import Optional, Dict

LOTTO_API_URL = "https://www.dhlottery.co.kr/common.do"

def fetch_lotto_result(draw_no: int) -> Optional[Dict]:
    """동행복권 API에서 당첨번호 조회"""
    try:
        response = requests.get(
            LOTTO_API_URL,
            params={"method": "getLottoNumber", "drwNo": draw_no},
            timeout=10
        )
        data = response.json()
        
        if data.get("returnValue") == "success":
            return {
                "draw_no": data["drwNo"],
                "draw_date": data["drwNoDate"],
                "numbers": sorted([
                    data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                    data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                ]),
                "bonus": data["bnusNo"],
                "prize_1st": data.get("firstWinamnt")
            }
        return None
    except Exception as e:
        print(f"Error fetching draw {draw_no}: {e}")
        return None
```

### 3.4 ML 특성 추출

```python
# backend/services/ml_service.py
import numpy as np
import pandas as pd
from typing import List

def extract_features(df: pd.DataFrame, idx: int) -> List[float]:
    """79개 특성 추출"""
    features = []
    
    # 1. 이전 5회차 당첨번호 (30개)
    for i in range(1, 6):
        if idx - i >= 0:
            prev = df.iloc[idx - i]
            for j in range(1, 7):
                features.append(prev[f'num{j}'])
        else:
            features.extend([0] * 6)
    
    # 2. 이전 회차 홀짝 비율 (1개)
    if idx > 0:
        prev = df.iloc[idx - 1]
        nums = [prev[f'num{j}'] for j in range(1, 7)]
        odd_ratio = sum(1 for n in nums if n % 2 == 1) / 6
    else:
        odd_ratio = 0.5
    features.append(odd_ratio)
    
    # 3. 이전 회차 고저 비율 (1개)
    if idx > 0:
        high_ratio = sum(1 for n in nums if n > 23) / 6
    else:
        high_ratio = 0.5
    features.append(high_ratio)
    
    # 4. 평균/표준편차 (2개)
    if idx > 0:
        features.append(np.mean(nums))
        features.append(np.std(nums))
    else:
        features.extend([23, 10])
    
    # 5. 각 번호 출현 빈도 (45개)
    recent = df.iloc[max(0, idx-100):idx]
    for num in range(1, 46):
        if len(recent) > 0:
            count = sum(
                (recent[f'num{j}'] == num).sum() 
                for j in range(1, 7)
            )
            features.append(count / len(recent))
        else:
            features.append(0)
    
    return features  # 총 79개
```

### 3.5 프론트엔드 LottoBall 컴포넌트

```tsx
// frontend/src/components/LottoBall.tsx
interface LottoBallProps {
  number: number;
  size?: 'sm' | 'md' | 'lg';
  isBonus?: boolean;
}

const getBallColor = (num: number): string => {
  if (num <= 10) return 'bg-yellow-400';
  if (num <= 20) return 'bg-blue-400';
  if (num <= 30) return 'bg-red-400';
  if (num <= 40) return 'bg-gray-400';
  return 'bg-green-400';
};

const getSizeClass = (size: string): string => {
  switch (size) {
    case 'sm': return 'w-8 h-8 text-sm';
    case 'lg': return 'w-14 h-14 text-xl';
    default: return 'w-10 h-10 text-base';
  }
};

export default function LottoBall({ 
  number, 
  size = 'md', 
  isBonus = false 
}: LottoBallProps) {
  return (
    <div
      className={`
        ${getBallColor(number)}
        ${getSizeClass(size)}
        ${isBonus ? 'ring-2 ring-purple-500' : ''}
        rounded-full flex items-center justify-center
        text-white font-bold shadow-md
      `}
    >
      {number}
    </div>
  );
}
```

### 3.6 API 클라이언트

```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

export const api = {
  results: {
    getAll: (params?: { page?: number; limit?: number }) =>
      client.get('/results', { params }),
    getByDrawNo: (drawNo: number) =>
      client.get(`/results/${drawNo}`),
  },
  
  statistics: {
    getAll: (recent?: number) =>
      client.get('/statistics', { params: { recent } }),
  },
  
  predict: {
    get: () => client.get('/predict'),
  },
  
  recommend: {
    get: () => client.get('/recommend'),
  },
  
  admin: {
    sync: () => client.post('/sync'),
    syncFull: () => client.post('/sync/full'),
    train: () => client.post('/train'),
    status: () => client.get('/status'),
  },
};
```

---

## 4. 구현 시 주의사항

### 4.1 Constitution 준수 사항
- ✅ 모든 API는 `/api/v1/` 프리픽스 사용
- ✅ 응답 형식: `{ status, data, message }` 표준 준수
- ✅ TypeScript 타입 정의 필수
- ✅ Python Type hints 필수
- ✅ 예측 결과에 면책 문구 포함

### 4.2 에러 처리
```python
# 백엔드 에러 응답
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="해당 회차를 찾을 수 없습니다."
)
```

```typescript
// 프론트엔드 에러 처리
try {
  const response = await api.results.getAll();
  setData(response.data);
} catch (error) {
  setError('데이터를 불러오는데 실패했습니다.');
}
```

### 4.3 성능 고려사항
- 대량 데이터 동기화 시 배치 처리 (10개씩)
- API 응답 캐싱 고려
- ML 모델은 파일로 저장하여 재사용

---

## 5. 테스트 가이드

### 5.1 백엔드 테스트 실행
```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

### 5.2 API 수동 테스트
```bash
# 1. 서버 실행
uvicorn main:app --reload

# 2. API 문서 확인
open http://localhost:8000/docs

# 3. 데이터 동기화
curl -X POST http://localhost:8000/api/v1/sync/full

# 4. 모델 학습
curl -X POST http://localhost:8000/api/v1/train

# 5. 예측 확인
curl http://localhost:8000/api/v1/predict
```

### 5.3 프론트엔드 테스트
```bash
cd frontend
npm run dev
# http://localhost:5173 에서 확인
```

---

## 6. 배포 체크리스트

### 6.1 배포 전 확인
- [ ] 모든 환경변수 설정 (.env)
- [ ] CORS 설정 (운영 도메인)
- [ ] 에러 핸들링 완료
- [ ] 로깅 설정

### 6.2 Docker 배포
```bash
# 빌드 및 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f
```

---

## 7. 문제 해결 가이드

### 7.1 일반적인 문제

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| CORS 오류 | Origins 설정 누락 | allow_origins에 프론트 URL 추가 |
| DB 연결 실패 | 경로 오류 | DB_PATH 확인 |
| 모델 로드 실패 | 파일 없음 | /train API 먼저 호출 |
| API 타임아웃 | 동행복권 API 지연 | timeout 값 증가 |

### 7.2 디버깅 팁
```python
# FastAPI 디버그 모드
uvicorn main:app --reload --log-level debug
```

```typescript
// React 디버그
console.log('API Response:', response.data);
```

---

## 8. 완료 기준

### 8.1 기능 완료 체크
- [ ] 당첨번호 조회 정상 작동
- [ ] 통계 차트 렌더링 정상
- [ ] ML 예측 결과 표시
- [ ] 추천 번호 표시
- [ ] 데이터 동기화 정상
- [ ] 모델 학습 정상

### 8.2 품질 완료 체크
- [ ] 페이지 로딩 < 3초
- [ ] API 응답 < 5초
- [ ] 반응형 UI 작동
- [ ] 에러 메시지 표시

---

**구현 가이드 끝**
