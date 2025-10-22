# Development History

Complete chronological record of all technical decisions, bug fixes, and architectural changes for the calibration_hybrid project.

**Purpose**: Permanent archive of development journal entries. Never deleted, only appended.

**Format**: Reverse chronological (newest first)

**See also**: [CLAUDE.md](CLAUDE.md) for current status and recent entries

---

## 2025-10-22: Phase 4C - Resume System Implementation

**Context**: Production optimization runs take 2-3 days (720 evaluations). System vulnerable to interruptions (power outage, crashes, manual stops). Unity performance degraded with 400+ parameter files in Input folder (370s → 480s per simulation). Need robust resume capability for long-running optimizations.

**Problems Identified**:
1. No checkpoint/resume system - interruption means restart from scratch
2. Unity Input/Output folders accumulating 400+ files - performance degradation
3. Manual recovery complex - need to rebuild history from scattered result files
4. Generation numbers estimated incorrectly in analysis graphs (1.00, 1.02 instead of 1, 2, 3)
5. Result JSON showing wrong best_objective (1e10 penalty instead of true best)
6. Result JSON showing wrong n_evaluations (796 instead of 436)
7. Time estimation using total evaluations instead of remaining for resume
8. No tracking of which iteration/generation produced best result

**Solution - Comprehensive Resume System**:

### 1. File Archiving System
**Problem**: Unity scanning 400+ files in Input/Output folders → performance degradation
**Solution**: Use fixed filenames in Unity, archive to separate folders after use

**Files Modified**:
- `unity_simulator.py` (Lines 192-206, 249-255):
  - Changed input to `current_parameters.json` (fixed name)
  - Archive input to `data/input/parameters/{experimentId}_parameters.json` using `shutil.copy2()`
  - Changed output to `current_result.json` (fixed name)
  - Archive output to `data/output/results/{experimentId}_result.json` using `shutil.copy2()` (NOT move!)
- `Calibration_hybrid_OutputManager.cs` (Lines 343-348):
  - Changed from `$"{experimentId}_result.json"` to `"current_result.json"`

**Impact**: Unity folders only contain latest 2 files, archives preserved in data/ folders

### 2. Checkpoint Save System
**Problem**: No way to resume from interruption
**Solution**: Save checkpoint every iteration with all necessary state

**Files Modified**:
- `scipy_de_optimizer.py` (Lines 275-310):
  - Added `_save_checkpoint()` method
  - Saves: eval_counter, generation, best_params, best_objective, random_state, history_csv, algorithm metadata
  - Called every iteration after evaluation (Line 190)
  - Outputs to `data/output/checkpoint_latest.pkl`

**Checkpoint Format**:
```python
{
    'eval_counter': 436,
    'generation': 3,
    'best_params': np.array([...]),  # 18 values
    'best_objective': 1.7306,
    'random_state': np.random.get_state(),  # Full RNG state
    'history_csv': 'data/output/history_*.csv',
    'algorithm': 'ScipyDE_pop10_best1bin',
    'popsize': 10,
    'seed': 1234567890,
    'max_evaluations': 720,
    'timestamp': '2025-10-22T17:10:28.961332'
}
```

### 3. Resume Logic
**Problem**: No mechanism to load and continue from checkpoint
**Solution**: Add --resume flag with full state restoration

**Files Modified**:
- `run_optimization.py` (Lines 203-270):
  - Added `--resume` argument
  - Added `load_checkpoint()` function
  - Resume mode: load checkpoint, validate algorithm match, restore random state
  - Calculate remaining_evals = max_evaluations - eval_counter
  - Set args.seed from checkpoint for logging
- `scipy_de_optimizer.py` (Lines 78-79, 107-108, 160-161):
  - Added `resume_eval_counter` and `resume_generation` parameters to __init__
  - Initialize counters from resume values instead of 0
- `run_optimization.py` (Lines 66-95):
  - Modified `create_optimizer()` to accept checkpoint and pass resume counters
- `objective_function.py` (Lines 80-88):
  - Added `set_eval_counter()` method to restore eval count

