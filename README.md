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
- [x] Phase 2: Objective Function 구현 (완료 - Baseline: 4.5932)
- [x] Phase 3: 최적화 알고리즘 연결 (완료 - 아카이브됨)
- [x] **Phase 4B: Optimizer Abstraction Layer (완료 - 2025-10-16)**
  - ✅ 모듈화된 최적화 시스템 (core/, optimizer/, analysis/)
  - ✅ Unity Editor 완전 자동화 (파일 트리거 시스템)
  - ✅ 알고리즘 교체 가능한 구조 (SCI 논문 대비)
  - ✅ Input-Output 1:1 매칭 (완전한 추적 가능성)
  - ✅ 유니크 히스토리 파일 (실험 비교 용이)
  - ✅ 자동 분석 및 그래프 생성
  - ✅ 테스트 완료 (TESTING.md 5단계 검증)

**상태**: 프로덕션 최적화 준비 완료 (750 evaluations, ~3일 소요)

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

### Step 3: 자동 최적화 실행
```bash
# 테스트 실행 (10 evaluations, ~1시간)
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5

# 프로덕션 실행 (750 evaluations, ~3일)
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42
```

**자동으로 실행됨**:
- Python이 파라미터 생성
- Unity가 자동으로 시뮬레이션 실행 (파일 트리거 방식)
- 결과 자동 평가 및 다음 파라미터 생성
- 최적화 완료 후 convergence plot 자동 생성

### Step 4: 결과 확인
최적화 완료 후 자동 생성된 파일들:
- `data/output/best_parameters.json` - 최적 파라미터
- `data/output/optimization_history_*.csv` - 최적화 히스토리
- `data/output/optimization_history_*.png` - 수렴 그래프
- `data/output/result_*.json` - 전체 결과

---

## 상세 사용법

### Phase 4B: 자동 최적화 (메인 사용법)

**Optimization Algorithm**: Scipy Differential Evolution (population-based, gradient-free)

#### 완전 자동화 모드 (권장)
```bash
# Unity Editor 열어둔 상태에서 실행
python dev/run_optimization.py --algorithm scipy_de --max-evals 100 --popsize 10

# 고급 옵션
python dev/run_optimization.py \
  --algorithm scipy_de \
  --max-evals 750 \
  --popsize 15 \
  --strategy best1bin \
  --seed 42 \
  --timeout 1200
```

**옵션 설명**:
- `--max-evals`: 총 시뮬레이션 실행 횟수
- `--popsize`: 세대당 개체 수 (큰 값 = 더 넓은 탐색)
- `--strategy`: 진화 전략 (best1bin, rand1bin 등)
- `--seed`: 재현성을 위한 랜덤 시드
- `--timeout`: 시뮬레이션당 최대 대기 시간 (초)

**자동 생성 파일**:
- `optimization_history_ScipyDE_pop15_best1bin_20251016_163602.csv` - 유니크 히스토리
- `optimization_history_ScipyDE_pop15_best1bin_20251016_163602.png` - 수렴 그래프
- `result_ScipyDE_pop15_best1bin_20251016_163602.json` - 메타데이터
- `best_parameters.json` - 최적 파라미터

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
Objective = 0.50 * MeanError + 0.30 * Percentile95 + 0.20 * TimeGrowth
Baseline: 4.5932
```

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
# 테스트 최적화 (10 evaluations, ~1시간)
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5

# 프로덕션 최적화 (750 evaluations, ~3일)
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42

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

**Unity 결과 파일을 찾을 수 없음**:
- Unity 시뮬레이션이 정상 완료되었는지 확인
- 출력 경로: `StreamingAssets/Calibration/Output/simulation_result.json`

**Python 스크립트 실행 오류**:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
pip list  # 설치 확인
```

**Unity Editor가 자동 실행되지 않음**:
- Unity Editor가 열려 있는지 확인
- `Calibration_Hybrid.unity` scene이 로드되어 있는지 확인
- 콘솔에서 `[AutomationController] File trigger system initialized` 메시지 확인

**Optimization이 개선되지 않음**:
- Convergence plot 확인: `data/output/optimization_history_*.png`
- Local minimum 가능성: population size 증가 (`--popsize 20`)
- 더 많은 evaluations: `--max-evals 1000`

**시뮬레이션이 중간에 멈춤**:
- Unity 콘솔에서 에러 메시지 확인
- Timeout 증가: `--timeout 1200` (기본 600초 → 1200초)

---

## 참고

- **CLAUDE.md**: 개발 가이드, 코드 구조, 알고리즘 상세 설명
- **Unity C# Scripts**: `D:\UnityProjects\...\Calibration_hybrid\`