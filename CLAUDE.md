# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## CLAUDE.md Writing Rules

### Purpose
- **CLAUDE.md**: For Claude Code (AI assistant) - Current status, architecture, next steps (lean, recent focus)
- **README.md**: For humans (users, developers) - Installation, usage instructions, how-to guides
- **DEV_HISTORY.md**: Complete development journal - All decisions, bugs, changes (chronological archive)

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

**5. Development History** (Recent critical items only)
- Keep only last 30 days OR most recent 2-3 entries
- Format: `YYYY-MM-DD: Title`
- Include: Problem/Context, Solution/Rationale, Impact
- Move older entries to DEV_HISTORY.md (never delete)
- Link to DEV_HISTORY.md for full history

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
- Development History: Add new entry (keep only recent 2-3, move old to DEV_HISTORY.md)
- Next Steps: Update immediate task
- Development Commands: Add new workflows if any
- Remove stale information

**2.5. Update DEV_HISTORY.md**:
- Add new entry at TOP (reverse chronological)
- Format: YYYY-MM-DD: Title
- Include: Full context, problem, solution, impact, files modified
- Never delete old entries
- This is permanent archive

**3. Update README.md**:
- 현재 상태: Update phase, recent updates
- 빠른 시작: Update if workflow changed
- 상세 사용법: Update if new features/options
- Quick Reference: Keep commands current
- Remove outdated troubleshooting

**3.5. Cleanup README.md** (Automatic trim):
- **최근 업데이트**: Keep only last 3-5 items (remove old updates)
- **상세 사용법**: Remove deprecated commands/options
- **문제 해결**: Remove solved issues, keep only common recurring issues
- **프로젝트 구조**: Update if changed, remove outdated paths
- **Target**: README.md should stay ~300-350 lines (never >400)

**4. Cleanup CLAUDE.md** (Automatic trim to prevent bloat):
- **Completed sections**: Archive finished phases (move details to DEV_HISTORY.md if needed)
  - Keep only current phase details
  - Old phases: Single checkmark line only
- **Development History**: Keep ONLY 2 most recent entries
  - Move 3rd+ entries to DEV_HISTORY.md
  - Each entry: Max 15 lines (Problem/Solution/Impact only)
- **Next Steps**: Remove completed tasks
  - Keep only pending and immediate next tasks
  - Archive old "Future Work" if stale
- **Examples/Code blocks**: Remove if outdated
  - JSON schemas: Keep minimal examples only
  - Commands: Keep only currently used workflows
- **Target**: CLAUDE.md should stay ~400-500 lines (never >600)

**5. Prepare for "follow" command**:
- Ensure "Next Steps" in CLAUDE.md has clear immediate task
- Verify "Last Session" summary is accurate (1-2 sentences)
- Check all three docs are consistent
- Next session "follow" should have zero confusion

**6. Quality Checks**:
- Language: CLAUDE.md (English), README.md (Korean)
- No Korean in CLAUDE.md
- No low-level details (line counts, code snippets)
- No duplicate information between sections
- No stale/outdated commands or paths
- All examples tested and working
- **File size**: CLAUDE.md <600 lines, README.md <400 lines

**7. Final Verification**:
- Current phase clearly stated
- Last session captured (1-2 sentences)
- Next task actionable with acceptance criteria
- No rule violations (check Purpose, Structure, Language Policy)
- Information sufficient for perfect "follow" continuation
- **Token efficiency**: Lean enough for daily /init without waste

### Quality Checklist
Before ending session, verify:
- [ ] Current phase clearly stated
- [ ] Completed items checked off
- [ ] Next task with acceptance criteria defined
- [ ] Bugs/decisions documented in History
- [ ] Commands for next session present
- [ ] No stale/outdated information

### "follow" Command Protocol

When user says **"follow"** at session start, perform comprehensive project analysis:

**1. Read Core Documentation** (in order):
- CLAUDE.md (current status, next steps, recent history)
- README.md (verify user-facing accuracy)
- DEV_HISTORY.md (skim recent 2-3 entries for context)

**2. Extract Critical Information**:
- **Current Phase**: From "Current Status" (e.g., "Phase 4B+ Complete")
- **Current Task**: From "Current Task" line (e.g., "Production run ready")
- **Last Session**: What was done (1-2 sentence summary)
- **Next Steps**: Immediate task from "Next Steps" section
- **Blockers**: Any prerequisites or issues mentioned

**3. Verify Codebase Alignment** (spot check):
- Key paths exist (Unity project, Python dev/, data/output/)
- Recent output files exist if mentioned (best_parameters.json, history CSVs)
- Git status if relevant (uncommitted changes warning)

**4. Present Continuation Summary** (concise format):
```
📍 **Current State**
- Phase: [phase name]
- Last Session: [what was accomplished]
- Status: [ready/blocked/in-progress]

🎯 **Next Task**
- Goal: [clear objective]
- Command: [exact command to run]
- Expected: [outputs, time estimate]
- Prerequisite: [if any]

📋 **Continuation Plan**
1. [Step 1]
2. [Step 2]
3. [Step 3]

Ready to proceed? (yes/no)
```

**5. Execute with Approval**:
- Wait for user confirmation
- Use TodoWrite for multi-step tasks
- Update documentation when complete

**Critical Success Criteria**:
- ✅ Can answer: "What phase are we in?"
- ✅ Can answer: "What did last session accomplish?"
- ✅ Can answer: "What's the next immediate task?"
- ✅ Can provide: Exact command to continue work
- ✅ Zero need for user to explain context

**Goal**: Zero context loss, immediate productive continuation

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
3. Python computes objective (RMSE + 95th percentile + time growth + density)
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

