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

**Phase**: Phase 3 Complete, Phase 4 Pending
**Current File**: N/A (awaiting user decision)
**Last Session**: Restructured CLAUDE.md to English with writing rules for better session continuity

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

### Next

#### Phase 4: Full Automation ⏳ (Pending)
- [ ] `run_optimization.py` - Automated Unity batch mode execution
  - [ ] Launch Unity via subprocess with batch mode flags
  - [ ] Wait for simulation completion (timeout 10min)
  - [ ] Load results and continue optimization loop
  - [ ] Handle Unity crashes/errors gracefully
  - [ ] Progress tracking with tqdm
  - [ ] Checkpoint/resume capability

**Blocker**: Waiting for user confirmation that Phase 3 manual testing is satisfactory before implementing automation.

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

### Baseline Setup (Run Once)
```bash
# 1. Generate baseline parameters from Unity defaults
python dev/generate_parameters.py --baseline

# 2. Export to Unity JSON format
python dev/export_to_unity.py --input data/input/baseline_parameters.json --auto-id

# 3. Run Unity simulation manually
# Open: D:\UnityProjects\META_VERYOLD_P01_s\
# Load: Calibration.unity scene
# Press Play button → Wait for simulation to complete and auto-stop

# 4. Save baseline objective for future comparison
python dev/evaluate_objective.py --save-baseline
# Creates: data/output/baseline_objective.json
```

### Optimization Workflow (Phase 3 - Manual)
```bash
# Test run: 2 generations × 5 individuals = 10 Unity simulations
python dev/generate_parameters.py --optimize --manual --maxiter 2 --popsize 5

# Script will:
# 1. Generate new parameters
# 2. Export to Unity JSON
# 3. Print: "Press ENTER after Unity simulation completes..."
# 4. User manually runs Unity Play button
# 5. User presses ENTER when done
# 6. Script evaluates objective and continues

# Production run: 50 generations × 15 individuals = 750 simulations (~1-3 days)
python dev/generate_parameters.py --optimize --manual --maxiter 50 --popsize 15
```

### Analysis Commands
```bash
# Analyze optimization history with convergence plots
python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv

# Evaluate single simulation result
python dev/evaluate_objective.py --verbose

# Compare multiple results
python dev/evaluate_objective.py --compare result1.json result2.json

# Inspect simulation data
python dev/load_simulation_results.py --verbose --agent-id 4236
```

### File Paths Reference

