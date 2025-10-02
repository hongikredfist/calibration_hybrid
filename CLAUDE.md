# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🤖 Claude Code를 위한 업데이트 가이드라인

**대상**: Claude Code (AI 개발 어시스턴트)
**목적**: 새 세션마다 작업 컨텍스트 복원, 개발 가이드라인 제공

**업데이트 규칙** (사용자가 ".md 문서를 각각 작성 규칙에 맞게 업데이트 해줘" 요청 시):
1. **"📍 현재 작업 상태"** 섹션 업데이트
   - 어느 Phase인지
   - 어떤 파일을 작업 중인지
   - 완료된 작업 체크

2. **"🎯 다음 작업"** 섹션 업데이트
   - 바로 다음에 해야 할 작업
   - 완료 조건
   - 예상 파일명

3. **"📝 개발 중 발견사항"** 섹션에 추가
   - 발견한 이슈
   - 내린 설계 결정
   - 변경된 데이터 포맷
   - 주의사항

4. **"✅ 완료된 작업"** 섹션에 추가
   - 완료한 Phase/파일
   - 주요 기능
   - 파일 위치

**절대 변경하지 말 것**: "🛠️ Development Philosophy", "🏗️ System Architecture" (핵심 원칙)

---

## 🎯 Project Identity

**calibration_hybrid** - Unity-Python Hybrid Parameter Calibration System for PIONA

- **PIONA**: Pedestrian Intelligence for Oriented Navigation Architecture (보행 시뮬레이션)
- **목표**: Unity 시뮬레이션 파라미터를 실제 데이터에 맞게 자동 최적화
- **전략**: Unity(시뮬레이션) + Python(최적화/분석) 분리 아키텍처

---

## 🏗️ System Architecture

```
Unity (시뮬레이션)  ←→  Python (최적화)
     ↓                      ↓
 JSON/CSV              파라미터 생성
```

**워크플로우**: Python 파라미터 생성 → Unity 시뮬레이션 → Python 결과 평가 → 반복

---

## 🛠️ Development Philosophy

### ✅ DO
- **수동 검증 가능한 개별 모듈** 작성
- **단일 스크립트**로 독립 실행 가능하게
- **각 단계별 안정성 확인** 후 다음 단계
- **필요한 것만** 만들기
- 간결하고 명확한 코드

### ❌ DON'T
- 처음부터 완전 자동화 시도
- 복잡한 클래스 구조 만들기
- 불필요한 기능 추가
- 볼륨 증가시키기

---

## 📍 현재 작업 상태

**현재 Phase**: Phase 3 완료 (Phase 4 대기)
**현재 작업**: Phase 4 자동화 구현 준비
**작업 중인 파일**: N/A

### 완료 항목
- [x] 프로젝트 초기화
- [x] README.md 작성 (사용자 대상)
- [x] CLAUDE.md 작성 (Claude Code 대상)
- [x] 개발 계획 수립
- [x] data/input, data/output 디렉토리 생성
- [x] Unity OutputManager 구현 (`Calibration_hybrid_OutputManager.cs`)
  - 18 SFM 파라미터 수집
  - 에이전트별 오차 데이터 수집
  - JSON 파일 저장
  - 파라미터 캐싱 (에이전트 destroy 문제 해결)
- [x] Phase 1: `load_simulation_results.py` 구현 완료
  - JSON 파일 로드 및 파싱
  - 18개 파라미터 검증
  - 에이전트 오차 통계 출력
  - 특정 에이전트 상세 조회 기능
- [x] Phase 1: Unity → Python 데이터 파이프라인 검증 완료
- [x] Phase 2: `evaluate_objective.py` 구현 완료
  - Objective Function 설계 (3개 메트릭)
  - MeanError (50%), Percentile95 (30%), TimeGrowthPenalty (20%)
  - Baseline objective: 4.5932
  - Verbose mode로 worst time-growth agents 분석
  - Compare mode로 여러 시뮬레이션 결과 비교
