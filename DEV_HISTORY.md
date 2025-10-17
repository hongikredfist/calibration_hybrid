# Development History

Complete chronological record of all technical decisions, bug fixes, and architectural changes for the calibration_hybrid project.

**Purpose**: Permanent archive of development journal entries. Never deleted, only appended.

**Format**: Reverse chronological (newest first)

**See also**: [CLAUDE.md](CLAUDE.md) for current status and recent entries

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