**Phase**: Phase 4B+ Complete ✅ (Production Ready)
**Current Task**: Production run ready (720 evals, ~2-3 days)
**Last Session**: Fixed critical race condition bug (JSON parsing error at iteration 64/720). Implemented file stability check with size monitoring + JSON validation. System now production-ready with robust error handling.

### Completed

- [x] **Phase 1**: Data Pipeline ✅
- [x] **Phase 2**: Objective Function ✅
- [x] **Phase 3**: Manual Optimization (archived) ✅
- [x] **Phase 4B**: Optimizer Abstraction Layer ✅ (modular architecture, Unity automation)

#### Phase 4B+: Objective Function Enhancements ✅ (Complete - 2025-10-17)
- [x] **Density Metric** - Macroscopic crowd behavior validation
- [x] **RMSE Metric** - Changed from MAE (literature standard)
- [x] **TimeGrowthPenalty Improvement** - Linear regression instead of first/last 25%
- [x] **Generation Tracking** - CSV now includes generation column
- [x] **Enhanced History Tracking** - Individual metrics in CSV
- [x] **Seed Reproduction Commands** - Auto-print at completion
- [x] **Baseline Remeasurement** - New baseline: 2.8254 (RMSE-based)
- [x] **Auto-detect Latest Result** - evaluate_objective.py finds newest *_result.json
- [x] **Unity DensityAnalyzer** - Grid-based spatial density tracking (40×40 grid, 2.5m cells)
- [x] **Graph Bug Fix** - Generation size calculation corrected in analyze_history.py
- [x] **Grid Resolution Optimization** - Upgraded from 10×10 (10m cells) to 40×40 (2.5m cells)
- [x] **Documentation System** - DEV_HISTORY.md + "follow" protocol + auto-cleanup rules
- [x] **Race Condition Fix** - File stability check for 65MB JSON files (2025-10-20)

### Next Steps

**Immediate**: Production optimization (720 evals, ~2-3 days)
1. Verify Unity Scene: DensityAnalyzer component has 40×40 grid
2. Remeasure baseline: `python dev/evaluate_objective.py --save-baseline`
3. Run optimization: `python dev/run_optimization.py --algorithm scipy_de`
4. Analyze results and document for SCI paper

**Prerequisite**: Unity Editor open with Calibration_Hybrid.unity scene

**Future**:
- Alternative algorithms (Bayesian, CMA-ES) for SCI paper comparison
- Resume capability for interrupted optimizations

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

### Data Exchange Format

**Python → Unity**: `eval_XXXX_parameters.json` (18 SFM params + experimentId + timestamp)
**Unity → Python**: `eval_XXXX_result.json` (parameters + agentErrors[] + densityMetrics + metadata)

### Objective Function Formula

**Objective** (lower is better):
```
Objective = 0.40 × RMSE + 0.25 × Percentile95 + 0.15 × TimeGrowth + 0.20 × DensityDiff
```

**Components**:
1. **RMSE** (40% weight) - Root Mean Square Error
   - Individual trajectory accuracy
   - More sensitive to large errors than MAE (literature standard)
   - Calculation: sqrt(mean([agent_mean_error²]))

2. **Percentile95** (25% weight)
   - 95th percentile of agent errors
   - Robustness: penalizes outliers without being overly sensitive
   - Ignores worst 5% to prevent extreme outlier influence

3. **TimeGrowthPenalty** (15% weight)
   - Temporal stability measurement
   - Calculation: Linear regression slope of error over time (scipy.stats.linregress)
   - Only penalizes positive slopes (growing errors)
   - Negative slopes (improving accuracy) = no penalty

4. **DensityDifference** (20% weight) - NEW!
   - Macroscopic crowd behavior validation
   - Calculation: RMSE of agent density across 40×40 spatial grid (2.5m cells)
   - Ensures crowd flow patterns match reality (not just individual trajectories)
   - Cell size: 2.5m × 2.5m = 6.25m² (3-13 pedestrians per cell typical)

**Baseline**: 2.8254 (Unity default parameters, RMSE-based)
- Previous baseline (MAE-based): 4.5932
- Change reflects RMSE + improved TimeGrowth + density metrics

### Optimization Algorithm

**Scipy Differential Evolution** - Population-based, gradient-free, 18D parameter space

**Key Settings**:
- `popsize` = multiplier (NOT absolute size). Actual population = `popsize × 18`
- Total evals = `popsize × 18 × generations`
- Default: `popsize=10, generations=4` → 720 evals (~2-3 days)

**Usage**: See Development Commands section

---

## Development History

**Recent Critical Entries** (Last 30 days):

### 2025-10-20: Critical Race Condition Fix - JSON Parsing Error

**Problem**: Production run failed at iteration 64/720 - Python reading 65MB JSON files while Unity still writing (race condition)

**Solution**: File stability check - monitors file size stability (2×0.5s) + JSON validation before reading

**Impact**: Prevents optimization crashes, +1s overhead per eval (negligible), production-ready robustness

### 2025-10-17: Phase 4B+ Objective Function Enhancements

**Problem**: Missing macroscopic validation, MAE vs RMSE, simple TimeGrowth calc, no generation tracking

**Solution**: 8 enhancements - Density metric (40×40 grid), RMSE conversion, TimeGrowth linear regression, generation column, enhanced history, seed reproduction, auto-detect result, grid optimization

**Impact**: Production-ready objective function with macroscopic validation (SCI paper ready)

---

**Full History**: See [DEV_HISTORY.md](DEV_HISTORY.md) for complete chronological record of all development decisions, bug fixes, and architectural changes since project start.

---