- [x] Phase 3: `export_to_unity.py` 구현 완료
  - Python parameters → Unity JSON 변환
  - Experiment ID 자동 생성
  - 파라미터 검증 및 clamping
  - StreamingAssets/Input/ 경로 저장
- [x] Phase 3: `generate_parameters.py` 구현 완료 및 수정
  - Scipy Differential Evolution 통합
  - Baseline parameter 생성
  - Manual mode (Phase 3용)
  - Optimization history tracking (CSV)
  - 18-parameter bounds 적용
  - **Iteration counting 버그 수정 (2025-01-XX)**
    - `maxiter * popsize`로 총 평가 횟수 정확히 제한
    - StopIteration → RuntimeError 발생 → Callback 방식으로 최종 해결
    - Scipy의 `callback` 메커니즘으로 정상 종료 처리
  - **Optimization history 분석 기능 추가 (2025-01-XX)**
    - `--analyze` mode 추가
    - Summary statistics (best/worst/mean/std)
    - Best objective per generation
    - Convergence plot (matplotlib)
  - **Baseline objective 저장 및 비교 기능 추가 (2025-01-XX)**
    - `load_baseline_objective()` - 파일에서 baseline 자동 로드
    - Optimization 및 분석 시 baseline과 자동 비교
    - Convergence plot에 baseline 수평선 표시
- [x] Phase 3: `evaluate_objective.py` 수정
  - **Baseline 저장 기능 추가 (2025-01-XX)**
    - `save_baseline_objective()` 함수
    - `--save-baseline` CLI 옵션
    - `data/output/baseline_objective.json` 생성

### 미완료 항목
- [ ] Phase 4: `run_optimization.py` 구현 (자동화)
  - Unity batch mode 자동 실행
  - Subprocess 관리 (timeout, error handling)
  - Progress tracking (tqdm)
  - Checkpoint/resume 기능

---

## 🎯 다음 작업

### 즉시 해야 할 작업
**Phase 4 준비: 자동화 구현 대기**

사용자가 Phase 3 수동 테스트를 완료하면 Phase 4 자동화로 진행

**Phase 4 구현 내용 (예정)**:
- `run_optimization.py` 구현
- Unity batch mode 자동 실행
- 전체 워크플로우 무인 실행

### Phase 3 사용법 (구현 완료)
```bash
# Method 1: Baseline 파라미터 생성 및 저장
python dev/generate_parameters.py --baseline
python dev/export_to_unity.py --input data/input/baseline_parameters.json --auto-id
# Unity 실행 (Play 버튼)
python dev/evaluate_objective.py --save-baseline
# → data/output/baseline_objective.json 생성

# Method 2: 수동 최적화 실행 (테스트: 2 generation, 5 evals)
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5
# → Baseline 자동 로드하여 비교

# Method 3: Optimization history 분석
python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv
# → Baseline 비교 및 convergence plot 생성

# Method 4: 실제 최적화 실행 (50 generations, 15 individuals = 750 evals)
python dev/generate_parameters.py --optimize --manual --maxiter 50 --popsize 15
```

---

## 📁 Project Structure

### Python Workspace (This Repository)
```
calibration_hybrid/
├── data/
│   ├── input/          # Unity 파라미터 복사본 (version control)
│   ├── output/         # Unity 결과 복사본 (분석용)
│   └── piona_mvp/
│       └── scripts/    # Unity C# scripts (참고용 초기 MVP, 실제 사용 안함)
├── dev/                # 개발 중인 Python 스크립트
├── archive/            # deprecated 코드
├── .venv/              # Python 가상환경
├── README.md           # 프로젝트 개요 및 사용법 (사람 대상)
└── CLAUDE.md           # (이 파일) Claude Code 개발 가이드
```

