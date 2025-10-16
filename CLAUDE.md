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

### "update md" Command Protocol

When user says **"update md"**, perform full session documentation:

**1. Review Session Work** (analyze what was done):
- Code changes and new features
- Bug fixes and decisions
- User's explicit requests and feedback
- Problems solved

**2. Update CLAUDE.md**:
- Current Status: Update phase, last session summary
- Completed: Check off finished items, add dates
- Development History: Add new entry if non-trivial bug/decision
- Next Steps: Update immediate task
- Development Commands: Add new workflows if any
- Remove stale information

**3. Update README.md**:
- 현재 상태: Update phase, recent updates
- 빠른 시작: Update if workflow changed
- 상세 사용법: Update if new features/options
- Quick Reference: Keep commands current
- Remove outdated troubleshooting

**4. Quality Checks**:
- Language: CLAUDE.md (English), README.md (Korean)
- No Korean in CLAUDE.md
- No low-level details (line counts, code snippets)
- No duplicate information between sections
- No stale/outdated commands or paths
- All examples tested and working
- Next session can /init and immediately continue work

**5. Final Verification**:
- Current phase clearly stated
- Last session captured (1-2 sentences)
- Next task actionable with acceptance criteria
- No rule violations (check Purpose, Structure, Language Policy)
- Information sufficient for perfect follow-up session

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
Python (run_optimization.py)
    ↓ eval_XXXX_parameters.json
Unity Simulation (PIONA/SFM 18 params)
    ↓ eval_XXXX_result.json
Python (objective_function.py)
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

**Phase**: Phase 4B Complete ✅
**Current Task**: Production optimization ready
**Last Session**: CLI refactoring (popsize+generations interface), seed reproducibility feature implemented. All Phase 4B work complete.

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

#### Phase 4B: Optimizer Abstraction Layer ✅ (Complete - 2025-10-16)
- [x] Architecture design (core/, optimizer/, analysis/ modules)
- [x] `optimizer/base_optimizer.py` - Abstract interface for all algorithms
- [x] `core/parameter_utils.py` - Parameter conversion utilities
- [x] `core/unity_simulator.py` - Unity Editor automation with file trigger system
- [x] `core/objective_function.py` - Evaluation logic (reusable)
- [x] `core/history_tracker.py` - Optimization history tracking (extracted)
- [x] `optimizer/scipy_de_optimizer.py` - Wrap existing Scipy DE code
- [x] `analysis/analyze_history.py` - Analysis functions (extracted)
- [x] `run_optimization.py` - Unified CLI with algorithm selection
- [x] `Calibration_hybrid_AutomationController.cs` - Unity Editor automation with file trigger
- [x] TESTING.md - Comprehensive test guide (5 steps)
- [x] **Testing complete**: All 5 steps validated (Steps 2-5)
- [x] **Bug fixes**: Scene path, .meta file warning, off-by-one error, simulation not stopping
- [x] **Feature additions**: File trigger system, Input-Output 1:1 matching, unique history files, auto-analysis
- [x] **Code cleanup**: Phase 3 archived, modular structure finalized
- [x] **CLI refactoring**: Intuitive popsize+generations interface (2025-10-16)
- [x] **Seed reproducibility**: Auto-generate and save random seeds for reproducibility (2025-10-16)

### Next

#### Production Optimization (Ready to start)
- [ ] Run production optimization (720 evaluations, ~2-3 days)
  - Recommended: `python dev/run_optimization.py --algorithm scipy_de`
  - Alternative: `python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5` (1350 evals)
  - Unity Editor must be open during execution
  - Can run unattended after initial confirmation
  - Specify seed only for reproducibility: `--seed 42`
- [ ] Analyze convergence and parameter sensitivity
- [ ] Compare with baseline (4.5932)
- [ ] Document final calibrated parameters

#### Future Work (Phase 5+)
- [ ] Implement alternative algorithms (Bayesian, CMA-ES) for SCI paper comparison
- [ ] Add resume capability for interrupted optimizations
- [ ] Parallel simulation execution (if multiple Unity instances feasible)

