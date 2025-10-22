# calibration_hybrid

**MIMLAB : Parameter Calibration for PIONA**

---

## 📋 문서 목적 및 작성 규칙

**대상**: 사람 (개발자, 사용자, 팀원)
**목적**: 프로젝트 이해, 설치 방법, 사용법 안내

**업데이트 규칙**:
- 사용자 관점에서 "무엇을", "어떻게 사용"하는지 중심
- 새로운 기능이 완성되면 "빠른 시작" 섹션 업데이트
- 새로운 의존성 추가 시 "설치" 섹션 업데이트
- 프로젝트 구조 변경 시 "프로젝트 구조" 섹션 업데이트
- **개발 세부사항, 코드 구조, 이슈는 CLAUDE.md에 기록**

---

## 프로젝트 개요

Unity PIONA 보행 시뮬레이션의 파라미터를 실제 데이터에 맞게 자동으로 최적화하는 시스템입니다.

**핵심 아이디어**:
- Unity: 고성능 시뮬레이션 실행
- Python: 결과 분석 및 최적화 알고리즘

**시스템 구조**:
```
Python (파라미터 생성)
    ↓
Unity (시뮬레이션 실행)
    ↓
Python (결과 평가 → 새 파라미터)
    ↓
반복...
```

---

## 현재 상태

- [x] Phase 1: 데이터 파이프라인 검증 (완료)
- [x] Phase 2: Objective Function 구현 (완료)
- [x] Phase 3: 최적화 알고리즘 연결 (완료 - 아카이브됨)
- [x] **Phase 4B: Optimizer Abstraction Layer (완료 - 2025-10-16)**
  - ✅ 모듈화된 최적화 시스템 (core/, optimizer/, analysis/)
  - ✅ Unity Editor 완전 자동화 (파일 트리거 시스템)
  - ✅ 알고리즘 교체 가능한 구조 (SCI 논문 대비)
- [x] **Phase 4C: Resume System (완료 - 2025-10-22)**
  - ✅ 체크포인트 기반 중단/재개 시스템
  - ✅ 파일 아카이빙 (Unity 성능 유지)
  - ✅ 정확한 결과 리포팅 (best iteration/generation 추적)
- [x] **Phase 4B+: Objective Function 강화 (완료 - 2025-10-17)**
  - ✅ 밀도 메트릭 추가 (군중 행동 검증)
  - ✅ RMSE 메트릭 (문헌 표준)
  - ✅ TimeGrowth 선형회귀 개선
  - ✅ Generation 추적 기능
  - ✅ 새 Baseline: **2.8254**
- [x] **Production Run 준비 완료 (2025-10-20)**
  - ✅ Input-Output 1:1 매칭 (완전한 추적 가능성)
  - ✅ 유니크 히스토리 파일 (실험 비교 용이)
  - ✅ 자동 분석 및 그래프 생성
  - ✅ Race condition 버그 수정 (JSON 파싱 오류 해결)

**상태**: 프로덕션 최적화 진행중 (436/720 완료, ~33시간 남음)

**최근 업데이트**:
- ✅ **Resume System 구현 (2025-10-22)** - 중단/재개 가능, 체크포인트 기반
- ✅ **파일 아카이빙 (2025-10-22)** - Unity 성능 유지 (400+ 파일 문제 해결)
- ✅ **결과 정확도 개선 (2025-10-22)** - best iteration/generation 추적

---

## 설치

```bash
# 1. Python 가상환경 활성화
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Unix/Mac

# 2. 패키지 설치
pip install -r requirements.txt
```

**Unity 프로젝트**:
- 위치: `D:\UnityProjects\META_VERYOLD_P01_s\`
- 출력 경로: `StreamingAssets/Calibration/Output/simulation_result.json`

---

## 빠른 시작 (Phase 4B - 완전 자동화)

### Step 1: 환경 설정
```bash
# Python 환경 준비
.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Unity Editor 실행
- Unity 프로젝트 열기: `D:\UnityProjects\META_VERYOLD_P01_s\`
- Scene 로드: `Calibration_Hybrid.unity`
- **Unity Editor를 그대로 둔 채로 다음 단계 진행** (자동화됨)

### Step 3: 자동 최적화 실행 (또는 재개)

**새로 시작**:
```bash
# 기본 실행 (720 evaluations, ~2-3일) - 가장 간단!
python dev/run_optimization.py --algorithm scipy_de

# 빠른 테스트 (36 evaluations, ~5시간)
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

