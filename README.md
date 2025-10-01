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

---

## 시스템 구조

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

## 설치

### 1. Python 환경 설정
```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate

# 패키지 설치 (추후)
pip install -r requirements.txt
```

### 2. Unity 프로젝트
- Unity 프로젝트 위치: `D:\UnityProjects\META_VERYOLD_P01_s\`
- `Calibration_hybrid_OutputManager.cs` 컴포넌트 추가
- 출력 경로: `StreamingAssets/Calibration/Output/simulation_result.json`

---

## 빠른 시작

### Phase 1: 데이터 파이프라인 검증 (완료)

```bash
# 1. Unity에서 시뮬레이션 실행 (수동)
#    - Unity Play 버튼 클릭
#    - 시뮬레이션 완료 대기
#    - StreamingAssets/Calibration/Output/simulation_result.json 생성 확인

# 2. Python으로 결과 파일 읽기
python dev/load_simulation_results.py

# 3. 특정 에이전트 상세 보기
python dev/load_simulation_results.py --agent-id 4236

# 4. 전체 에이전트 상세 통계
python dev/load_simulation_results.py --verbose
```

**Unity 출력 내용**:
- 18개 SFM 파라미터
- 에이전트별 궤적 오차 데이터
- 평균/최대 오차 통계
- 실험 메타데이터 (ID, 시간, 실행시간)

---

### Phase 2: 목적함수 평가 (완료)

```bash
# 기본 평가
python dev/evaluate_objective.py

# 상세 시간 증가율 분석
python dev/evaluate_objective.py --verbose

# 여러 시뮬레이션 결과 비교
python dev/evaluate_objective.py --compare file1.json file2.json
```

**출력 예시**:
```
================================================================================
OBJECTIVE EVALUATION
================================================================================
Experiment ID:       ac86cbf1-ae85-4103-b05d-318105dc8a65
Execution Time:      367.71 seconds
Total Agents:        5008

METRICS BREAKDOWN:
--------------------------------------------------------------------------------
MeanError (50%):            3.6704 m   →     1.8352 weighted
Percentile95 (30%):         5.9518 m   →     1.7855 weighted
TimeGrowthPenalty (20%):    4.8625     →     0.9725 weighted

OBJECTIVE VALUE:        4.5932     (lower is better)
================================================================================
```

**Objective Function**:
- **MeanError (50%)**: 전체 평균 오차 (기본 충실도)
- **Percentile95 (30%)**: 상위 5% 제외 최대 오차 (극단값 방지)
- **TimeGrowthPenalty (20%)**: 초반 vs 후반 오차 증가율 (시간 안정성)

---

### Phase 3: 파라미터 최적화 (개발 예정)

```bash
# 새 파라미터 생성
python generate_parameters.py --objective 0.8234

# Unity 포맷으로 변환
python export_to_unity.py parameters.json data/input/params.json
```

**출력 예시**:
```
Generated new parameters:
- param_1: 1.234
- param_2: 0.567
...
Exported to: data/input/params.json
```

---

### Phase 4: 완전 자동화 (개발 예정)

```bash
python run_optimization.py --iterations 20
```

**출력 예시**:
```
Iteration 1/20: objective = 0.8234
Iteration 2/20: objective = 0.8456
...
Best objective: 0.9123
Best parameters saved to: results/best_params.json
```

---

## 프로젝트 구조

```
calibration_hybrid/
├── data/
│   ├── input/              # Unity가 읽을 파라미터
│   └── output/             # Unity 시뮬레이션 결과
├── dev/                    # 개발 중인 스크립트
├── results/                # 최적화 결과 (자동 생성)
├── .venv/                  # Python 가상환경
├── README.md               # 프로젝트 사용법 (이 파일)
└── CLAUDE.md               # Claude Code 개발 가이드
```

---

## 주요 파일

### Unity 측 (구축 완료)
- `Calibration_hybrid_OutputManager.cs` - 시뮬레이션 결과 수집 및 JSON 출력

### Python 측
**현재 사용 가능** (`dev/` 폴더):
- `load_simulation_results.py` - Unity 결과 로드 및 분석
- `evaluate_objective.py` - 목적함수 평가 (Baseline: 4.5932)

**개발 예정 (Phase별)**:
- `generate_parameters.py` - 파라미터 생성
- `export_to_unity.py` - Unity 포맷 변환
- `run_optimization.py` - 전체 최적화 실행

---

## 현재 상태

- [x] 프로젝트 초기화
- [x] 개발 계획 수립
- [x] Unity Output 시스템 구축
- [x] Phase 1: 데이터 파이프라인 검증 (완료)
  - [x] Unity 출력 시스템 (OutputManager + 파라미터 캐싱)
  - [x] Python 로더 스크립트 (`load_simulation_results.py`)
  - [x] 5008 에이전트, 127,729 trajectory points 검증 완료
- [x] Phase 2: Objective Function 구현 (완료)
  - [x] 3개 메트릭 설계 (MeanError, Percentile95, TimeGrowthPenalty)
  - [x] Baseline objective 측정: 4.5932
  - [x] 시간 누적 오차 분석 (평균 486% 증가 발견)
- [ ] Phase 3: 최적화 알고리즘 연결 (다음 단계)
- [ ] Phase 4: 자동화

---

## 기술 스택

- **Unity**: PIONA 보행 시뮬레이션
  - 위치: `D:\UnityProjects\META_VERYOLD_P01_s\`
  - 스크립트: `Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`
- **Python**: 3.10+
- **라이브러리**: NumPy (현재 사용), Scipy/Optuna (Phase 3에서 추가 예정)
- **데이터 포맷**: JSON
- **파라미터**: 18개 SFM 파라미터 (bounds 정의됨)

---

## 문제 해결

### Unity 결과 파일을 찾을 수 없음
- `data/output/` 디렉토리가 존재하는지 확인
- Unity에서 저장 경로 설정 확인

### Python 스크립트 실행 오류
- 가상환경이 활성화되었는지 확인: `.venv\Scripts\activate`
- 필요한 패키지가 설치되었는지 확인: `pip list`

---

## 참고

자세한 개발 정보, 코드 구조, 이슈 해결은 **CLAUDE.md** 참고