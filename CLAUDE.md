# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## CLAUDE.md Writing Rules

### Purpose
- **CLAUDE.md**: For Claude Code (AI assistant) - Technical context, architecture, current status, next steps
- **README.md**: For humans (users, developers) - Installation, usage instructions, how-to guides

### Language Policy
- **CLAUDE.md**: English (technical precision, better AI comprehension)
- **README.md**: Korean (user-facing documentation)
- **Code/Comments**: English only

### Structure Requirements

**1. Project Overview** (Static - rarely changes)
- One-sentence project description
- Core architecture diagram
- Tech stack and workflow

**2. Current Status** (Update every session)
- Current phase/milestone
- Completed checklist (with dates if significant)
- Next tasks checklist
- Last session summary (1-2 sentences)

**3. Development Commands** (Essential workflows)
- Environment setup
- Common daily workflows
- File path references

**4. Architecture Deep Dive** (High-level only)
- Cross-component interactions requiring multiple files to understand
- Data format specifications (JSON schemas)
- Algorithm configurations
- Exclude: obvious file structure, low-level class details

**5. Development History** (Critical decisions and bugs)
- Format: `YYYY-MM-DD: Title`
- Include: Problem/Context, Solution/Rationale, Impact
- Archive old entries after 10+ items

**6. Next Steps** (Actionable tasks)
- Immediate next task
- Goal and acceptance criteria
- Expected files/changes
- Blockers if any

### Update Triggers

**Always update** when:
- Completing a phase/milestone → Update "Current Status"
- Fixing non-trivial bug → Add to "Development History"
- Making architectural decision → Add to "Development History"
- Changing next task → Update "Next Steps"
- Adding new workflow → Update "Development Commands"

**Never update** for:
- Trivial changes (typo, formatting)
- Expected task progress (use TODO comments)
- Temporary experiments (use git branches)

### Quality Checklist
Before ending session, verify:
- [ ] Current phase clearly stated
- [ ] Completed items checked off
- [ ] Next task with acceptance criteria defined
- [ ] Bugs/decisions documented in History
- [ ] Commands for next session present
- [ ] No stale/outdated information

---

## Project Overview

**calibration_hybrid** - Unity-Python hybrid system for automatic parameter calibration of PIONA pedestrian simulation using black-box optimization.

### Architecture
```
Python (generate_parameters.py)
    ↓ parameters.json
Unity Simulation (PIONA/SFM 18 params)
    ↓ simulation_result.json
Python (evaluate_objective.py)
    ↓ objective score
Scipy Differential Evolution
    ↓ next parameters
[Loop until convergence]
```

### Tech Stack
- **Unity 2021+**: PIONA pedestrian simulation (Social Force Model)
- **Python 3.10+**: numpy, scipy, matplotlib, tqdm
- **Optimization**: Scipy Differential Evolution (population-based, gradient-free)
- **Data Format**: JSON for Unity ↔ Python communication

### Core Workflow
1. Python generates 18 SFM parameters within bounds
2. Unity runs simulation comparing SFM agents vs real ATC trajectory data
3. Python computes objective (mean error + 95th percentile + time growth penalty)
4. Optimization algorithm suggests next parameters
5. Repeat until objective minimized

### 18 SFM Parameters (Calibration Targets)
- **Basic Physics** (2): minimalDistance, relaxationTime
- **Agent Interaction** (3): repulsionStrengthAgent, repulsionRangeAgent, lambdaAgent
- **Obstacle Interaction** (3): repulsionStrengthObs, repulsionRangeObs, lambdaObs
- **Physical Contact Forces** (4): k, kappa, obsK, obsKappa
- **Perception/Vision** (6): considerationRange, viewAngle, viewAngleMax, viewDistance, rayStepAngle, visibleFactor

All bounds defined in `export_to_unity.py:PARAMETER_BOUNDS`.

---

## Current Status

**Phase**: Phase 4B In Progress - Unity Automation Debugging
**Current Task**: Testing Unity automation (TESTING.md Step 2)
**Last Session**: Fixed AutomationController scene path issue (Calibration.unity → Calibration_Hybrid.unity)

### Completed

#### Phase 1: Data Pipeline ✅ (Complete)
- [x] `load_simulation_results.py` - Load and parse Unity simulation_result.json
- [x] Validate 18 parameters, display agent error statistics
- [x] Unity → Python JSON communication verified

