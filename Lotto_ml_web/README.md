# 로또 Machine Learning 예측

머신러닝 기반 한국 로또 번호 분석 및 예측 웹 애플리케이션

> **면책조항**: 로또는 완전한 무작위 추첨이므로 AI/ML로 정확한 예측이 불가능합니다. 본 서비스는 학습 및 오락 목적으로만 제공됩니다.

## 기능

- **당첨번호 조회**: 1회~1202회 역대 당첨번호 조회 (페이지네이션, 검색)
- **통계 분석**: 번호별 출현 빈도, 홀짝 분포, 합계 분포, 연속번호 통계
- **ML 예측**: Random Forest, Gradient Boosting, Neural Network 3개 모델
- **번호 추천**: 고빈도, 저빈도, 홀짝균형, 구간분산, 합계최적 5가지 전략
- **관리 기능**: 데이터 동기화, 모델 학습

## 기술 스택

### Backend
- Python 3.11+
- FastAPI 0.104+
- Scikit-learn (ML 모델)
- Pandas / NumPy
- SQLite

### Frontend
- React 18 + TypeScript 5
- Vite 5
- Tailwind CSS 3
- Recharts 2
- Axios

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/david1005910/_dev.git
cd _dev/Lotto_ml_web
```

### 2. Backend 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API 문서: http://localhost:8000/docs

### 3. Frontend 실행
```bash
cd frontend
npm install
npm run dev
```
- 웹 앱: http://localhost:5173

### 4. Docker로 실행 (선택)
```bash
docker-compose up --build -d
```

## 사용 방법

1. 관리 페이지에서 "전체 동기화" 클릭 (최초 1회)
2. "모델 학습" 클릭
3. ML 예측 / 추천 페이지에서 결과 확인

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/results` | 당첨번호 목록 |
| GET | `/api/v1/results/{draw_no}` | 특정 회차 조회 |
| GET | `/api/v1/statistics` | 통계 데이터 |
| GET | `/api/v1/predict` | ML 예측 |
| GET | `/api/v1/recommend` | 번호 추천 |
| POST | `/api/v1/sync` | 증분 동기화 |
| POST | `/api/v1/sync/full` | 전체 동기화 |
| POST | `/api/v1/train` | 모델 학습 |
| GET | `/api/v1/status` | 시스템 상태 |

## 프로젝트 구조

```
Lotto_ml_web/
├── backend/
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 환경설정
│   ├── models/              # DB, Pydantic 스키마
│   ├── services/            # 비즈니스 로직
│   ├── routers/             # API 라우터
│   └── tests/               # 테스트
├── frontend/
│   ├── src/
│   │   ├── components/      # 재사용 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   ├── services/        # API 클라이언트
│   │   └── types/           # TypeScript 타입
│   └── ...
├── docker-compose.yml
└── README.md
```

## 라이선스

MIT License