### Unity Project (Actual Development Location)
```
D:\UnityProjects\META_VERYOLD_P01_s\
└── Assets\
    └── VeryOld_P01_s\
        └── Dev\
            └── Calibration_hybrid\          # ← 실제 Unity 스크립트 위치
                ├── Calibration_hybrid_OutputManager.cs      # JSON 출력 관리
                ├── Calibration_hybrid_SimulationManager.cs  # 시뮬레이션 제어
                ├── Calibration_hybrid_SFM.cs                # SFM 에이전트 (18 params)
                ├── Calibration_hybrid_Empirical.cs          # 실제 궤적 재생
                └── Calibration_hybrid_ExtractError.cs       # 오차 계산
```

---

## 🚀 Development Roadmap

### Phase 1: 데이터 파이프라인 검증 ✅
- **목표**: Unity ↔ Python 데이터 교환 확인
- **파일**: `load_simulation_results.py`
- **완료 조건**: Unity 출력 파일을 Python에서 정상적으로 읽고 내용 출력
- **상태**: 완료

### Phase 2: Objective Function 구현 ✅
- **목표**: 시뮬레이션 결과 정량적 평가
- **파일**: `evaluate_objective.py`
- **완료 조건**: 시뮬레이션 결과에 대한 정량적 평가 점수 산출
- **상태**: 완료

### Phase 3: 최적화 알고리즘 연결 ✅
- **목표**: 파라미터 생성 및 변환
- **파일**: `generate_parameters.py`, `export_to_unity.py`
- **완료 조건**: 수동으로 최적화 루프 1회 완전 순환
- **상태**: 완료

### Phase 4: 자동화 (👈 다음 단계)
- **목표**: 전체 워크플로우 자동 실행
- **파일**: `run_optimization.py`
- **완료 조건**: 사용자 개입 없이 N회 최적화 반복 실행
- **상태**: 대기

---

## 📝 개발 중 발견사항

### 이슈 및 결정사항

**2025-01-XX: Unity Calibration System MVP 구현 완료**
- 5개의 Unity C# 스크립트로 구성된 calibration system 구축
- 18개 SFM 파라미터 입력 및 시뮬레이션 결과 JSON 출력 기능 완성
- ParameterInterface가 parameter bounds metadata를 자동 생성 (Python 최적화용)

**2025-01-XX: 데이터 포맷 JSON으로 확정**
- Unity 결과 파일 포맷: JSON (CSV보다 중첩 구조 표현 용이)
- Python → Unity 파라미터 파일 포맷: JSON
- Newtonsoft.Json 사용 (Vector3 custom converter 구현)

**2025-01-XX: Optimization Algorithm - Scipy Differential Evolution 선택**
- TuRBO/ASHA 대신 Scipy DE 선택 이유:
  - 18-dim continuous optimization에 적합 (TuRBO는 50+ dim에서 강점)
  - Gradient-free (Unity는 미분 불가능한 black-box)
  - 단순한 설정 (하이퍼파라미터 3-4개만)
  - 프로젝트 철학 (단순함 유지) 부합
  - 30년 검증된 robust algorithm
- 설정: popsize=15, maxiter=50, strategy='best1bin'
- 예상 총 평가 횟수: ~750 Unity simulations

**2025-01-XX: Unity → Python 파라미터 로딩 시스템 구축**
- `Calibration_hybrid_InputManager.cs` 생성 (OutputManager와 동일한 패턴)
- Python export_to_unity.py가 생성한 JSON 파일 자동 로드
- `StreamingAssets/Calibration/Input/` 폴더에서 최신 `*_parameters.json` 자동 탐색
- `Calibration_hybrid_SFM.cs` 수정: Start()에서 InputManager로부터 18개 파라미터 자동 로드
- Parameter validation 및 bounds clamping 적용

**2025-01-XX: Unity 자동 종료 기능 추가**
- `Calibration_hybrid_OutputManager.cs`에 `autoStopPlayMode` 옵션 추가
- 시뮬레이션 완료 및 결과 저장 후 자동으로 Unity Play 모드 종료
- Manual Optimization 워크플로우 개선 (수동 정지 단계 제거)
- Editor mode: `EditorApplication.isPlaying = false`
- Build mode: `Application.Quit()`