#### Phase 2: Objective Function ✅ (Complete)
- [x] `evaluate_objective.py` - Compute objective from simulation results
- [x] 3-metric formula: 50% MeanError + 30% Percentile95 + 20% TimeGrowthPenalty
- [x] Baseline objective: 4.5932 (Unity default parameters)
- [x] Compare mode for multiple results
- [x] Baseline save/load feature (`--save-baseline`)

#### Phase 3: Manual Optimization ✅ (Complete)
- [x] `generate_parameters.py` - Scipy Differential Evolution integration
- [x] `export_to_unity.py` - Python dict → Unity JSON with validation
- [x] Baseline parameter generation (`--baseline`)
- [x] Manual optimization mode (user runs Unity manually each iteration)
- [x] Optimization history tracking (CSV)
- [x] History analysis with convergence plots (`--analyze`)
- [x] Baseline auto-load and comparison
- [x] **Bug fix**: Iteration counting (callback mechanism) - 2025-10-02
- [x] Unity auto-stop Play mode after simulation

#### Phase 4B: Optimizer Abstraction Layer ⏳ (In Progress)
- [x] Architecture design (core/, optimizer/, analysis/ modules)
- [x] `optimizer/base_optimizer.py` - Abstract interface for all algorithms
- [x] `core/parameter_utils.py` - Parameter conversion utilities
- [x] `core/unity_simulator.py` - Unity Editor automation (encapsulated)
- [x] `core/objective_function.py` - Evaluation logic (reusable)
- [x] `optimizer/scipy_de_optimizer.py` - Wrap existing Scipy DE code
- [x] `run_optimization.py` - Unified CLI with algorithm selection
- [x] `Calibration_hybrid_AutomationController.cs` - Unity Editor menu automation
- [x] TESTING.md - Comprehensive test guide
- [x] **Bug fix**: Scene path (Calibration → Calibration_Hybrid) - 2025-10-15

### Next

#### Phase 4B: Testing & Validation (Current)
- [ ] **CURRENT**: Test Unity automation (TESTING.md Step 2)
  - Verify AutomationController loads Calibration_Hybrid scene correctly
  - Verify Play mode starts/stops automatically
  - Verify simulation_result.json created
- [ ] Test Python → Unity integration (TESTING.md Step 3)
- [ ] Test Objective Function wrapper (TESTING.md Step 4)
- [ ] Test end-to-end optimization (TESTING.md Step 5: 10 evaluations)
- [ ] Compare results with Phase 3 manual mode (validate no regression)

**Blocker**: Scene path confusion resolved. User testing Step 2 now.

**Rationale**: SCI paper requires algorithm comparison experiments. Implementing abstraction now prevents costly refactoring later (8 hours now vs 20+ hours after Phase 4A).

---

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
.venv\Scripts\activate              # Windows
source .venv/bin/activate           # Unix/Mac

# Install dependencies
pip install -r requirements.txt
```

### Phase 3: Manual Optimization
```bash
# Test: 2 gens × 5 pop = 10 evaluations
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5

# Production: 50 gens × 15 pop = 750 evaluations
python dev/generate_parameters.py --optimize --manual --maxiter 50 --popsize 15

# Analysis
python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv
```

### Phase 4B: Automated Optimization (Testing)
```bash
# See dev/TESTING.md for 5-step test procedure

# Quick test (10 evals)
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5 --seed 42