# 더 많은 탐색 (1350 evaluations, ~5일)
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5
```

**중단된 최적화 재개**:
```bash
# 체크포인트에서 재개 (정확한 상태 복원)
python dev/run_optimization.py --algorithm scipy_de --resume
```

**자동으로 실행됨**:
- Python이 파라미터 생성
- Unity가 자동으로 시뮬레이션 실행 (파일 트리거 방식)
- 결과 자동 평가 및 다음 파라미터 생성
- 최적화 완료 후 convergence plot 자동 생성

**참고**:
- Seed는 기본적으로 매번 자동 생성됩니다 (다양성 확보)
- 자동 생성된 시드는 결과 파일에 저장되어 나중에 재현 가능
- 재현이 필요한 실험에서만 `--seed 42` 처럼 직접 지정

### Step 4: 결과 확인
최적화 완료 후 자동 생성된 파일들:
- `data/output/best_parameters.json` - 최적 파라미터
- `data/output/history_*.csv` - 최적화 히스토리 (generation, 모든 메트릭 포함)
- `data/output/history_*.png` - 수렴 그래프
- `data/output/result_*.json` - 전체 결과 (best iteration/generation, 시드 포함)
- `data/output/checkpoint_latest.pkl` - 체크포인트 (resume용)
- 콘솔에 재현 명령어 자동 출력

**아카이브** (자동 생성):
- `data/input/parameters/` - 모든 입력 파라미터 저장 (eval_0001~eval_0720)
- `data/output/results/` - 모든 결과 파일 저장 (eval_0001~eval_0720)

---

## 상세 사용법

### Phase 4B: 자동 최적화 (메인 사용법)

**Optimization Algorithm**: Scipy Differential Evolution (population-based, gradient-free)

#### 완전 자동화 모드 (권장)
```bash
# Unity Editor 열어둔 상태에서 실행

# 기본 실행 (가장 간단, 권장)
python dev/run_optimization.py --algorithm scipy_de
# → popsize=10, generations=4 → 720 evals

# 빠른 테스트
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1
# → 36 evals (~5시간)

# 더 많은 탐색 (큰 population)
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5
# → 1350 evals (~5일)

# 재현 가능한 실험 (seed 지정)
python dev/run_optimization.py --algorithm scipy_de --seed 42

# 고급 옵션
python dev/run_optimization.py \
  --algorithm scipy_de \
  --popsize 10 \
  --generations 4 \
  --strategy best1bin \
  --seed 42 \
  --timeout 1200
```

**주요 옵션 설명**:
- `--popsize`: 탐색 범위 (기본값: 10, 권장: 5-15)
  - 값이 클수록 더 넓은 영역 탐색 (느림)
- `--generations`: 진화 세대 수 (기본값: 4, 권장: 3-10)
  - 값이 클수록 더 정교한 수렴 (느림)
- `--seed`: 랜덤 시드 (기본값: None = 자동 생성)
  - 자동 생성된 시드는 결과 파일에 저장되어 재현 가능
  - 재현 필요시만 직접 지정: `--seed 42`
- `--max-evals`: [고급] 강제 평가 제한 (선택사항)

**실제 평가 횟수**: `popsize`와 `generations` 값에 따라 자동 계산
- 기본값: **720회** (약 2-3일 소요)
- 빠른 테스트: **36회** (약 5시간)
- 더 많은 탐색: **1350회** (약 5일)

**자동 생성 파일** (`data/output/` 디렉토리):
- `best_parameters.json` - 최적 파라미터 (메인 결과)
- `optimization_history_*.csv` - 전체 평가 히스토리
- `optimization_history_*.png` - 수렴 그래프
- `result_*.json` - 메타데이터 (seed, 알고리즘 설정 등)

**재현성**: 콘솔 출력과 result JSON에 자동 생성된 seed가 저장되므로, `--seed` 옵션으로 동일한 결과 재현 가능

### 유틸리티: 데이터 검증 및 평가

```bash
# Unity 결과 확인
python dev/load_simulation_results.py
python dev/load_simulation_results.py --verbose --agent-id 4236

# Objective 평가
python dev/evaluate_objective.py
python dev/evaluate_objective.py --verbose
python dev/evaluate_objective.py --compare result1.json result2.json
```

**Objective Function** (Lower is better):
```
Objective = 0.40 * RMSE + 0.25 * Percentile95 + 0.15 * TimeGrowth + 0.20 * DensityDiff
```

**메트릭 설명**:
- **RMSE** (40%): 개별 궤적 정확도 (Root Mean Square Error, 문헌 표준)
- **Percentile95** (25%): 이상치 제어 (하위 95% 에이전트 평균)
- **TimeGrowth** (15%): 시간 안정성 (선형회귀 기울기)
- **DensityDiff** (20%): 군중 밀도 일치도 (40×40 그리드, 2.5m 셀)

**Baseline**: 재측정 필요 (이전: MAE 기반 4.5932)

### 아카이브: Phase 3 수동 모드

Phase 3의 수동 최적화 모드는 `archive/phase3/`로 이동되었습니다.
필요시 다음과 같이 사용 가능:

```bash
# Phase 3 수동 모드 (아카이브됨)
python archive/phase3/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5
# 각 evaluation마다 Unity Play 버튼 수동 클릭 필요