**2025-01-XX: generate_parameters.py Iteration Counting 버그 수정**
- **문제**: Scipy DE maxiter 조정 로직 오류로 iteration이 무한 증가
  - `scipy_maxiter = maxiter - 1` 계산이 부정확
  - Convergence 실패 시 계속 실행됨
  - User expects `maxiter=1, popsize=5` → 5 evals, but got 6+ evals
- **1차 해결 (StopIteration 방식)**:
  - Total evaluations 기준으로 변경: `max_evaluations = maxiter * popsize`
  - Evaluation counter로 hard limit 적용
  - Limit 도달 시 `StopIteration` 예외로 정상 종료
  - `scipy_maxiter = maxiter * 10` (safety margin, 실제로는 StopIteration으로 제어)
- **문제 발생**: RuntimeError "func(x, *args) must return a scalar value"
  - StopIteration이 scipy 내부 `_calculate_population_energies()`에서 잘못 처리됨
  - Scipy는 objective function이 scalar를 반환할 것으로 기대
  - Exception 발생 시점에 scipy가 에너지 계산 시도하면서 충돌
- **최종 해결 (Callback 방식)**:
  - StopIteration 대신 scipy의 `callback` 메커니즘 사용
  - Callback 함수가 `True` 반환 시 정상 종료 (scipy가 올바르게 처리)
  - Evaluation counter는 유지, callback에서 limit 체크
  - `differential_evolution(..., callback=callback)` 추가
- **결과**: `maxiter=2, popsize=5` → 정확히 10회 평가 후 정상 종료 (RuntimeError 해결)

**2025-01-XX: Optimization History 분석 기능 추가**
- **기능**: `analyze_optimization_history()` 함수 추가
  - Summary statistics (total evals, best/worst/mean/std objective)
  - Best objective per generation (generation 단위 그룹화)
  - Best parameters 출력
  - Matplotlib convergence plot (optional)
    - Left: All evaluations scatter plot
    - Right: Best per generation line plot
- **CLI**: `--analyze` mode 추가
  - Usage: `python dev/generate_parameters.py --analyze --history path/to/history.csv`
  - Unity 실행 없이 기존 결과 분석 가능
- **목적**: 사용자가 optimization 진행 상황을 쉽게 파악

**2025-01-XX: Baseline Objective 저장 및 자동 비교 기능**
- **문제**: 하드코딩된 baseline (4.5932)으로는 다른 초기 파라미터 비교 불가
- **해결**:
  - `evaluate_objective.py`에 `save_baseline_objective()` 추가
    - `--save-baseline` 옵션으로 baseline 저장
    - `data/output/baseline_objective.json` 생성
    - Objective, metrics, parameters, timestamp 저장
  - `generate_parameters.py`에 `load_baseline_objective()` 추가
    - 파일에서 baseline 자동 로드 (없으면 4.5932 fallback)
    - Optimization 완료 시 baseline과 자동 비교
    - `analyze_optimization_history()`에서 baseline 비교 섹션 추가
    - Convergence plot에 baseline 수평선 표시 (빨간 점선)
- **워크플로우**:
  1. 최초 1회: `python dev/evaluate_objective.py --save-baseline`
  2. 이후 optimization/분석: baseline 자동 참조
- **장점**: 다양한 초기 조건 테스트 및 비교 가능

### 데이터 포맷 결정

**Unity → Python** (시뮬레이션 결과): `simulation_result.json`