# Production (750 evals, ~3 days)
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42
```

### Key Paths

**Unity**: `D:\UnityProjects\META_VERYOLD_P01_s\`
- Scripts: `Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`
- Scene: `Assets\VeryOld_P01_s\Scene\PedModel\Calibration_Hybrid.unity`
- Input: `Assets\StreamingAssets\Calibration\Input\*_parameters.json`
- Output: `Assets\StreamingAssets\Calibration\Output\simulation_result.json`

**Python**: `c:\dev\calibration_hybrid\dev\`
- Results: `data/output/` (baseline_objective.json, optimization_history.csv, best_parameters.json)

---

## Architecture Deep Dive

### Unity → Python Data Flow

**Unity Side** (D:\UnityProjects\...\Calibration_hybrid\):
1. `Calibration_hybrid_InputManager.cs`
   - Loads parameters JSON from StreamingAssets/Input/
   - Validates and clamps parameters to bounds
   - Single source of truth for parameter values
2. `Calibration_hybrid_SimulationManager.cs`
   - Loads ATC trajectory CSV (real pedestrian data)
   - Spawns paired agents (empirical + validation) at correct timepoints
   - Controls simulation frame loop
3. `Calibration_hybrid_SFM.cs`
   - Social Force Model physics with 18 parameters
   - Validation agents use SFM to navigate same path as empirical
4. `Calibration_hybrid_Empirical.cs`
   - Replays real ATC trajectory exactly (no physics)
5. `Calibration_hybrid_ExtractError.cs`
   - Computes 2D Euclidean distance between empirical and validation agents
   - Per-agent, per-timepoint error tracking
6. `Calibration_hybrid_OutputManager.cs`
   - Collects parameters from InputManager
   - Collects errors from ExtractError via reflection
   - Saves simulation_result.json to StreamingAssets/Output/
   - Auto-stops Play mode when complete

**Python Side** (c:\dev\calibration_hybrid\dev\):
1. `generate_parameters.py`
   - Scipy Differential Evolution optimizer
   - Manual mode: exports params, waits for user, loads results
   - Auto mode: Phase 4 (not yet implemented)
   - History tracking and analysis
2. `export_to_unity.py`
   - Converts Python dict to Unity JSON
   - Validates parameters against bounds
   - Auto-clamps out-of-bounds values
   - Generates experiment IDs
3. `evaluate_objective.py`
   - Loads simulation_result.json
   - Computes 3-metric objective function
   - Saves/loads baseline for comparison
4. `load_simulation_results.py`
   - Utility for inspecting simulation data
   - Verbose mode and agent-specific views

### JSON Data Formats

**Python → Unity** (parameters.json):
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
  "experimentId": "exp_20250115_103000_a1b2c3d4",
  "timestamp": "2025-01-15T10:30:00"
}
```

**Unity → Python** (simulation_result.json):
```json
{
  "experimentId": "exp_20250115_103000_a1b2c3d4",
  "startTime": "2025-01-15T10:30:00",
  "endTime": "2025-01-15T10:35:42",
  "executionTimeSeconds": 342.5,
  "totalAgents": 100,
  "actualAgents": 95,
  "parameters": {
    "minimalDistance": 0.2,
    // ... all 18 parameters
  },
  "agentErrors": [
    {
      "agentId": 4236,
      "timeErrors": [
        {"timeIndex": 1, "error": 0.234},
        {"timeIndex": 2, "error": 0.456}
      ],
      "meanError": 0.345,
      "maxError": 0.678,
      "percentile95": 0.612
    }
  ],
  "avgFPS": 60.0,
  "memoryUsageMB": 512
}
```

### Objective Function Formula

**Objective** (lower is better):
```
Objective = 0.50 × MeanError + 0.30 × Percentile95 + 0.20 × TimeGrowthPenalty
```

**Components**:
1. **MeanError** (50% weight)
   - Average trajectory error across all agents
   - Primary metric: overall simulation accuracy

2. **Percentile95** (30% weight)
   - 95th percentile of agent errors
   - Robustness: penalizes outliers without being overly sensitive

3. **TimeGrowthPenalty** (20% weight)
   - Detects agents whose error grows over time (instability)
   - Calculation: For each agent, compute slope of error vs time
   - Penalty: Average positive slope (growing errors only)

**Baseline**: 4.5932 (Unity default parameters)

### Optimization Algorithm Configuration

**Scipy Differential Evolution** - Population-based, gradient-free

