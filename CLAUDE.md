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

**Phase**: Phase 4D - Algorithm Analysis & Configuration ✅
**Current Task**: Identified DE configuration issue - need proper generation count for convergence
**Last Session**: Completed 720-eval production run. Analyzed results revealing poor convergence (only 5 improvements in 720 evals). Root cause: 4 generations insufficient for DE evolution. Created result extraction utility. Fixed result filename matching to history CSV.

### Completed

- [x] **Phase 1**: Data Pipeline ✅
- [x] **Phase 2**: Objective Function ✅
- [x] **Phase 3**: Manual Optimization (archived) ✅
- [x] **Phase 4B**: Optimizer Abstraction Layer ✅ (modular architecture, Unity automation)
- [x] **Phase 4B+**: Objective Function Enhancements ✅ (density, RMSE, time growth)
- [x] **Phase 4C**: Resume System ✅ (checkpoint, archive, recovery) - 2025-10-22

#### Phase 4C: Resume System ✅ (Complete - 2025-10-22)
- [x] **File Archiving System** - Fixed filenames in Unity, archive to data/input/parameters & data/output/results
- [x] **Checkpoint Save** - Every iteration with eval_counter, generation, best_params, random_state
- [x] **Resume Logic** - Restore from checkpoint with --resume flag
- [x] **Generation Tracking Fix** - CSV generation column used directly, not estimated
- [x] **Result Accuracy** - Extract true best from history CSV (not optimizer's 1e10 penalty)
- [x] **Time Estimation** - Separate remaining/total time display for resume/normal mode
- [x] **Random State Recovery** - Perfect reproducibility via np.random.set_state()
- [x] **Utility Scripts** - rebuild_history.py, create_checkpoint.py for manual recovery

#### Phase 4D: Algorithm Analysis & Configuration ✅ (Complete - 2025-10-24)
- [x] **Production Run Complete** - 720 evals finished, best objective: 1.7306 (38% improvement)
- [x] **Result Filename Fix** - Result JSON now matches history CSV name (history_XXX.csv → result_XXX.json)
- [x] **Result Extraction Utility** - generate_result_from_history.py for extracting results from completed runs
- [x] **Convergence Analysis** - Discovered poor convergence: only 5 improvements in 720 evals, best found at iteration 273
- [x] **Root Cause Identified** - 4 generations insufficient for DE (popsize=10, gen=4), resembles random sampling

### Next Steps

**Immediate**: Re-run optimization with proper DE configuration
1. Run with more generations for true convergence: `python dev/run_optimization.py --algorithm scipy_de --popsize 4 --generations 10 --seed 42`
   - Same 720 evals (4×18×10 = 720)
   - 10 generations allows evolution/convergence
   - Compare with previous run (best=1.7306) to verify if it was just random luck
2. Analyze convergence behavior (generation-wise improvement)
3. Document findings for SCI paper

**Current Results** (popsize=10, gen=4):
- 720 evals completed, best objective: 1.7306 (38% improvement over baseline 2.8254)
- Best found at iteration 273 (Gen 2), no improvement in subsequent 447 evals
- Only 5 total improvements in 720 evals (0.7%) - resembles random sampling

**Future**:
- Longer run with proper generations (e.g., popsize=5, gen=20 = 1800 evals)
- Alternative algorithms (Bayesian, CMA-ES) for SCI paper comparison
- Multi-run comparison for statistical significance

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

### Phase 4B/4C: Automated Optimization with Resume
```bash
# Default (720 evals, ~2-3 days)
python dev/run_optimization.py --algorithm scipy_de
# → popsize=10, generations=4 → 10×18×4 = 720 evals

# Resume from checkpoint (continues from last saved state)
python dev/run_optimization.py --algorithm scipy_de --resume

# Quick test (36 evals, ~5 hours)
python dev/run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

# Reproducible run (for experiments)
python dev/run_optimization.py --algorithm scipy_de --seed 42

# Manual analysis (auto-called after optimization)
python -c "from dev.analysis.analyze_history import analyze_optimization_history; analyze_optimization_history('data/output/history_*.csv')"

# Extract result JSON from completed history CSV
python dev/utils/generate_result_from_history.py data/output/history_ScipyDE_best1bin_YYYYMMDD_HHMMSS.csv

# Manual recovery from interrupted run
python dev/utils/rebuild_history.py      # Rebuild history from result files
python dev/utils/create_checkpoint.py    # Create checkpoint from history
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
- Input: `Assets\StreamingAssets\Calibration\Input\current_parameters.json` (fixed filename)
- Output: `Assets\StreamingAssets\Calibration\Output\current_result.json` (fixed filename)

**Python**: `c:\dev\calibration_hybrid\`
- Main: `dev/run_optimization.py` (unified entry point with --resume)
- Core: `dev/core/` (unity_simulator, objective_function, parameter_utils, history_tracker)
- Optimizers: `dev/optimizer/` (scipy_de_optimizer with checkpoint)
- Analysis: `dev/analysis/` (analyze_history with generation fix)
- Utils: `dev/utils/` (rebuild_history, create_checkpoint)
- Data Archives: `data/input/parameters/`, `data/output/results/` (eval_XXXX files)
- Results: `data/output/` (checkpoint_latest.pkl, history_*.csv, result_*.json)
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
- **IMPORTANT**: Generations must be sufficient for evolution (minimum 10+, ideally 20-50)

**Recommended Configurations**:
```python
# Quick test (720 evals, ~2-3 days)
popsize=4, generations=10  # 72 individuals × 10 gen = 720

# Moderate run (1800 evals, ~7 days)
popsize=5, generations=20  # 90 individuals × 20 gen = 1800

# Production run (3600 evals, ~14 days)
popsize=5, generations=40  # 90 individuals × 40 gen = 3600
```

**AVOID**: `popsize=10, generations=4` - too few generations for convergence (resembles random sampling)

**Literature Basis**:
- Storn & Price (1997): Recommend popsize = 10×n_params (scipy default)
- No explicit minimum generations, but empirically 10-50 needed for convergence
- Scipy default maxiter = 1000 (problem-dependent)

**Usage**: See Development Commands section

---

## Development History

**Recent Critical Entries** (Last 30 days):

### 2025-10-24: Phase 4D - DE Configuration Analysis & Result Utilities

**Problem**: Completed 720-eval production run showed poor convergence - only 5 improvements total, best found at iteration 273 (Gen 2) with no subsequent improvement in 447 evals. Suspected insufficient generations for DE evolution.

**Analysis**:
- Configuration: popsize=10, generations=4 (180 individuals × 4 generations)
- Generation-wise best: Gen1=1.8443, Gen2=1.7306, Gen3=1.7673, Gen4=1.7626
- Only Gen1→Gen2 showed improvement (-6.16%), subsequent generations stagnant
- 0.7% improvement rate (5/720) resembles random sampling, not optimization

**Root Cause**: DE requires multiple generations for evolution (crossover/mutation of good individuals). 4 generations insufficient - no time for population to evolve toward optimum.

**Literature Review**:
- Storn & Price (1997): No explicit minimum generations stated
- Scipy default: maxiter=1000 (problem-dependent)
- Empirical consensus: Minimum 10-20 generations for meaningful convergence

**Solution**:
1. Recommend popsize=4, generations=10 (same 720 evals, better convergence)
2. Long-term: popsize=5, generations=20+ for production runs
3. Created generate_result_from_history.py utility for result extraction
4. Fixed result filename to match history CSV (history_XXX.csv → result_XXX.json)

**Impact**: Need to re-run optimization with proper generation count. Previous result (best=1.7306) likely random luck, not true optimization.

**Files Modified**:
- run_optimization.py (result filename matching)
- dev/utils/generate_result_from_history.py (new utility)
- CLAUDE.md (DE configuration guidelines)

### 2025-10-22: Phase 4C Resume System Implementation

**Problem**: Long-running optimizations (2-3 days) vulnerable to interruptions. Unity performance degraded with 400+ files. Manual recovery complex.

**Solution**: Comprehensive resume system with 8 components:
1. Fixed filenames in Unity (current_parameters.json, current_result.json)
2. Automatic file archiving to data/input/parameters & data/output/results
3. Checkpoint save every iteration (eval_counter, generation, best_params, random_state)
4. Resume logic with --resume flag (restores exact state via np.random.set_state)
5. Generation tracking fix (use CSV column directly, not estimation)
6. Result accuracy (extract true best from history, not optimizer penalty)
7. Time estimation (separate remaining/total for resume/normal)
8. Manual recovery utilities (rebuild_history.py, create_checkpoint.py)

**Impact**: Production-ready resume capability. Can pause/continue 720-eval runs. Perfect reproducibility. Tested with 436-eval recovery.

**Files Modified**:
- run_optimization.py (resume logic, time estimation, result extraction)
- scipy_de_optimizer.py (checkpoint save, generation tracking, resume counters)
- unity_simulator.py (fixed filenames, archiving with copy not move)
- analyze_history.py (use CSV generation column, fix graph axes)
- history_tracker.py (append mode for resume)
- objective_function.py (set_eval_counter for resume)
- Calibration_hybrid_OutputManager.cs (fixed filename output)

### 2025-10-20: Critical Race Condition Fix

**Problem**: Production run failed at iteration 64/720 - Python reading 65MB JSON while Unity still writing

**Solution**: File stability check - monitors file size stability (2×0.5s) + JSON validation before reading

**Impact**: Prevents optimization crashes, +1s overhead per eval (negligible), production-ready robustness

---

**Full History**: See [DEV_HISTORY.md](DEV_HISTORY.md) for complete chronological record of all development decisions, bug fixes, and architectural changes since project start.

---