```json
{
  "experimentId": "guid-string",
  "startTime": "2025-01-15T10:30:00",
  "endTime": "2025-01-15T10:35:42",
  "executionTimeSeconds": 342.5,
  "totalAgents": 100,
  "actualAgents": 95,
  "maxTimeIndex": 300,
  "actualTimeIndex": 300,
  "successful": true,
  "errorMessage": "",
  "metrics": {
    "actualAgents": 95,
    "avgTrajectoryError": 0.234,
    "maxTrajectoryError": 1.456
  },
  "trajectories": [
    {
      "agentId": 1,
      "empiricalPoints": [
        {
          "timeIndex": 0,
          "position": {"x": 1.0, "y": 0.0, "z": 2.0},
          "speed": 1.2,
          "timestamp": "2025-01-15T10:30:01"
        }
      ],
      "validationPoints": [
        {
          "timeIndex": 0,
          "position": {"x": 1.05, "y": 0.0, "z": 2.02},
          "speed": 1.18,
          "timestamp": "2025-01-15T10:30:01"
        }
      ]
    }
  ],
  "avgFPS": 60.0,
  "memoryUsageMB": 512
}
```

**Python → Unity** (파라미터): `parameters.json`

```json
{
  "minimalDistance": 0.2,
  "relaxationTime": 0.5,
  "repulsionStrengthAgent": 1.2,
  "repulsionRangeAgent": 5.0,
  "lambdaAgent": 0.35,
  "repulsionStrengthObs": 1.0,
  "repulsionRangeObs": 5.0,
  "lambdaObs": 0.35,
  "k": 8.0,
  "kappa": 5.0,
  "obsK": 3.0,
  "obsKappa": 0.0,
  "considerationRange": 2.5,
  "viewAngle": 150.0,
  "viewAngleMax": 240.0,
  "viewDistance": 5.0,
  "rayStepAngle": 30.0,
  "visibleFactor": 0.7,
  "mass": 1.0,
  "agentRadius": 0.3,
  "rotationSpeed": 5.0,
  "randomSeed": 42,
  "fidelityLevel": "L3",
  "agentSamplingRatio": 1.0,
  "maxTimeIndex": -1,
  "experimentId": "exp_001",
  "timestamp": "2025-01-15T10:30:00"
}
```

**Unity Auto-Generated** (parameter bounds metadata): `parameter_bounds.json`

```json
{
  "parameter_count": 18,
  "bounds": {
    "minimalDistance": {"min": 0.15, "max": 0.35},
    "relaxationTime": {"min": 0.3, "max": 0.8},
    "repulsionStrengthAgent": {"min": 0.8, "max": 1.8},
    "repulsionRangeAgent": {"min": 3.0, "max": 7.0},
    "lambdaAgent": {"min": 0.2, "max": 0.5},
    "repulsionStrengthObs": {"min": 0.6, "max": 1.5},
    "repulsionRangeObs": {"min": 3.0, "max": 7.0},
    "lambdaObs": {"min": 0.2, "max": 0.5},
    "k": {"min": 5.0, "max": 12.0},
    "kappa": {"min": 3.0, "max": 7.0},
    "obsK": {"min": 2.0, "max": 4.5},
    "obsKappa": {"min": 0.0, "max": 2.0},
    "considerationRange": {"min": 2.0, "max": 4.0},
    "viewAngle": {"min": 120.0, "max": 180.0},
    "viewAngleMax": {"min": 200.0, "max": 270.0},
    "viewDistance": {"min": 3.0, "max": 10.0},
    "rayStepAngle": {"min": 15.0, "max": 45.0},
    "visibleFactor": {"min": 0.5, "max": 0.9}
  },
  "parameter_names": ["minimalDistance", "relaxationTime", ...],
  "created_at": "2025-01-15 10:30:00"
}
```

### Unity C# Components Architecture