**Unity Project**:
- Project root: `D:\UnityProjects\META_VERYOLD_P01_s\`
- Unity scripts: `Assets\VeryOld_P01_s\Dev\Calibration_hybrid\`
- Parameter input: `Assets\StreamingAssets\Calibration\Input\*_parameters.json`
- Result output: `Assets\StreamingAssets\Calibration\Output\simulation_result.json`
- Trajectory data: `Assets\StreamingAssets\Data\PedestrianTrajectory\ATC\atc_resampled_1s_noQueing.csv`

**Python Workspace**:
- Scripts: `c:\dev\calibration_hybrid\dev\`
- Input (version control): `data/input/`
- Output (results): `data/output/`
  - `baseline_objective.json` - Auto-loaded by optimization/analysis
  - `optimization_history.csv` - Full evaluation log
  - `best_parameters.json` - Best parameters found so far
  - `optimization_history.png` - Convergence plot with baseline

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

### 2025-09-30: Chose Scipy DE over TuRBO/AxPlatform

**Context**: Selecting optimization algorithm for 18-parameter black-box calibration

**Options Considered**:
1. **TuRBO** (Trust Region Bayesian Optimization)
   - Pros: State-of-the-art for high-dim (50-1000D)
   - Cons: Complex setup, designed for 50+ dimensions, requires tuning
2. **Ax Platform** (Adaptive Experimentation)
   - Pros: Multi-objective, parallel evaluations, enterprise features
   - Cons: Heavy framework, overkill for 18D single-objective
3. **Scipy DE** (Differential Evolution)
   - Pros: Simple, robust, optimal for 10-40D, no gradients needed
   - Cons: Not cutting-edge, slower than gradient methods (not applicable here)

**Decision**: Scipy Differential Evolution

**Rationale**:
- 18D is in DE's sweet spot (TuRBO overkill)
- Unity simulation is black-box → gradient-free required
- 3-4 hyperparameters vs 15+ for TuRBO
- 30 years of validation in literature
- Aligns with project philosophy: simplicity, manual verification at each phase

**Configuration**: `popsize=15, maxiter=50, strategy='best1bin'` → 750 evaluations

### 2025-09-29: Unity Auto-Stop Play Mode

**Problem**: Manual optimization workflow required user to stop Unity Play mode after each simulation

**Solution**:
- Added `autoStopPlayMode` boolean flag to `Calibration_hybrid_OutputManager.cs`
- After saving simulation_result.json, automatically exit Play mode
- Editor mode: `EditorApplication.isPlaying = false`
- Build mode: `Application.Quit()`

**Impact**: Reduced manual steps in Phase 3 workflow (user only needs to press Play, not Stop)

### 2025-09-29: Unity InputManager Architecture

**Decision**: Create `Calibration_hybrid_InputManager.cs` as single source of truth for parameters

**Architecture**:
- InputManager loads parameters JSON at scene start
- Validates and clamps all 18 parameters to bounds
- Provides public static accessors for parameter values
- OutputManager reads parameters from InputManager (not SFM instances)
- SFM instances read parameters from InputManager in Start()

**Rationale**:
- Previous approach: OutputManager queried SFM instances via reflection (fragile)
- Problem: Agents destroyed before OutputManager could collect parameters
- Solution: Centralized parameter storage independent of agent lifecycle

**Impact**: Robust parameter tracking, eliminates race conditions

---

## Next Steps

### Immediate Task: Phase 4 Automation

**Goal**: Implement fully automated optimization loop without user intervention

**Status**: **BLOCKED** - Awaiting user confirmation that Phase 3 manual testing is complete and satisfactory

**When Unblocked**:

**File to Create**: `dev/run_optimization.py`

**Requirements**:
1. Launch Unity in batch mode via subprocess
   - Command: `Unity.exe -batchmode -nographics -quit -executeMethod [method] -logFile -`
   - Requires Unity C# method to load scene and start simulation
2. Wait for simulation completion
   - Poll for simulation_result.json file creation
   - Timeout: 10 minutes per simulation
   - Handle Unity crashes (check process exit code)
3. Load results and evaluate objective
   - Reuse `evaluate_objective.py` functions
4. Feed objective back to Differential Evolution
   - Same callback mechanism as manual mode
5. Progress tracking
   - tqdm progress bar showing current iteration/total
   - ETA calculation
6. Checkpoint/resume
   - Save optimization state after each evaluation
   - Resume from checkpoint if interrupted

**Acceptance Criteria**:
```bash
python dev/run_optimization.py --maxiter 2 --popsize 5
# Should run 10 Unity simulations without user intervention
# Should display progress bar
# Should handle Unity crashes gracefully
# Should save optimization history and best parameters
```

**Technical Challenges**:
- Unity batch mode execution on Windows (path handling, arguments)
- Unity error detection (parse log file for exceptions)
- Process timeout and cleanup (kill Unity if frozen)
- Checkpoint serialization (pickle Scipy DE state)

**Estimated Effort**: 4-6 hours implementation + 2-3 hours testing

---

## Development Philosophy

### DO
- Write standalone, independently executable scripts
- Enable manual verification at each step before automation
- Keep code simple and function-oriented (not complex classes)
- Document architectural decisions with rationale
- Build incrementally: Phase 1 → 2 → 3 → 4

### DON'T
- Create complex class hierarchies unnecessarily
- Attempt full automation before manual verification works
- Add features not explicitly needed
- Use emojis in code (OK in .md files)
- Increase code volume without clear benefit

### Code Style
- Each script runnable independently via `if __name__ == '__main__'`
- argparse for command-line arguments
- Docstrings with brief usage examples
- Function-oriented over class-oriented
- English comments and variable names

---

## Testing Strategy

No automated unit tests currently. Manual verification workflow:

**Phase 1 Test**: Load sample Unity JSON, print statistics
**Phase 2 Test**: Evaluate multiple result files, compare objectives
**Phase 3 Test**: Run 1-2 optimization iterations manually, verify history
**Phase 4 Test**: Run automated optimization for 10 evaluations, verify results match manual mode

**Future**: Consider pytest for data loading/validation functions (low priority)