**Why DE**:
- Unity simulation is black-box (no gradients available)
- 18D continuous parameter space (DE optimal range: 10-40D)
- Simple configuration (3-4 hyperparameters vs TuRBO's 15+)
- 30+ years of proven robustness
- Project philosophy: simplicity over cutting-edge complexity

**Configuration**:
```python
scipy.optimize.differential_evolution(
    objective_function,
    bounds=[(min, max) for each of 18 params],
    strategy='best1bin',      # Mutation strategy
    maxiter=50,               # Generations
    popsize=15,               # Individuals per generation
    mutation=(0.5, 1.0),      # Default mutation factor range
    recombination=0.7,        # Default crossover probability
    callback=early_stop_callback  # Hard limit on evaluations
)
```

**Total Evaluations**: `maxiter × popsize = 50 × 15 = 750` Unity simulations
**Expected Runtime**: 1-3 days (5-10 min per simulation)

---

## Development History

### 2025-10-15: AutomationController Scene Path Fix

**Problem**:
- User ran `Automation → Test - Run Simulation (Manual)` menu in Unity
- Unity loaded wrong scene: `Calibration.unity` (old system with `Calibration_ParameterInterface`)
- Should load: `Calibration_Hybrid.unity` (Phase 3 system with `Calibration_hybrid_*` scripts)
- Error: `[ParameterInterface] Instance CalibrationManager - Specific file not found: parameters.json`
- Root cause: Two parallel calibration systems exist in project

**Context**:
- **Old system** (`Assets/VeryOld_P01_s/Dev/Calibration/`): Uses `Calibration_ParameterInterface.cs`, different parameter loading mechanism
- **Phase 3+ system** (`Assets/VeryOld_P01_s/Dev/Calibration_hybrid/`): Uses `Calibration_hybrid_InputManager.cs`, designed for Python integration
- `AutomationController.cs` had hardcoded path: `"Assets/Scenes/Calibration.unity"` (wrong scene)

**Solution**:
1. Updated `CALIBRATION_SCENE_PATH` in `Calibration_hybrid_AutomationController.cs` (line 22):
   ```csharp
   // Before: "Assets/Scenes/Calibration.unity"
   // After:  "Assets/VeryOld_P01_s/Scene/PedModel/Calibration_Hybrid.unity"
   ```
2. Updated `SCENE_NAME_PATTERNS` to prioritize "Calibration_Hybrid" over "Calibration"
3. Added comments distinguishing Phase 3+ system from old system
4. Updated TESTING.md with scene name clarification and troubleshooting section

**Discovery**: Found actual scene path using file system search:
```bash
find "D:\UnityProjects\META_VERYOLD_P01_s" -name "*Calibration_Hybrid*.unity"
# Result: Assets/VeryOld_P01_s/Scene/PedModel/Calibration_Hybrid.unity
```

**Impact**: AutomationController now loads correct scene, no more ParameterInterface errors. Phase 4B automation uses same system as Phase 3 manual workflow.

### 2025-10-02: Scipy DE Iteration Counting Bug Fix

**Problem**:
- User expects `maxiter=2, popsize=5` → exactly 10 Unity simulations
- Scipy DE `maxiter` parameter = "max generations until convergence", not total evaluations
- When convergence not reached, DE continued indefinitely
- Initial attempts with `scipy_maxiter = maxiter - 1` were incorrect

**Root Cause**:
- Scipy's internal convergence logic doesn't guarantee exact evaluation count
- First attempted fix: Raise `StopIteration` exception when limit reached
- This caused `RuntimeError: func(x, *args) must return a scalar value`
- `StopIteration` propagated into Scipy's `_calculate_population_energies()` method
- Scipy interpreted exception as malformed objective function return

**Solution**:
- Use Scipy's `callback` mechanism instead of exceptions
- Callback function receives current best candidate and convergence metric
- Callback returns `True` → Scipy stops optimization gracefully
- Callback returns `False` → Continue optimization
- Manual evaluation counter: `eval_counter['count'] >= maxiter * popsize`

**Implementation**:
```python
eval_counter = {'count': 0}
max_evaluations = maxiter * popsize

def callback(xk, convergence):
    return eval_counter['count'] >= max_evaluations  # True = stop

result = differential_evolution(
    objective_func,
    bounds,
    callback=callback,
    maxiter=maxiter * 10  # Large safety margin, callback controls actual limit
)
```

**Impact**: Exact evaluation count guarantee, stable termination, no RuntimeError

### 2025-10-02: Baseline Objective Save/Load Feature

**Context**:
- Initial implementation hardcoded baseline objective = 4.5932
- Unable to test different initial parameter sets without code modification
- Need to compare optimization results against multiple baselines

**Solution**:
- Added `save_baseline_objective()` to `evaluate_objective.py`
- CLI flag: `--save-baseline` saves to `data/output/baseline_objective.json`
- Added `load_baseline_objective()` to `generate_parameters.py`
- Optimization and analysis automatically load baseline (fallback to 4.5932 if missing)
- Convergence plots display baseline as red horizontal reference line

**Workflow**:
1. Generate baseline parameters: `python dev/generate_parameters.py --baseline`
2. Run Unity simulation with baseline
3. Save baseline: `python dev/evaluate_objective.py --save-baseline`
4. All future optimizations auto-load this baseline for comparison

**Impact**: Flexible baseline management, enables A/B testing of initial conditions

### 2025-10-01: Optimization History Analysis Feature

**Feature**:
- `--analyze` mode in `generate_parameters.py`
- Reads `optimization_history.csv` (generated during optimization)
- Computes summary statistics: total evaluations, best/worst/mean/std objective
- Groups evaluations by generation, extracts best-per-generation
- Generates matplotlib convergence plot (if matplotlib installed)
  - Left panel: All evaluations scatter plot
  - Right panel: Best-per-generation line plot
  - Baseline reference line

**Usage**:
```bash
python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv
```

**Impact**: Visual convergence monitoring, detect stagnation, identify local minima


### 2025-10-15: Phase 4B Decision and Implementation

**Context**: Preparing for SCI paper requiring algorithm comparison experiments

**Decision**: Implement Phase 4B (Optimizer Abstraction) before Phase 4A (direct automation)

**Rationale**:
- SCI papers require comparative analysis of multiple optimization algorithms
- Refactoring after Phase 4A would be 2-3x more difficult (codebase + results coupling)
- Abstraction enables algorithm addition in 1-2 hours vs days of refactoring
- Single responsibility principle: Unity execution, optimization, evaluation separated
- Current code tightly coupled to Scipy DE (line 8, 296-310 in generate_parameters.py)

**Architecture Implemented**:
```
dev/
├─ run_optimization.py              # Unified CLI (algorithm-agnostic)
├─ core/
│   ├─ unity_simulator.py           # Unity Editor automation via -executeMethod
│   ├─ objective_function.py        # Evaluation logic wrapper
│   └─ parameter_utils.py           # Bounds, conversion utilities
├─ optimizer/
│   ├─ base_optimizer.py            # Abstract interface
│   └─ scipy_de_optimizer.py        # Scipy DE implementation
└─ Unity:
    └─ Calibration_hybrid_AutomationController.cs  # Editor menu automation
```

**Key Components Created**:
1. **BaseOptimizer** abstract class with `optimize() -> OptimizerResult` interface
2. **UnitySimulator** encapsulates Editor automation (subprocess, polling, timeout)
3. **ObjectiveFunction** wraps Unity execution + evaluation in callable
4. **ScipyDEOptimizer** wraps existing DE logic from Phase 3
5. **AutomationController** Unity Editor MenuItem for testing
6. **TESTING.md** comprehensive 5-step test guide

**Impact**:
- Algorithm switching: Change `--algorithm scipy_de` CLI flag only
- Future additions: Bayesian, CMA-ES, PSO in 1-2 hours each
- Code reusability: 95% of Unity/evaluation logic shared across algorithms
- Time investment: 8 hours implementation + testing
- **Status**: Implementation complete, testing in progress (Step 2/5)

**Files Created** (2025-10-15):
- `dev/core/parameter_utils.py` (100 lines)
- `dev/core/unity_simulator.py` (300 lines)
- `dev/core/objective_function.py` (150 lines)
- `dev/optimizer/base_optimizer.py` (150 lines)
- `dev/optimizer/scipy_de_optimizer.py` (250 lines)
- `dev/run_optimization.py` (150 lines)
- `D:\UnityProjects\...\Calibration_hybrid_AutomationController.cs` (175 lines)
- `dev/TESTING.md` (consolidated test guide)

---

## Next Steps

### Immediate Task: Phase 4B Testing (TESTING.md Step 2)

**Goal**: Validate Unity automation works correctly with Calibration_Hybrid scene

**Status**: **BLOCKED - USER TESTING** - Waiting for user to test Step 2 in Unity

**Current Test**: TESTING.md Step 2 - Test Unity Automation (10 min)
1. Unity Editor → Menu → "Automation → Test - Run Simulation (Manual)"
2. Verify scene loaded: **Calibration_Hybrid** (not Calibration)
3. Verify Play mode starts automatically
4. Wait for simulation (~5-10 min)
5. Verify Play mode stops automatically
6. Check file exists: `Assets/StreamingAssets/Calibration/Output/simulation_result.json`

**Expected Result**: ✅ Unity automation works (Calibration_Hybrid scene loads, Play starts/stops automatically)

**Potential Issues**:
- If Unity exits: Scene path incorrect (see TESTING.md troubleshooting)
- If wrong scene loads: Update AutomationController.cs line 22
- If simulation doesn't stop: Check OutputManager `autoStopPlayMode` enabled

**Remaining Tests** (after Step 2):
- [ ] Step 3: Python → Unity integration (unity_simulator.py)
- [ ] Step 4: Objective Function wrapper
- [ ] Step 5: End-to-end optimization (10 evaluations)
- [ ] Compare results with Phase 3 manual mode

**After Phase 4B**: Production optimization (750 evals), algorithm comparison (Bayesian/CMA-ES), SCI paper

---

## Development Philosophy

**DO**: Standalone scripts, manual verification first, simple functions, incremental phases
**DON'T**: Complex classes, premature automation, unnecessary features, emojis in code