**Blocker**: None. System fully functional and tested.

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

### Phase 4B: Automated Optimization (Production Ready)
```bash
# Default (720 evals, ~2-3 days)
python dev/run_optimization.py --algorithm scipy_de
# → popsize=10, generations=4 → 10×18×4 = 720 evals

# Quick test (36 evals, ~5 hours)
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

# Production with more exploration (1350 evals, ~5 days)
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5

# Reproducible run (for experiments)
python dev/run_optimization.py --algorithm scipy_de --seed 42

# Manual analysis (auto-called after optimization)
python -c "from dev.analysis.analyze_history import analyze_optimization_history; analyze_optimization_history('data/output/optimization_history_*.csv')"
```

### Phase 3: Manual Optimization (Archived)
```bash
# See archive/phase3/README.md for Phase 3 documentation
# Phase 3 files moved to archive/phase3/

# If needed, run archived manual mode:
python archive/phase3/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5
```

### Key Paths

**Unity**: `D:\UnityProjects\META_VERYOLD_P01_s\`
- Scripts: `Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`
- Scene: `Assets\VeryOld_P01_s\Scene\PedModel\Calibration_Hybrid.unity`
- Input: `Assets\StreamingAssets\Calibration\Input\eval_XXXX_parameters.json`
- Output: `Assets\StreamingAssets\Calibration\Output\eval_XXXX_result.json`

**Python**: `c:\dev\calibration_hybrid\`
- Main: `dev/run_optimization.py` (unified entry point)
- Core: `dev/core/` (unity_simulator, objective_function, parameter_utils, history_tracker)
- Optimizers: `dev/optimizer/` (scipy_de_optimizer)
- Analysis: `dev/analysis/` (analyze_history)
- Results: `data/output/` (baseline_objective.json, best_parameters.json, optimization_history_*.csv)
- Archive: `archive/phase3/` (old manual mode)

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
   - Saves eval_XXXX_result.json to StreamingAssets/Output/
   - Auto-stops Play mode when complete

**Python Side** (c:\dev\calibration_hybrid\dev\) - Phase 4B Modular Architecture:
1. `run_optimization.py`
   - Main entry point for all optimization algorithms
   - CLI with algorithm selection (`--algorithm scipy_de`)
   - Handles Unity automation coordination
   - Auto-generates analysis after completion
2. `core/unity_simulator.py`
   - Unity Editor automation via file trigger system
   - Writes trigger_simulation.txt → Unity detects → runs simulation
   - Input-Output 1:1 matching (eval_0001_parameters.json ↔ eval_0001_result.json)
   - Deletes both .json and .meta files to avoid Unity warnings
3. `core/objective_function.py`
   - Wraps Unity execution + objective calculation
   - Calls unity_simulator.run_simulation()
   - Computes 3-metric objective function
   - Tracks history automatically
4. `core/history_tracker.py`
   - OptimizationHistory class (extracted from Phase 3)
   - Unique CSV filenames with timestamp and algorithm info
   - Format: optimization_history_ScipyDE_pop5_best1bin_20251016_163602.csv
5. `optimizer/scipy_de_optimizer.py`
   - Scipy Differential Evolution wrapper
   - Callback-based early stopping for exact evaluation count
   - Checks limit BEFORE evaluation to prevent off-by-one error
6. `analysis/analyze_history.py`
   - analyze_optimization_history() function (extracted from Phase 3)
   - Convergence plots (all evals + best per generation)
   - Baseline comparison
7. `export_to_unity.py`
   - Converts Python dict to Unity JSON
   - Validates parameters against bounds
   - Auto-clamps out-of-bounds values
   - Generates experiment IDs
8. `evaluate_objective.py`
   - Loads simulation_result.json
   - Computes 3-metric objective function
   - Saves/loads baseline for comparison
9. `load_simulation_results.py`
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

**Unity → Python** (eval_XXXX_result.json / simulation_result.json):
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
    popsize=15,               # Population multiplier (NOT absolute size)
    mutation=(0.5, 1.0),      # Default mutation factor range
    recombination=0.7,        # Default crossover probability
    callback=early_stop_callback  # Hard limit on evaluations
)
```

