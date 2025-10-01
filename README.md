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
- [x] Phase 3: 최적화 알고리즘 연결 (완료 - 테스트 대기)
  - Scipy Differential Evolution
  - Manual mode (사용자가 Unity 수동 실행)
- [ ] Phase 4: 자동화 (개발 예정)

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

## 빠른 시작

### Step 1: 환경 설정 및 Unity 실행
```bash
# Python 환경 준비
.venv\Scripts\activate
pip install -r requirements.txt
```

Unity에서 Calibration scene 실행 → 시뮬레이션 완료 대기 (5-10분)

### Step 2: 결과 분석
```bash
# Unity 결과 확인
python dev/load_simulation_results.py

# Objective 평가
python dev/evaluate_objective.py
# 출력: Baseline Objective = 4.5932
```

### Step 3: 최적화 시작
```bash
# Baseline 파라미터 생성
python dev/generate_parameters.py --baseline

# 테스트 최적화 (2 iterations)
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5
```

각 iteration마다 Unity 수동 실행 필요 → Phase 4에서 자동화 예정

---

## 상세 사용법

### Phase 1-2: 데이터 검증 및 평가

```bash
# 기본 로드 및 분석
python dev/load_simulation_results.py

# Objective 평가
python dev/evaluate_objective.py

# 상세 옵션
python dev/load_simulation_results.py --verbose --agent-id 4236
python dev/evaluate_objective.py --verbose
python dev/evaluate_objective.py --compare result1.json result2.json
```

**Objective Function** (Lower is better):
```
Objective = 0.50 * MeanError + 0.30 * Percentile95 + 0.20 * TimeGrowth
Baseline: 4.5932
```

### Phase 3: 파라미터 최적화

**Optimization Algorithm**: Scipy Differential Evolution (population-based, gradient-free)

#### 기본 사용법

```bash
# 1. Baseline 파라미터 생성
python dev/generate_parameters.py --baseline

# 2. Unity JSON 변환 (선택사항)
python dev/export_to_unity.py --input data/input/baseline_parameters.json --auto-id

# 3. 테스트 최적화 (2 iterations, ~10 evaluations)
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5

# 4. 전체 최적화 (50 iterations, ~750 evaluations, 1-3일 소요)
python dev/generate_parameters.py --optimize --manual --maxiter 50 --popsize 15
```

#### 최적화 실행 흐름 (Manual Mode)

1. Python이 새 파라미터 생성 → Unity JSON 저장
2. 화면에 "Press ENTER after Unity simulation completes..." 표시
3. **사용자가 Unity Play 버튼 클릭 → 시뮬레이션 실행 (수동)**
4. 시뮬레이션 완료 후 Python 콘솔에서 ENTER
5. Python이 결과 로드 → Objective 계산
6. Differential Evolution이 다음 파라미터 생성
7. 반복...

#### 출력 파일

- `data/output/optimization_history.csv` - 전체 평가 이력
- `data/output/best_parameters.json` - 최고 성능 파라미터

---

## Quick Reference

| 스크립트 | 용도 | 주요 옵션 |
|---------|------|----------|
| `load_simulation_results.py` | Unity 결과 로드 | `--verbose`, `--agent-id` |
| `evaluate_objective.py` | Objective 계산 | `--verbose`, `--compare` |
| `export_to_unity.py` | Python → Unity 변환 | `--input`, `--auto-id` |
| `generate_parameters.py` | 파라미터 생성/최적화 | `--baseline`, `--optimize --manual` |

**자주 사용하는 커맨드**:
```bash
python dev/evaluate_objective.py
python dev/generate_parameters.py --baseline
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5
```

---

## 프로젝트 구조

```
calibration_hybrid/
├── data/
│   ├── input/              # Python → Unity 파라미터
│   └── output/             # Unity → Python 결과
├── dev/                    # Python 스크립트
│   ├── load_simulation_results.py
│   ├── evaluate_objective.py
│   ├── export_to_unity.py
│   └── generate_parameters.py
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

**Optimization이 개선되지 않음**:
- Local minimum 가능성: population size 증가 (`--popsize 20`)
- 더 많은 generation: `--maxiter 100`
- Optimization history 분석: `data/output/optimization_history.csv`

---

## 참고

- **CLAUDE.md**: 개발 가이드, 코드 구조, 알고리즘 상세 설명
- **Unity C# Scripts**: `D:\UnityProjects\...\Calibration_hybrid\`