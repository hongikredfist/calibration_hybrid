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

**현재 Phase**: Phase 2 완료, Phase 3 준비 중
**현재 작업**: 파라미터 생성 및 최적화 알고리즘 연결 준비
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

### 미완료 항목
- [ ] Phase 3: `generate_parameters.py`, `export_to_unity.py` 구현
- [ ] Phase 4: `run_optimization.py` 구현

---

## 🎯 다음 작업

### 즉시 해야 할 작업
**Phase 3: 최적화 알고리즘 연결**

1. **파라미터 생성 스크립트** 작성: `dev/generate_parameters.py`
   - 최적화 알고리즘 선택 (Scipy, Optuna 등)
   - 18개 SFM 파라미터 bounds 적용
   - 새로운 파라미터 세트 생성

2. **Unity 포맷 변환 스크립트** 작성: `dev/export_to_unity.py`
   - Python 파라미터 → Unity JSON 포맷 변환
   - `StreamingAssets/Calibration/Input/` 경로에 저장
   - Experiment ID 자동 생성

3. **수동 최적화 루프 1회 실행**
   - Baseline 파라미터로 시뮬레이션 → Objective 평가
   - 새 파라미터 생성 → Unity 실행 → Objective 평가
   - 개선 여부 확인

### Phase 3 완료 조건
- 파라미터 생성 및 Unity 포맷 변환 성공
- 수동으로 최적화 루프 1회 완전 순환
- Objective value 개선 확인 (4.59 → ?)

### 예상 사용법
```bash
# 1. 새 파라미터 생성
python dev/generate_parameters.py --baseline

# 2. Unity 포맷으로 변환
python dev/export_to_unity.py --input params.json --output exp_001_parameters.json

# 3. Unity 시뮬레이션 실행 (수동)

# 4. Objective 평가
python dev/evaluate_objective.py --file exp_001_result.json
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

### Phase 1: 데이터 파이프라인 검증 (👈 현재 단계)
- **목표**: Unity ↔ Python 데이터 교환 확인
- **파일**: `load_simulation_results.py`
- **완료 조건**: Unity 출력 파일을 Python에서 정상적으로 읽고 내용 출력

### Phase 2: Objective Function 구현
- **목표**: 시뮬레이션 결과 정량적 평가
- **파일**: `evaluate_objective.py`
- **완료 조건**: 시뮬레이션 결과에 대한 정량적 평가 점수 산출

### Phase 3: 최적화 알고리즘 연결
- **목표**: 파라미터 생성 및 변환
- **파일**: `generate_parameters.py`, `export_to_unity.py`
- **완료 조건**: 수동으로 최적화 루프 1회 완전 순환

### Phase 4: 자동화
- **목표**: 전체 워크플로우 자동 실행
- **파일**: `run_optimization.py`
- **완료 조건**: 사용자 개입 없이 N회 최적화 반복 실행

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
- Caches SFM parameters from first spawned agent (prevents parameter loss when agents destroy)
- Collects error data from `ExtractError` component via reflection
- Saves `simulation_result.json` to `StreamingAssets/Calibration/Output/`
- Includes 18 SFM parameters, agent errors, and execution metadata
- Auto-saves when simulation completes or Unity exits

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

- **Calibration_hybrid_OutputManager.cs**: JSON output manager with parameter caching
- **Calibration_hybrid_SimulationManager.cs**: ATC trajectory loading, agent spawning, frame control
- **Calibration_hybrid_SFM.cs**: 18-parameter Social Force Model implementation
- **Calibration_hybrid_Empirical.cs**: Real trajectory playback
- **Calibration_hybrid_ExtractError.cs**: Error calculation between empirical and validation trajectories
- **Data Format Specification**: Confirmed JSON structure for Unity→Python communication
- **Parameter Caching Fix**: Caches SFM parameters at simulation start to prevent loss when agents destroy

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
  - Usage: `python dev/evaluate_objective.py [--verbose] [--compare file1.json file2.json]`

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

**Method 1: Unity Editor (Manual Testing)**
```bash
# 1. Open Unity project: D:\UnityProjects\META_VERYOLD_P01_s\
# 2. Open Calibration scene
# 3. Press Play button
# 4. Check StreamingAssets/Calibration/Output/simulation_result.json
```

**Method 2: Batch Mode (Python Automation)**
```bash
# From Python script, execute Unity in batch mode with parameters
"C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe" \
  -quit \
  -batchmode \
  -projectPath "D:\UnityProjects\META_VERYOLD_P01_s" \
  -executeMethod Calibration_ParameterInterface.ExecuteBatchModeSimulation \
  -logFile "logs/unity_simulation.log" \
  -parametermode \
  -autoexit \
  -parameterfile "exp_001_parameters.json" \
  -resultfile "exp_001_result.json" \
  -seed 42
```

**Command-line Arguments for ParameterInterface**
- `-parametermode` - Enable parameter loading from JSON
- `-autoexit` - Automatically exit Unity after simulation completes
- `-parameterfile <filename>` - Specify parameter JSON filename (in Input folder)
- `-resultfile <filename>` - Specify result JSON filename (in Output folder)
- `-seed <int>` - Set random seed for reproducibility

**Method 3: Editor Mode MenuItem (Legacy)**
```bash
# In Unity Editor menu bar:
# Calibration > Legacy - Run Single Simulation
# (Uses latest parameter file in Input folder)
```

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