# 상세 내용은 archive/phase3/README.md 참조
```

---

## Quick Reference

**메인 스크립트**:
| 스크립트 | 용도 | 주요 옵션 |
|---------|------|----------|
| `run_optimization.py` | **자동 최적화 (메인)** | `--algorithm scipy_de`, `--max-evals`, `--popsize`, `--seed` |
| `load_simulation_results.py` | Unity 결과 확인 | `--verbose`, `--agent-id` |
| `evaluate_objective.py` | Objective 계산 | `--verbose`, `--compare` |

**자주 사용하는 커맨드**:
```bash
# 기본 최적화 (720 evals, ~2-3일) - 가장 간단!
python dev/run_optimization.py --algorithm scipy_de

# 빠른 테스트 (36 evals, ~5시간)
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

# 더 많은 탐색 (1350 evals, ~5일)
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5

# Unity 결과 확인
python dev/load_simulation_results.py --verbose

# Objective 평가
python dev/evaluate_objective.py
```

---

## 프로젝트 구조

```
calibration_hybrid/
├── data/
│   ├── input/              # [생성됨] Python → Unity 파라미터
│   └── output/             # [생성됨] Unity → Python 결과, 히스토리, 그래프
├── dev/                    # Python 스크립트
│   ├── run_optimization.py              # 메인 실행 파일
│   ├── core/                             # 핵심 모듈
│   │   ├── unity_simulator.py           # Unity 자동화
│   │   ├── objective_function.py        # 평가 함수
│   │   ├── parameter_utils.py           # 파라미터 유틸리티
│   │   └── history_tracker.py           # 히스토리 추적
│   ├── optimizer/                        # 최적화 알고리즘
│   │   ├── base_optimizer.py            # 추상 인터페이스
│   │   └── scipy_de_optimizer.py        # Scipy DE 구현
│   ├── analysis/                         # 결과 분석
│   │   └── analyze_history.py           # 수렴 그래프 생성
│   ├── evaluate_objective.py             # Objective 계산 유틸
│   ├── export_to_unity.py                # Python → Unity 변환
│   ├── load_simulation_results.py        # Unity 결과 로드
│   └── TESTING.md                        # 테스트 가이드
├── archive/
│   └── phase3/                           # Phase 3 수동 모드 (아카이브)
├── requirements.txt
├── README.md               # 사용법 (이 파일)
└── CLAUDE.md               # 개발자 가이드
```

**Unity 프로젝트**: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`

---

## 기술 스택

- **Unity**: PIONA 보행 시뮬레이션
- **Python 3.10+**: NumPy, Scipy (Differential Evolution), Matplotlib, tqdm
- **데이터**: JSON format, 18 SFM parameters with bounds

---

## 문제 해결

### 시작 전 체크리스트
- [ ] Python 가상환경 활성화: `.venv\Scripts\activate`
- [ ] 패키지 설치: `pip install -r requirements.txt`
- [ ] Unity Editor 열기: `D:\UnityProjects\META_VERYOLD_P01_s\`
- [ ] Scene 로드: `Calibration_Hybrid.unity` (**Calibration.unity 아님**)

### 자주 발생하는 문제

**JSON 파싱 오류** (`JSONDecodeError`):
- **원인**: Unity가 65MB 파일을 쓰는 중에 Python이 읽으려 시도 (race condition)
- **해결**: 2025-10-20 패치로 자동 해결됨 (파일 안정성 체크 추가)
- 여전히 발생 시: `git pull` 후 재실행

**실행 안됨**:
- Unity Editor가 열려 있는지 확인
- Unity 콘솔에서 `[AutomationController] File trigger system initialized` 메시지 확인

**Python 오류**:
```bash
pip install -r requirements.txt
```

**최적화 개선 안됨**:
- `data/output/optimization_history_*.png` 그래프 확인
- 값이 평평하면 수렴 완료 (정상)
- 더 탐색: `--popsize 15 --generations 5`

**자세한 문제 해결**: `dev/TESTING.md` 참조

---

## 참고

- **CLAUDE.md**: 개발 가이드, 코드 구조, 알고리즘 상세 설명
- **Unity C# Scripts**: `D:\UnityProjects\...\Calibration_hybrid\`