**Random State Restoration**:
- Key insight: Seed alone insufficient for resume (can't skip 436 evaluations)
- Solution: `np.random.set_state(checkpoint['random_state'])` - restores exact RNG position
- Guarantees: Iteration 437 uses same random numbers as if running 1-437 continuously

### 4. Generation Tracking Fix
**Problem**: analyze_history.py estimated generation from iteration count, showing 1.00, 1.02, etc. on graphs
**Solution**: Use generation column directly from CSV

**Files Modified**:
- `analyze_history.py` (Lines 76-109):
  - Read `generations = [int(row['generation']) for row in rows]`
  - Use `unique_generations = sorted(set(generations))`
  - Group by actual generation values, not estimated ranges
- `analyze_history.py` (Lines 153-172):
  - Plot using CSV generation column
  - Added `plt.xticks(gen_nums)` for integer-only x-axis labels
  - Added `'o-'` for connected line plot

**Impact**: Graphs now show Generation 1, 2, 3 (not 1.00, 1.02) with proper lines connecting points

### 5. Result Accuracy Fix
**Problem**: Optimizer returns 1e10 penalty when hitting eval limit, not true best
**Solution**: Extract true best from history CSV when saving results

**Files Modified**:
- `run_optimization.py` (Lines 105-166):
  - Modified `save_results()` to accept `history_csv` parameter
  - If history exists, read all rows and find min objective
  - Override optimizer result with true best from history
  - Add `best_iteration`, `best_generation` fields
  - Add `best_metrics` with RMSE, P95, TimeGrowth, DensityDiff
- `run_optimization.py` (Line 425):
  - Pass `history_csv=history_path` to `save_results()`
- `run_optimization.py` (Lines 427-430):
  - Extract corrected best_params from saved result file

**New Result JSON Format**:
```json
{
  "best_objective": 1.7306,
  "best_iteration": 274,
  "best_generation": 2,
  "n_evaluations": 436,
  "best_metrics": {
    "mean_error": 1.9330,
    "percentile_95": 3.7289,
    "time_growth": 0.1043,
    "density_diff": 0.0476
  },
  ...
}
```

### 6. Time Estimation Fix
**Problem**: Resume showing 84 hours (720 evals) instead of 33 hours (284 remaining)
**Solution**: Use remaining_evals for time estimate, different messages for resume/normal

**Files Modified**:
- `run_optimization.py` (Lines 326-327):
  - Added `remaining_evals = max_evaluations` for normal mode
- `run_optimization.py` (Lines 355-364):
  - Changed `estimated_time = remaining_evals * 7 / 60`
  - Resume: "Estimated remaining time: 33.1 hours (1.4 days)"
  - Normal: "Estimated total time: 84.0 hours (3.5 days)"

### 7. Manual Recovery Utilities
**Problem**: Need to recover from manual file moves or interrupted checkpoint saves
**Solution**: Create utilities to rebuild history and checkpoint from result files

**Files Created**:
- `dev/utils/rebuild_history.py`:
  - Scans `data/output/results/eval_*_result.json`
  - Reconstructs history CSV with all iterations
  - Calculates generation from iteration (popsize × 18)
- `dev/utils/create_checkpoint.py`:
  - Reads history CSV
  - Finds best evaluation (min objective)
  - Creates checkpoint_latest.pkl from last iteration
  - Includes generation from CSV

**Usage**:
```bash
python dev/utils/rebuild_history.py      # Rebuild from result files
python dev/utils/create_checkpoint.py    # Create checkpoint from history
```

### 8. History Append Mode
**Problem**: Resume creates new history file instead of continuing existing one
**Solution**: Add append mode to OptimizationHistory

**Files Modified**:
- `history_tracker.py` (Lines 32-54, 56-96):
  - Added `append` and `start_iteration` parameters to __init__
  - If append=True, skip header write
  - Adjust iteration numbers: `actual_iteration = start_iteration + iteration`
- `run_optimization.py` (Lines 335-343):
  - Resume: `OptimizationHistory(history_path, append=True, start_iteration=0)`
  - Note: start_iteration=0 because eval_counter already correct

**Testing**:
- Ran optimization to iteration 436
- Generated history: `history_ScipyDE_best1bin_20251020_134139.csv`
- Used sed to fix generation 424-436: `sed -i 's/^424,1,/424,3,/' ...`
- Created checkpoint with `create_checkpoint.py`
- Resume successfully continued from 437

**Production Run Status**:
- Completed: 436/720 (61%)
- Best objective: 1.7306 (38% improvement over baseline 2.8071)
- Remaining: 284 evals (~33 hours, 1.4 days)
- Ready to resume with: `python dev/run_optimization.py --algorithm scipy_de --resume`

**Impact**:
- ✅ Can pause/resume 720-eval runs without data loss
- ✅ Perfect reproducibility via random state restoration
- ✅ Unity performance maintained (2 files instead of 400+)
- ✅ Accurate result reporting (true best, not penalty)
- ✅ Clear progress tracking (iteration, generation, metrics)
- ✅ Manual recovery possible from result files
- ✅ Production-ready for long-running optimizations

**Files Modified Summary**:
1. `run_optimization.py` - Resume logic, time estimation, result extraction from history
2. `scipy_de_optimizer.py` - Checkpoint save, generation tracking, resume counters
3. `unity_simulator.py` - Fixed filenames, file archiving with copy
4. `analyze_history.py` - Generation tracking from CSV, graph fixes
5. `history_tracker.py` - Append mode for resume
6. `objective_function.py` - set_eval_counter for resume
7. `Calibration_hybrid_OutputManager.cs` - Fixed filename output
8. `dev/utils/rebuild_history.py` - NEW
9. `dev/utils/create_checkpoint.py` - NEW

---

## 2025-10-20: Critical Race Condition Fix - JSON Parsing Error

**Context**: Production optimization run failed at iteration 64/720 with JSON parsing error

**Problem**:
- Optimization failed with `JSONDecodeError: Expecting ',' delimiter: line 1319636 column 37 (char 47697920)`
- File `eval_0064_result.json` was 65MB (very large due to 5008 agents + density data)
- Python was reading file while Unity was still writing it (race condition)
- File existed but was incomplete (47MB/65MB written when Python tried to read)

**Root Cause**:
```python
# unity_simulator.py:312 (BEFORE)
if self.result_file.exists():
    return  # Immediate return without checking if file write is complete
```

**Technical Details**:
- Unity writes 65MB JSON in ~1-2 seconds
- Python checks `exists()` every 2 seconds
- If check happens during write → file exists but incomplete
- JSON parser reads truncated data → `JSONDecodeError`

**Solution - File Stability Check**:
1. Added `import json` for validation
2. Implemented `_is_file_stable()` method with 2-stage verification:
   - **Stage 1**: File size stability (2 checks, 0.5s interval)
   - **Stage 2**: JSON validity (parse attempt)
3. Modified `_wait_for_result()` to check stability before returning

**Implementation**:
```python
def _is_file_stable(self, file_path, stability_checks=2, check_interval=0.5):
    """Check if file is stable by monitoring size and validating JSON."""
    prev_size = file_path.stat().st_size

    # Check file size stability (2 consecutive checks)
    for _ in range(stability_checks):
        time.sleep(check_interval)
        current_size = file_path.stat().st_size

        if current_size != prev_size:
            return False  # Still growing

        prev_size = current_size

    # Validate JSON integrity
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True  # Complete and valid
    except json.JSONDecodeError:
        return False  # Corrupted or incomplete
```

**Why 65MB Files?**:
- 5008 agents × ~100 timepoints × ~100 bytes/timepoint = ~50MB (trajectory data)
- 40×40 density grid × timepoints × 2 layers = ~15MB (density snapshots)
- Total: 65MB per simulation result

**Files Modified**:
- `dev/core/unity_simulator.py`:
  - Added `import json` (line 27)
  - Modified `_wait_for_result()` to call stability check (line 314)
  - Added `_is_file_stable()` method (line 351-392)

**Impact**:
- ✅ Prevents race condition crashes in production runs
- ✅ Zero data loss (waits for complete file)
- ✅ Robust JSON validation before parsing
- ⏱️ Minor overhead: +1 second per evaluation (720 evals → +12 min total, negligible)

**Testing Status**: Fix implemented, awaiting production run validation

**Related Issue**: Discovered during 720-eval production run preparation (iteration 64/720 crashed)

---

## 2025-10-17: Grid Resolution Optimization Decision

**Context**: Before 720-eval production run, user questioned if 10×10 grid was appropriate for density analysis

**Problem**:
- Initial density metric used 10×10 spatial grid
- Cell size: 10m × 10m = 100m² per cell
- Too coarse for detecting local crowd variations
- Literature standard: 2-5m cells for pedestrian density analysis
- 100m² cell can hold ~100 pedestrians (no local detail)

**Solution - Upgrade to 40×40 Grid**:
- Cell size: 2.5m × 2.5m = 6.25m² per cell
- Expected 3-13 pedestrians per cell (excellent spatial resolution)
- Aligns with pedestrian simulation literature standards
- 1,600 cells total (16x increase, still computationally light)

**Changes Made**:
- Modified `Calibration_hybrid_DensityAnalyzer.cs`: `gridResolutionX/Z = 40` (was 10)
- Updated CLAUDE.md and README.md to reflect 40×40 grid
- Note: Requires Unity Scene component verification

**Impact**:
- ✅ Optimal spatial resolution for local crowd behavior
- ✅ Literature-compliant density analysis
- ⚠️ Baseline remeasurement required (density values will change)
- ⚠️ Unity Scene needs DensityAnalyzer component update verification

**Rationale**: 2.5m cell size is sweet spot:
- Too small (<1m): Noisy, mostly empty cells
- Too large (>5m): Misses local crowd dynamics
- 2.5m: Captures pedestrian personal space (~1-2m diameter)

---

## 2025-10-17: Phase 4B+ Objective Function Enhancements

**Context**: Before 720-eval production run, identified need for improved objective function and additional metrics

**Problem**:
- Only 3 metrics (MAE, P95, TimeGrowth) - missing macroscopic validation
- MAE less sensitive to large errors than RMSE (literature uses RMSE)
- TimeGrowth using simple first/last 25% comparison (ignores middle trajectory)
- No generation tracking in CSV (had to infer from iteration count)
- No density validation (only individual trajectory errors)
- Convergence plot bug: generation size calculation always returned 1

**Solution - 8 Major Enhancements**:

### 1. Density Metric Addition (2 hours)
- Created `Calibration_hybrid_DensityAnalyzer.cs` (Unity)
- 40×40 spatial grid tracking (empirical vs SFM agent counts)
- Cell size: 2.5m × 2.5m = 6.25m² per cell
- RMSE calculation across grid cells over time
- Added to objective function with 20% weight

**Implementation**:
```csharp
public class DensityAnalyzer : MonoBehaviour
{
    public int gridResolutionX = 40;
    public int gridResolutionZ = 40;

    public struct DensitySnapshot
    {
        public int timeIndex;
        public float[,] empiricalDensity;
        public float[,] sfmDensity;
        public float rmse;
    }
}
```

### 2. MAE → RMSE Conversion (20 minutes)
- Changed mean_error calculation: `sqrt(mean([agent_mean_error²]))`
- More sensitive to large errors (literature standard)
- Aligns with pedestrian simulation research standards

### 3. TimeGrowthPenalty Improvement (30 minutes)
- Changed from first/last 25% comparison to `scipy.stats.linregress`
- Analyzes full trajectory slope (error vs time)
- Only penalizes positive slopes (growing errors)
- More accurate temporal stability measurement

**Before**:
```python
growth_penalty = (last_25_avg - first_25_avg) / first_25_avg
```

**After**:
```python
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(time_indices, error_values)
growth_penalty = max(0.0, slope)  # Only penalize positive slopes
```

### 4. Generation Column Addition (30 minutes)
- Added generation tracking to `scipy_de_optimizer.py`
- Calculation: `generation = (iteration-1) // (popsize × 18) + 1`
- CSV now includes generation column for accurate convergence analysis

### 5. Enhanced History Tracking (15 minutes)
- CSV columns expanded: `iteration, generation, timestamp, objective, mean_error, percentile_95, time_growth, density_diff, [18 params]`
- Full transparency of all metrics per evaluation
- Modified `history_tracker.py` and `objective_function.py`

### 6. Seed Reproduction Commands (10 minutes)
- Auto-print reproduction command at completion
- Format: `python dev/run_optimization.py --algorithm scipy_de --popsize X --generations Y --seed Z`
- Full experiment reproducibility

### 7. Auto-detect Latest Result (15 minutes)
- `evaluate_objective.py` now finds newest `*_result.json` automatically
- No need to specify file path for baseline remeasurement
```python
def find_latest_result_file(directory):
    result_files = glob.glob(os.path.join(directory, "*_result.json"))
    return max(result_files, key=os.path.getmtime)
```

### 8. Graph Bug Fix - Generation Size Calculation (30 minutes)
- **Problem**: Convergence plot showed 108 points in both graphs (should be 3 generations in right graph)
- **Cause**: `generation_size = len([i for i in iterations if i == 1])` always returned 1
- **Fix**: Calculate from `total_evals % common_pop_sizes`

**Before**:
```python
generation_size = len([i for i in iterations if i == 1])  # Always 1
```

**After**:
```python
possible_gen_sizes = [36, 54, 90, 126, 144, 180, 216, 270]  # popsize 2,3,5,7,8,10,12,15
for size in possible_gen_sizes:
    if total_evals % size == 0:
        generation_size = size
        break
```

**New Objective Function**:
```python
# Before (Phase 4B)
Objective = 0.50 × MAE + 0.30 × P95 + 0.20 × TimeGrowth

# After (Phase 4B+)
Objective = 0.40 × RMSE + 0.25 × P95 + 0.15 × TimeGrowth + 0.20 × Density
```

**Baseline Change**:
- Old (MAE-based): 4.5932
- New (RMSE-based): **2.8254** (with 10×10 grid)
- Note: Baseline remeasurement needed after 40×40 grid update
- Reflects all improvements (RMSE, better TimeGrowth calc, density metric)

**Files Modified**:
- Unity: `Calibration_hybrid_DensityAnalyzer.cs` (NEW, updated to 40×40 grid)
- Unity: `Calibration_hybrid_OutputManager.cs` (density collection)
- Python: `dev/evaluate_objective.py` (RMSE, density, TimeGrowth, auto-detect)
- Python: `dev/core/objective_function.py` (generation passing, metrics)
- Python: `dev/core/history_tracker.py` (generation column, individual metrics)
- Python: `dev/optimizer/scipy_de_optimizer.py` (generation tracking)
- Python: `dev/run_optimization.py` (reproduction command output)
- Python: `dev/analysis/analyze_history.py` (generation size calculation fix)

**Impact**:
- ✅ Macroscopic validation added (density metric) - critical for SCI papers
- ✅ Literature-standard RMSE metric
- ✅ More accurate temporal stability measurement (linear regression)
- ✅ Full metric transparency in CSV
- ✅ Perfect reproducibility with seed commands
- ✅ Optimal spatial resolution (40×40 grid, 2.5m cells)
- ✅ Baseline accurately reflects all improvements (2.8254 with 10×10 grid)
- ⚠️ Baseline remeasurement required before production run (40×40 grid update)

---

## 2025-10-16: CLI Refactoring and Seed Reproducibility

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

**Implementation**:
```python
# run_optimization.py
parser.add_argument('--generations', type=int, default=4,
                    help='Number of generations (default: 4)')
parser.add_argument('--seed', type=int, default=None,
                    help='Random seed (default: None = auto-generate)')

# Auto-calculate max_evals
if args.max_evals is None:
    args.max_evals = args.popsize * n_params * args.generations

# Auto-generate seed
if args.seed is None:
    args.seed = random.randint(0, 2**31 - 1)

# Print reproduction command
print(f"python dev/run_optimization.py --algorithm scipy_de --popsize {args.popsize} --generations {args.generations} --seed {result.seed}")
```

**Impact**:
- ✅ Intuitive interface: Users think in DE concepts (10 individuals, 4 generations)
- ✅ No mental math required for evaluation count
- ✅ Seed diversity by default (auto-generated each run)
- ✅ Full reproducibility: seed saved in result JSON and printed in console
- ✅ Backward compatible: old `--max-evals` style still works

---

## 2025-10-16: Phase 4B Refinements and Code Cleanup

**Context**: After initial Phase 4B implementation and testing, several issues and improvements identified

**Issues Fixed**:
1. **File Trigger System** - Replaced subprocess mode with file trigger to avoid "Multiple instances" error
2. **Unity .meta File Warning** - Added code to delete both .json and .meta files
3. **Off-by-one Error** - 11th evaluation started when max-evals=10. Fixed by checking limit BEFORE evaluation
4. **Simulation Not Stopping** - Optimization continued past limit. Fixed with proper early stopping
5. **Input-Output Mismatch** - simulation_result.json (fixed name) vs eval_xxxx_parameters.json (unique). Implemented 1:1 matching

**Features Added**:

### 1. File Trigger System (default mode)
- Python writes `trigger_simulation.txt`
- Unity polls for trigger file via `[InitializeOnLoad]` static constructor
- Unity detects → deletes trigger → runs simulation
- Advantage: Unity Editor stays open (no 30s startup overhead)

**Implementation**:
```csharp
[InitializeOnLoad]
public class Calibration_hybrid_AutomationController
{
    private static string triggerFilePath = "path/to/trigger_simulation.txt";

    static Calibration_hybrid_AutomationController()
    {
        EditorApplication.update += CheckForTriggerFile;
    }

    private static void CheckForTriggerFile()
    {
        if (File.Exists(triggerFilePath))
        {
            File.Delete(triggerFilePath);
            RunSimulation();
        }
    }
}
```

### 2. Input-Output 1:1 Matching
- Modified `OutputManager.cs` to use experimentId from InputManager
- Dynamic filenames: `eval_0001_parameters.json` ↔ `eval_0001_result.json`
- Complete traceability for each evaluation

**Before**:
```csharp
// Always "simulation_result.json"
string outputPath = "StreamingAssets/Calibration/Output/simulation_result.json";
```

**After**:
```csharp
// Use experimentId from InputManager
string experimentId = InputManager.instance.GetExperimentId();
string outputPath = $"StreamingAssets/Calibration/Output/{experimentId}_result.json";
```

### 3. Unique History Files
- Format: `optimization_history_ScipyDE_pop5_best1bin_20251016_163602.csv`
- Includes algorithm name and timestamp
- Allows comparing different experiments without overwriting

### 4. Automatic Analysis
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

---

## 2025-10-15: Phase 4B Decision and Implementation

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

### 1. BaseOptimizer Abstract Class
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class OptimizerResult:
    best_params: np.ndarray
    best_objective: float
    history: List[tuple]
    metadata: dict

class BaseOptimizer(ABC):
    @abstractmethod
    def optimize(self, objective_function, bounds) -> OptimizerResult:
        pass
```

### 2. UnitySimulator
- Encapsulates Editor automation (subprocess, polling, timeout)
- File trigger system for zero startup overhead
- Input-Output 1:1 matching

### 3. ObjectiveFunction
- Wraps Unity execution + evaluation in callable
- Tracks history automatically
- Handles metrics computation

### 4. ScipyDEOptimizer
- Wraps existing DE logic from Phase 3
- Implements BaseOptimizer interface
- Callback-based early stopping

### 5. AutomationController (Unity)
- Unity Editor MenuItem for testing
- File trigger polling system
- Auto-stop Play mode

### 6. TESTING.md
- Comprehensive 5-step test guide
- Step 1: Environment setup
- Step 2: Baseline evaluation
- Step 3: Unity automation test
- Step 4: Quick optimization (36 evals)
- Step 5: Analysis verification

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

**Design Pattern**: Strategy Pattern
- Context: `run_optimization.py`
- Strategy Interface: `BaseOptimizer`
- Concrete Strategies: `ScipyDEOptimizer`, (future: BayesianOptimizer, CMAESOptimizer)
- Client: Unified CLI with `--algorithm` parameter

**Extensibility Example**:
```python
# Future algorithm addition (1-2 hours)
class BayesianOptimizer(BaseOptimizer):
    def optimize(self, objective_function, bounds) -> OptimizerResult:
        # Use same objective_function, just different algorithm
        pass

# Usage (no other code changes needed)
python dev/run_optimization.py --algorithm bayesian
```