**Location**: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`

**Calibration_hybrid_OutputManager.cs** (JSON Output Manager)
- Collects 18 SFM parameters directly from InputManager (single source of truth)
- Collects error data from `ExtractError` component via reflection
- Saves `simulation_result.json` to `StreamingAssets/Calibration/Output/`
- Includes 18 SFM parameters, agent errors, and execution metadata
- Auto-saves when simulation completes or Unity exits
- Auto-stop Play mode option (`autoStopPlayMode`)

**Calibration_hybrid_SimulationManager.cs** (Simulation Orchestrator)
- Loads ATC trajectory CSV data (real pedestrian data)
- Spawns paired agents (empirical + validation) at correct timepoints
- Controls simulation speed and frame management
- Manages agent dictionaries and trajectory data
- Completes simulation when maxTimeIndex is reached

**Calibration_hybrid_SFM.cs** (Social Force Model - 18 Parameters)
- Implements Social Force Model with 18 calibration parameters
- Computes driving force, repulsive forces (agent & obstacle)
- Handles collision detection and resolution
- Visibility-based navigation with raycasting
- Tracks validation trajectory for comparison

**Calibration_hybrid_Empirical.cs** (Real Trajectory Tracking)
- Plays back real ATC trajectory data
- Interpolates position between timepoints
- Renders empirical trajectory with LineRenderer
- Paired with validation agent for error calculation

**Calibration_hybrid_ExtractError.cs** (Error Calculation)
- Calculates 2D distance between empirical and validation agents
- Skips spawn position (first point) to avoid initial error
- Saves per-agent, per-timepoint error to CSV
- Used for calibration objective function

### 18 SFM Parameters (Calibration Targets)

**Basic Physics** (2 parameters)
- `minimalDistance` [0.15, 0.35] - minimum allowed distance between agents
- `relaxationTime` [0.3, 0.8] - time to reach desired velocity

**Agent Interaction** (3 parameters)
- `repulsionStrengthAgent` [0.8, 1.8] - social force strength from other agents
- `repulsionRangeAgent` [3.0, 7.0] - range of agent repulsion
- `lambdaAgent` [0.2, 0.5] - anisotropic factor (forward vs backward)

**Obstacle Interaction** (3 parameters)
- `repulsionStrengthObs` [0.6, 1.5] - social force strength from obstacles
- `repulsionRangeObs` [3.0, 7.0] - range of obstacle repulsion
- `lambdaObs` [0.2, 0.5] - anisotropic factor for obstacles

**Physical Contact Forces** (4 parameters)
- `k` [5.0, 12.0] - body force coefficient (agent-agent)
- `kappa` [3.0, 7.0] - friction force coefficient (agent-agent)
- `obsK` [2.0, 4.5] - body force coefficient (agent-obstacle)
- `obsKappa` [0.0, 2.0] - friction force coefficient (agent-obstacle)

**Perception/Vision** (6 parameters)
- `considerationRange` [2.0, 4.0] - range to consider nearby objects
- `viewAngle` [120, 180] - default field of view angle (degrees)
- `viewAngleMax` [200, 270] - maximum field of view when obstructed
- `viewDistance` [3.0, 10.0] - maximum visibility distance
- `rayStepAngle` [15, 45] - angular step for raycasting
- `visibleFactor` [0.5, 0.9] - weight of current velocity in navigation

### 주의사항

**Unity Execution**
- Unity project location: `D:\UnityProjects\META_VERYOLD_P01_s\`
- Scene name: `Calibration.unity` (must be in Build Settings for batch mode)
- StreamingAssets path is automatically created by ParameterInterface
- Results are saved even if Unity crashes (OnDestroy handler)

**Parameter Validation**
- All parameters are automatically clamped within bounds by `ValidateAndClamp()`
- Invalid parameters will be corrected, not rejected
- experimentId links parameters to results

**Trajectory Data**
- CSV file: `atc_resampled_1s_noQueing.csv` (1-second intervals)
- Empirical agents follow real data exactly (no physics)
- Validation agents use SFM physics with the same start/goal points
- Error calculation starts from 2nd timepoint (skip spawn position)

---

## ✅ 완료된 작업

### 초기 설정
- **README.md**: 사용자 대상 프로젝트 사용법 문서 작성
- **CLAUDE.md**: Claude Code 대상 개발 가이드 작성
- **개발 계획**: 4단계 Phase 계획 수립

### Unity Calibration System
**Location**: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`