**IMPORTANT: Scipy popsize Behavior**:
- `popsize` is a **multiplier**, not absolute population size
- Actual population = `popsize × n_parameters = popsize × 18`
- **Total evaluations** = `(popsize × 18) × generations`
- Example: `popsize=10, generations=4` → 10×18×4 = 720 evaluations

**Recommended Settings**:
```bash
# Default (balanced, recommended)
python dev/run_optimization.py --algorithm scipy_de
# → popsize=10, generations=4 → 720 evals

# More exploration (larger population)
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5
# → 15×18×5 = 1350 evals

# More convergence (more generations)
python dev/run_optimization.py --algorithm scipy_de --popsize 8 --generations 8
# → 8×18×8 = 1152 evals

# Quick test
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1
# → 2×18×1 = 36 evals
```

**Theory Guidelines**:
- Population size: 5N ~ 10N recommended (N=18 → 90~180 individuals)
  - `popsize=5~10` is optimal range
- Minimum generations: 3+ (1 gen = random search, no evolution)
- No complex calculation needed - just set `--popsize` and `--generations`

**Expected Runtime**: 1-3 days (5-10 min per simulation)

---

## Development History

### 2025-10-16: CLI Refactoring and Seed Reproducibility

**Context**: User feedback on confusing `--max-evals` parameter and seed reproducibility concerns

**Problem 1 - Non-intuitive CLI**:
- Users had to manually calculate: `max-evals = popsize × 18 × generations`
- Example: `--max-evals 720 --popsize 10` → user must know 720 = 10×18×4
- Scipy's `popsize` as multiplier (not absolute size) was non-intuitive
- `--seed 42` always used → no exploration diversity between runs

**Solution 1 - Direct generations Parameter**:
```bash
# Before (complex)
--max-evals 720 --popsize 10 --seed 42

# After (intuitive)
--popsize 10 --generations 4
# → auto-calculates: 10×18×4 = 720 evals
```

**Problem 2 - Seed Reproducibility**:
- User concern: With `seed=None`, results non-reproducible
- Scipy generates random seed internally but doesn't save it
- No way to reproduce results without knowing seed value

**Solution 2 - Auto-generate and Save Seed**:
- Auto-generate random seed if None (0 to 2^31-1)
- Store seed in `OptimizerResult.seed` field
- Print reproduction command in console output
- Save seed to result JSON file for later reference

**Changes Made**:
1. **New `--generations` parameter**: Direct control over evolution cycles (default: 4)
2. **`--max-evals` now optional**: Only used as safety override (default: None)
3. **`--seed` default None**: Random seed each run, auto-generated and saved
4. **`--popsize` default 10** (was 15): More balanced for 18D problem (180 individuals/gen)
5. **Auto-calculation**: `max_evals = popsize × n_params × generations` when not specified
6. **Seed storage**: Added `seed` field to `OptimizerResult` and result JSON files
7. **Seed reproduction guide**: Console prints exact command to reproduce results

**Impact**:
- ✅ Intuitive interface: Users think in DE concepts (10 individuals, 4 generations)
- ✅ No mental math required for evaluation count
- ✅ Seed diversity by default (auto-generated each run)
- ✅ Full reproducibility: seed saved in result JSON and printed in console
- ✅ Backward compatible: old `--max-evals` style still works

### 2025-10-16: Phase 4B Refinements and Code Cleanup

**Context**: After initial Phase 4B implementation and testing, several issues and improvements identified

**Issues Fixed**:
1. **File Trigger System** - Replaced subprocess mode with file trigger to avoid "Multiple instances" error
2. **Unity .meta File Warning** - Added code to delete both .json and .meta files
3. **Off-by-one Error** - 11th evaluation started when max-evals=10. Fixed by checking limit BEFORE evaluation
4. **Simulation Not Stopping** - Optimization continued past limit. Fixed with proper early stopping
5. **Input-Output Mismatch** - simulation_result.json (fixed name) vs eval_xxxx_parameters.json (unique). Implemented 1:1 matching

