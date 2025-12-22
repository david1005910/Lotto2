# 로또 Machine Learning 예측 웹 애플리케이션 - Constitution

**버전:** 1.0.0  
**비준일:** 2025-12-23  
**최종 수정일:** 2025-12-23

---

## 전문 (Preamble)

이 문서는 "로또 Machine Learning 예측 웹 애플리케이션" 프로젝트의 개발 원칙과 규칙을 정의합니다.
AI 코딩 에이전트와 개발자는 모든 개발 단계에서 이 원칙들을 준수해야 합니다.

> ⚠️ **중요 면책조항:** 로또는 완전한 무작위 추첨이므로 AI/ML로 정확한 예측이 불가능합니다.
> 본 서비스는 학습 및 오락 목적으로만 제공됩니다.

---

## 제1조: 기술 스택 원칙 (Technology Stack Principles)

### 1.1 프론트엔드 (Frontend)
- **필수:** React 18.x + TypeScript 5.x
- **필수:** Vite 5.x (빌드 도구)
- **필수:** Tailwind CSS 3.x (스타일링)
- **필수:** Recharts 2.x (데이터 시각화)
- **필수:** Axios 1.x (HTTP 클라이언트)

### 1.2 백엔드 (Backend)
- **필수:** Python 3.11+
- **필수:** FastAPI 0.104+ (웹 프레임워크)
- **필수:** Scikit-learn 1.3+ (ML 모델)
- **필수:** Pandas 2.0+ / NumPy 1.26+ (데이터 처리)
- **필수:** Uvicorn 0.24+ (ASGI 서버)

### 1.3 데이터베이스 (Database)
- **개발 환경:** SQLite (설정 불필요, 파일 기반)
- **운영 환경:** PostgreSQL 15+ (확장성, JSONB 지원)

### 1.4 금지 사항
- jQuery 또는 레거시 JavaScript 라이브러리 사용 금지
- Flask/Django 대신 FastAPI 사용
- CSS-in-JS 대신 Tailwind CSS 사용

---

## 제2조: 아키텍처 원칙 (Architecture Principles)

### 2.1 3-Tier 아키텍처 준수
```
Presentation Layer (React) → Application Layer (FastAPI) → Data Layer (SQLite/PostgreSQL)
```

### 2.2 API 설계 원칙
- 모든 API는 RESTful 원칙을 따름
- API 버저닝 필수: `/api/v1/...`
- JSON 형식 응답 표준화:
  ```json
  {
    "status": "success" | "error",
    "data": { ... },
    "message": "optional message"
  }
  ```

### 2.3 컴포넌트 분리 원칙
- 프론트엔드: 컴포넌트는 단일 책임 원칙(SRP) 준수
- 백엔드: 라우터, 서비스, 모델 레이어 분리
- 비즈니스 로직은 서비스 레이어에 배치

---

## 제3조: 코드 품질 원칙 (Code Quality Principles)

### 3.1 TypeScript/JavaScript
- ESLint 설정 준수
- 모든 함수/컴포넌트에 TypeScript 타입 정의 필수
- `any` 타입 사용 최소화

### 3.2 Python
- PEP 8 스타일 가이드 준수
- Type hints 필수
- docstring 작성 권장

### 3.3 명명 규칙
- **컴포넌트:** PascalCase (예: `StatisticsChart`)
- **함수/변수:** camelCase (예: `fetchLottoData`)
- **Python 함수/변수:** snake_case (예: `get_lotto_results`)
- **상수:** UPPER_SNAKE_CASE (예: `API_BASE_URL`)
- **파일명:** kebab-case (예: `statistics-chart.tsx`)

---

## 제4조: ML 모델 원칙 (ML Model Principles)

### 4.1 필수 모델
1. **Random Forest:** n_estimators=100, max_depth=10
2. **Gradient Boosting:** n_estimators=50, max_depth=5
3. **Neural Network (MLP):** layers=(128, 64, 32), ReLU

### 4.2 특성 엔지니어링
총 79개 특성 추출 필수:
- 이전 5회차 당첨번호 (30개)
- 홀짝 비율, 고저 비율
- 평균, 표준편차
- 각 번호(1-45)의 상대적 출현 빈도 (45개)

### 4.3 평가 지표
- ±3 범위 내 정확도 측정
- 예측값이 실제값 ±3 범위 내에 있으면 "정확"으로 간주

### 4.4 면책 사항 표시
- 모든 예측 결과에 면책 문구 표시 필수
- 예측 정확도가 30-35% 수준임을 명시

---

## 제5조: 데이터 수집 원칙 (Data Collection Principles)

### 5.1 데이터 소스
- **유일한 소스:** 동행복권 API
- URL: `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={회차}`

### 5.2 데이터 무결성
- 회차 번호 중복 저장 금지 (UNIQUE 제약)
- 당첨번호 범위 검증: 1-45
- 보너스 번호도 1-45 범위

### 5.3 자동 업데이트
- 매주 토요일 추첨 후 자동 업데이트 지원
- 현재 회차: 1202회 (2025년 12월 20일 기준)

---

## 제6조: 보안 및 성능 원칙 (Security & Performance Principles)

### 6.1 보안
- HTTPS 통신 (TLS 1.2+) 권장
- API Rate Limiting 구현
- 입력 값 검증 (SQL Injection 방지)

### 6.2 성능 목표
| 지표 | 목표값 |
|------|--------|
| 페이지 로딩 시간 | < 3초 |
| ML 예측 응답 시간 | < 5초 |
| 서비스 업타임 | > 99% |
| 동시 접속자 | 100+ |

### 6.3 브라우저 지원
- Chrome, Safari, Firefox, Edge 최신 버전

---

## 제7조: 테스트 원칙 (Testing Principles)

### 7.1 테스트 유형
- **Unit Test:** 개별 함수/컴포넌트 테스트
- **Integration Test:** API 엔드포인트 테스트
- **E2E Test:** 사용자 시나리오 테스트 (선택)

### 7.2 테스트 커버리지
- 핵심 비즈니스 로직: 80% 이상
- API 엔드포인트: 100%

---

## 제8조: 문서화 원칙 (Documentation Principles)

### 8.1 필수 문서
- README.md: 프로젝트 개요, 설치/실행 방법
- API 문서: FastAPI 자동 생성 (Swagger/OpenAPI)
- 환경 변수: .env.example 파일 제공

### 8.2 코드 주석
- 복잡한 로직에는 주석 필수
- ML 모델 파라미터 선택 이유 설명

---

## 제9조: 배포 원칙 (Deployment Principles)

### 9.1 지원 플랫폼
- **권장:** Docker + docker-compose
- **대안:** Heroku, Railway, AWS EC2, Vercel + Render

### 9.2 환경 분리
- 개발(dev), 스테이징(staging), 운영(prod) 환경 분리
- 환경별 설정은 환경 변수로 관리

### 9.3 CI/CD
- Git 기반 버전 관리
- 자동 배포 파이프라인 권장

---

## 부칙 (Supplementary Provisions)

### A. 워크플로우 순서
```
/constitution → /specify → /plan → /tasks → /implement
```

### B. 품질 게이트
1. **Specification → Planning:** 모든 기능 요구사항 정의 완료
2. **Planning → Tasks:** 기술 아키텍처 검토 완료
3. **Tasks → Implementation:** 태스크 분류 및 의존성 확인 완료

### C. 예외 처리
- 긴급 수정(Hotfix)의 경우 간소화된 워크플로우 허용
- 단, 사후에 문서 업데이트 필수

---

**문서 끝**