- **Calibration_hybrid_OutputManager.cs**: JSON output manager (reads from InputManager)
- **Calibration_hybrid_InputManager.cs**: Parameter loading and validation
- **Calibration_hybrid_SimulationManager.cs**: ATC trajectory loading, agent spawning, frame control
- **Calibration_hybrid_SFM.cs**: 18-parameter Social Force Model implementation
- **Calibration_hybrid_Empirical.cs**: Real trajectory playback
- **Calibration_hybrid_ExtractError.cs**: Error calculation between empirical and validation trajectories
- **Data Format Specification**: Confirmed JSON structure for Unity→Python communication
- **Parameter Architecture**: InputManager as single source of truth (OutputManager reads from InputManager)

### Python Development Scripts
**Location**: `c:\dev\calibration_hybrid\dev\`

- **load_simulation_results.py**: Load and analyze Unity simulation results
  - Parses `simulation_result.json` from Unity
  - Validates 18 SFM parameters
  - Displays agent error statistics
  - Supports verbose mode and agent-specific detail view
  - Usage: `python dev/load_simulation_results.py [--verbose] [--agent-id ID]`

- **evaluate_objective.py**: Compute objective function from simulation results
  - 3 metrics: MeanError (50%), Percentile95 (30%), TimeGrowthPenalty (20%)
  - Baseline objective: 4.5932 (lower is better)
  - Verbose mode shows top 10 worst time-growth agents
  - Compare mode for multiple simulation results
  - Baseline save mode: `--save-baseline` saves to `data/output/baseline_objective.json`
  - Usage: `python dev/evaluate_objective.py [--verbose] [--compare file1.json file2.json] [--save-baseline]`

- **export_to_unity.py**: Export Python parameters to Unity JSON format
  - Converts Python dict to Unity-compatible JSON
  - Auto-generates experiment IDs (timestamp + UUID)
  - Validates parameters against 18 SFM bounds
  - Automatic parameter clamping for out-of-bounds values
  - Saves to StreamingAssets/Calibration/Input/
  - Usage: `python dev/export_to_unity.py --input params.json --auto-id`

- **generate_parameters.py**: Parameter generation and optimization with Scipy DE
  - Creates baseline parameters from Unity defaults
  - Scipy Differential Evolution optimization
  - Manual mode: exports params, waits for user to run Unity, loads results
  - Auto mode: Phase 4 (not yet implemented)
  - Optimization history tracking (CSV)
  - Best parameters auto-save
  - Iteration counting bug fixed (exact `maxiter * popsize` evaluations)
  - Analyze mode: analyze existing optimization history (--analyze)
  - Baseline auto-load: loads from `data/output/baseline_objective.json` (fallback: 4.5932)
  - Baseline comparison in optimization results and analysis
  - Usage: `python dev/generate_parameters.py --baseline`
  - Usage: `python dev/generate_parameters.py --optimize --manual --maxiter 1 --popsize 5`
  - Usage: `python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv`

---

## 💻 Development Commands

### Python Environment

**Activation**
```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate
```

**Dependencies** (현재 상태)
- Python 3.10+
- 추후 추가: NumPy, Pandas, Scipy (requirements.txt 생성 예정)

### Unity Execution

**Method 1: Unity Editor (Manual Testing - Phase 3)**
```bash
# 1. Open Unity project: D:\UnityProjects\META_VERYOLD_P01_s\
# 2. Open Calibration scene
# 3. Press Play button
# 4. Check StreamingAssets/Calibration/Output/simulation_result.json
```

**Method 2: Batch Mode (Python Automation - Phase 4, TBD)**
- Unity batch mode 자동 실행은 Phase 4에서 구현 예정
- `run_optimization.py`에서 subprocess로 Unity.exe 실행
- 상세 커맨드 및 인자는 Phase 4 구현 시 문서화

---

## 🔍 Important Conventions

### Data Format
- **Unity → Python**: JSON (시뮬레이션 결과)
- **Python → Unity**: JSON (파라미터 설정)
- **Vector3 Serialization**: Custom JsonConverter handles Unity Vector3 to prevent circular references

### File Locations

**Unity Project**:
- **Unity Scripts** (actual development): `D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`
- **StreamingAssets** (runtime I/O):
  - Input: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Input\`
  - Output: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\`
  - Trajectory data: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Data\PedestrianTrajectory\ATC\`

**Python Workspace** (this repository):
- `data/input/` - Parameter files copy (version control)
- `data/output/` - Results copy (analysis)
- `data/piona_mvp/scripts/` - Reference only (초기 MVP, 실제 사용 안함)
- Development scripts: Project root or `dev/`

### Gitignore
- `data/` - Data files (not tracked by git)
- `archive/` - Deprecated code (not tracked by git)
- `.venv/` - Python virtual environment

### Naming Conventions
- Parameter files: `<experimentId>_parameters.json` (e.g., `exp_001_parameters.json`)
- Result files: `<experimentId>_result.json` (e.g., `exp_001_result.json`)
- Experiment IDs: Use descriptive names (e.g., `baseline`, `opt_iter_5`) or GUIDs

---

## 🎓 Context for New Sessions

### 새 Claude Code 세션 시작 시 체크리스트:

1. **"📍 현재 작업 상태"** 확인
   - 어느 Phase인지
   - 어떤 파일 작업 중인지
   - 완료/미완료 항목

2. **"🎯 다음 작업"** 확인
   - 바로 해야 할 작업
   - 완료 조건

3. **"📝 개발 중 발견사항"** 확인
   - 이전 세션에서 발견한 이슈
   - 내린 설계 결정

4. **"🛠️ Development Philosophy"** 숙지
   - 수동 검증 우선
   - 단순하고 독립적인 스크립트
   - 필요한 것만 만들기

5. **작업 시작 전 확인**
   - README.md의 "현재 상태" 체크리스트 확인
   - 해당 Phase의 완료 조건 확인

---

## 🔧 Development Tips

### 코딩 스타일
- 각 스크립트는 독립적으로 실행 가능
- argparse로 명령줄 인자 처리
- 간단한 사용 예시 docstring 포함
- 복잡한 클래스보다 함수 중심

### 테스트 접근법
- Phase 1: 샘플 JSON/CSV로 로드 테스트
- Phase 2: 여러 결과 파일로 목적함수 값 비교
- Phase 3: 수동으로 1회 전체 루프 실행
- Phase 4: 자동화 파이프라인 검증

### 문서 업데이트
- Phase 완료 시 README.md의 체크리스트 업데이트
- CLAUDE.md의 "📍 현재 작업 상태", "✅ 완료된 작업" 업데이트
- 새로운 발견사항은 "📝 개발 중 발견사항"에 추가

---

## 🚨 Critical Reminders

1. **단순함 유지**: 복잡한 구조 금지
2. **단계별 검증**: 각 Phase 완료 조건 충족 확인
3. **수동 우선**: 자동화는 마지막 단계에서만
4. **독립 실행**: 각 스크립트는 단독으로 실행 가능해야 함
5. **볼륨 관리**: 불필요한 코드 생성 금지

---

## 📚 Additional Resources

- **README.md**: 전체 시스템 개요, 워크플로우, 사용법 (사람 대상)
- **Unity 프로젝트**: PIONA 시뮬레이션 (별도 위치, 추후 명시)
- **실제 데이터**: ATC 궤적 데이터 (추후 명시)
- to memorize: 1. 앞으로 너가 작성해주는 모든 코드, 이미지, 그래프, 파일 등 모든 output은 영어로만 작성해줬으면 좋겠어. 2. .md 파일을 제외한 모든 파일(특히 코드 작성)을 작업할 때 이모지를 쓰지마.