**Features Added**:
1. **File Trigger System** (default mode):
   - Python writes `trigger_simulation.txt`
   - Unity polls for trigger file via `[InitializeOnLoad]` static constructor
   - Unity detects → deletes trigger → runs simulation
   - Advantage: Unity Editor stays open (no 30s startup overhead)

2. **Input-Output 1:1 Matching**:
   - Modified `OutputManager.cs` to use experimentId from InputManager
   - Dynamic filenames: `eval_0001_parameters.json` ↔ `eval_0001_result.json`
   - Complete traceability for each evaluation

3. **Unique History Files**:
   - Format: `optimization_history_ScipyDE_pop5_best1bin_20251016_163602.csv`
   - Includes algorithm name and timestamp
   - Allows comparing different experiments without overwriting

4. **Automatic Analysis**:
   - Convergence plot auto-generated after optimization completes
   - Baseline comparison in plots
   - Summary statistics printed

**Code Cleanup**:
- Extracted `OptimizationHistory` class → `dev/core/history_tracker.py`
- Extracted `analyze_optimization_history()` → `dev/analysis/analyze_history.py`
- Moved `generate_parameters.py` → `archive/phase3/`
- Created `archive/phase3/README.md` explaining manual mode
- Organized test data: `archive/phase3_tests/` and `archive/phase4b_tests/`
- Updated imports in `run_optimization.py` to use new module structure

**Testing Complete**: All 5 steps from TESTING.md validated

**Impact**: Production-ready automated system with clean modular architecture

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
- Time investment: 8 hours implementation + 8 hours testing/refinement
- **Status**: Complete and production-ready (2025-10-16)

**Files Created**:
- Python modules: `core/`, `optimizer/`, `analysis/` directories
- Unity: `Calibration_hybrid_AutomationController.cs`
- Documentation: `dev/TESTING.md`, `archive/phase3/README.md`

---

## Next Steps

### Immediate Task: Production Optimization

**Goal**: Run full-scale optimization to find best 18 SFM parameters

**Status**: Ready to start (Phase 4B complete, all tests passed)

**Recommended Commands**:
```bash
# Default (balanced, recommended)
python dev/run_optimization.py --algorithm scipy_de
# → Uses default: popsize=10, generations=4 → 720 evals

# Reproducible run (for experiments)
python dev/run_optimization.py --algorithm scipy_de --seed 42

# More exploration
python dev/run_optimization.py --algorithm scipy_de --popsize 15 --generations 5
# → 1350 evals
```

**Prerequisites**:
- Unity Editor must be open with `Calibration_Hybrid.unity` scene
- Estimated time: ~2-3 days (720-810 evaluations × 5-10 min each)
- Can run unattended after initial confirmation prompt

**Expected Outputs**:
- `data/output/best_parameters.json` - Best 18 SFM parameters found
- `data/output/optimization_history_ScipyDE_pop10_best1bin_YYYYMMDD_HHMMSS.csv` - Full history
- `data/output/optimization_history_ScipyDE_pop10_best1bin_YYYYMMDD_HHMMSS.png` - Convergence plot
- `data/output/result_ScipyDE_pop10_best1bin_YYYYMMDD_HHMMSS.json` - Full result metadata

**Success Criteria**:
- Objective < 4.5932 (baseline)
- Convergence visible in plot (diminishing improvements)
- No Unity crashes or errors during optimization

**After Production Run**:
1. Analyze parameter sensitivity
2. Validate calibrated parameters with held-out test data
3. Document results for SCI paper
4. Implement alternative algorithms (Bayesian, CMA-ES) for comparison

**Blockers**: None

---

## Development Philosophy

**DO**: Standalone scripts, manual verification first, simple functions, incremental phases
**DON'T**: Complex classes, premature automation, unnecessary features, emojis in code
