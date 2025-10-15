# Phase 4B Testing Guide

**Purpose**: Test the automated parameter calibration system

**Total Time**: 2-3 hours (mostly Unity simulation time)

---

## Prerequisites

- [  ] Unity project: `D:\UnityProjects\META_VERYOLD_P01_s\`
- [  ] `Calibration_hybrid_AutomationController.cs` exists in Unity project (already created)
- [  ] Python environment activated: `.venv\Scripts\activate`
- [  ] Working directory: `c:\dev\calibration_hybrid`

---

## Quick Start (5 Steps)

### Step 1: Verify Unity Scene (2 min)

**IMPORTANT**: Use **Calibration_Hybrid.unity** scene (Phase 3+ system), NOT "Calibration.unity" (old system)

**In Unity Editor**:
1. Verify `AutomationController.cs` has correct scene path:
   ```
   D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\Calibration_hybrid_AutomationController.cs
   ```
2. Check line 22:
   ```csharp
   private const string CALIBRATION_SCENE_PATH = "Assets/VeryOld_P01_s/Scene/PedModel/Calibration_Hybrid.unity";
   ```
3. If path is different, find your scene:
   - Project window → Search "Calibration_Hybrid"
   - Right-click scene → Copy Path
   - Update line 22
4. Save, wait for Unity to recompile

**Why**:
- `Calibration_Hybrid.unity` uses Phase 3 system (`Calibration_hybrid_*` scripts) ✅
- `Calibration.unity` uses old system (`Calibration_ParameterInterface`) ❌ Wrong!

---

### Step 2: Test Unity Automation (10 min)

**In Unity Editor**:
1. Menu → **Automation → Test - Run Simulation (Manual)**
2. **If Unity exits**: Check Unity Console for error before it closes
   - If error shows "Scene not found" or wrong scene loaded
   - Verify Step 1: scene path should be `Calibration_Hybrid.unity`
   - Update `CALIBRATION_SCENE_PATH` in AutomationController.cs (line 22)
   - Retry this step
3. Verify Play mode starts automatically
4. Verify scene loaded: **Calibration_Hybrid** (check top of Unity window)
5. Wait for simulation (~5-10 min)
6. Verify Play mode stops automatically
7. Check file: `Assets/StreamingAssets/Calibration/Output/simulation_result.json`

**Expected**: ✅ Unity automation works (Calibration_Hybrid scene loads, Play mode starts and stops automatically)

---

### Step 3: Test Python → Unity (10 min)

```powershell
cd c:\dev\calibration_hybrid
.venv\Scripts\activate
python dev/core/unity_simulator.py
```

**Expected**: Unity launches, simulation runs, prints "SUCCESS!"

---

### Step 4: Test Objective Function (10 min)

```powershell
python dev/core/objective_function.py
```

**Expected**: Objective ~4.59 (baseline), prints "SUCCESS!"

---

### Step 5: Test End-to-End (1-2 hours)

```powershell
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5 --seed 42
```

**Prompt**:
```
Continue? [y/N]: y  <-- Type 'y' and Enter
```

**Expected**: 10 Unity simulations run automatically, 3 files created in `data/output/`:
- `optimization_history.csv` (11 lines: header + 10 rows)
- `best_parameters.json`
- `result_ScipyDE_pop5_best1bin_TIMESTAMP.json`

---

## Success Criteria

- [  ] Step 2: Unity menu automation works
- [  ] Step 3: Python launches Unity successfully
- [  ] Step 4: Objective ~4.59
- [  ] Step 5: 10 evaluations complete

**All pass** → Phase 4B works! ✅

---

## Detailed Test Suite

### Test 1: Unity Command Line Execution

**Purpose**: Verify `-executeMethod` works from command line

**Find Unity Path**:
```powershell
Get-ChildItem "C:\Program Files\Unity" -Recurse -Filter "Unity.exe" | Select-Object FullName
```

**Run Unity**:
```powershell
$unityPath = "C:\Program Files\Unity\Hub\Editor\2021.3.X\Editor\Unity.exe"
$projectPath = "D:\UnityProjects\META_VERYOLD_P01_s"

& $unityPath `
  -projectPath $projectPath `
  -executeMethod Calibration_hybrid_AutomationController.RunCalibrationSimulation `
  -logFile "dev\unity_test.log"
```

**Expected**: Unity opens, loads scene, enters Play mode, simulation runs, auto-stops

**Check Log**:
```powershell
Get-Content dev\unity_test.log -Tail 30
```

Should contain:
```
[AutomationController] Starting automated calibration simulation
[AutomationController] Scene loaded successfully
[AutomationController] Entering Play mode...
[Validation] Simulation Complete
[OutputManager] Auto-stopping Play mode
```

---

### Test 2: Parameter Utilities

**Test in Python**:
```python
cd c:\dev\calibration_hybrid
.venv\Scripts\activate
python
```

```python
from dev.core.parameter_utils import *
import numpy as np

# Test bounds
bounds = load_parameter_bounds()
assert len(bounds) == 18
print(f"✓ Loaded {len(bounds)} bounds")

# Test conversion
params = np.array([0.2, 0.5, 1.2, 5.0, 0.35, 1.0, 5.0, 0.35, 8.0, 5.0, 3.0, 0.0, 2.5, 150.0, 240.0, 5.0, 30.0, 0.7])
params_dict = params_array_to_dict(params)
assert params_dict['minimalDistance'] == 0.2
print(f"✓ Array to dict works")

params_back = params_dict_to_array(params_dict)
assert np.allclose(params, params_back)
print(f"✓ Dict to array works")

# Test clamping
invalid = params.copy()
invalid[0] = 0.1  # Too low (min=0.15)
clamped = validate_and_clamp_params(invalid)
assert clamped[0] == 0.15
print(f"✓ Validation works")

print("\n✅ All tests passed!")
```

---

### Test 3: Scipy DE Optimizer (Simple Function)

**Test without Unity** (fast):
```powershell
python dev/optimizer/scipy_de_optimizer.py
```

**What it does**: Minimizes f(x) = sum(x²), should find x ≈ [0,0,0,0,0]

**Expected Output**:
```
SCIPY DE OPTIMIZER TEST (Quadratic Function)
...
Best Objective:  0.00XXXX
Best Params:     [~0, ~0, ~0, ~0, ~0]
[TEST] SUCCESS! Found minimum close to zero.
```

**Duration**: < 1 second

---

### Test 4: Full Optimization (Production Test)

**After all tests pass**, run longer optimization:

```powershell
# 50 evaluations (~6 hours)
python dev/run_optimization.py --algorithm scipy_de --max-evals 50 --popsize 10 --seed 42

# 750 evaluations (~3-4 days)
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42
```

**Monitor**:
```powershell
# Check history file grows
Get-Content data/output/optimization_history.csv | Measure-Object -Line

# Check best objective
Get-Content data/output/best_parameters.json | ConvertFrom-Json | Select-Object -First 3
```

---

## Troubleshooting

### Issue: Unity exits when running Test menu

**Symptom**: Click "Automation → Test - Run Simulation (Manual)", Unity immediately closes

**Cause**: Scene path incorrect or wrong scene name in AutomationController.cs

**Solution**:
1. Before Unity closes, quickly check Console for error log:
   - Look for: `[AutomationController] Available scenes (X):`
   - This lists all scene paths in your project
2. Find **Calibration_Hybrid.unity** path (NOT Calibration.unity)
3. Open `AutomationController.cs`:
   ```
   D:\UnityProjects\META_VERYOLD_P01_s\Assets\VeryOld_P01_s\Dev\Calibration_hybrid\Calibration_hybrid_AutomationController.cs
   ```
4. Update line 22:
   ```csharp
   private const string CALIBRATION_SCENE_PATH = "Assets/VeryOld_P01_s/Scene/PedModel/Calibration_Hybrid.unity";
   ```
5. Save, wait for recompile, retry Step 2

**Important**: AutomationController searches for "Calibration_Hybrid" FIRST, then falls back to "Calibration". Make sure Calibration_Hybrid.unity exists in your project.

---

### Issue: Wrong scene loads (Calibration_ParameterInterface errors)

**Symptom**:
- Simulation starts but shows errors: `[ParameterInterface] Instance CalibrationManager - Specific file not found`
- Scene name shows "Calibration" instead of "Calibration_Hybrid"

**Cause**: AutomationController loaded wrong scene (old system instead of Phase 3 system)

**Solution**: Same as "Unity exits" issue above - update scene path to Calibration_Hybrid.unity

---

### Issue: "Unity Editor not found"

**Solution 1 - Set environment variable**:
```powershell
$unityPath = "C:\Program Files\Unity\Hub\Editor\2021.3.XXf1\Editor\Unity.exe"
[Environment]::SetEnvironmentVariable("UNITY_EDITOR_PATH", $unityPath, "User")
```

**Solution 2 - Provide via CLI**:
```powershell
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --unity-path "C:\...\Unity.exe"
```

---

### Issue: "Module not found"

**Symptom**: `ModuleNotFoundError: No module named 'export_to_unity'`

**Solution**:
```powershell
cd c:\dev\calibration_hybrid  # Ensure correct directory
.venv\Scripts\activate        # Activate virtual environment
python -c "import sys; print(sys.path)"  # Verify dev/ is in path
```

---

### Issue: Unity timeout

**Symptom**: `TimeoutError: Simulation timeout after 600s`

**Solutions**:

1. **Increase timeout**:
   ```powershell
   python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --timeout 1200  # 20 min
   ```

2. **Check Unity is running**:
   - Look for Unity window
   - Check Task Manager for Unity.exe

3. **Verify auto-stop enabled**:
   - Open Calibration scene
   - Select OutputManager GameObject
   - Inspector: Check "Auto Stop Play Mode"

---

### Issue: Objective values inconsistent

**Symptom**: Different runs with same seed give different results (variation > 0.1)

**Check**:
```powershell
# Run baseline test multiple times
python dev/core/objective_function.py
# Objective should be ~4.59 ± 0.01
```

**If variation > 0.1**: Unity simulation may not be fully deterministic

---

## Command Reference

```powershell
# Environment
cd c:\dev\calibration_hybrid
.venv\Scripts\activate

# Quick tests (no Unity)
python dev/optimizer/scipy_de_optimizer.py                    # 1 sec
python -m pytest dev/core/parameter_utils.py                  # If pytest installed

# Unity tests (5-10 min each)
python dev/core/unity_simulator.py                            # Single simulation
python dev/core/objective_function.py                         # Simulation + evaluation

# Optimization (specify duration)
python dev/run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5    # ~1 hour
python dev/run_optimization.py --algorithm scipy_de --max-evals 50 --popsize 10   # ~6 hours
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15  # ~3 days

# Check results
ls data/output/
Get-Content data/output/optimization_history.csv
Get-Content data/output/best_parameters.json | ConvertFrom-Json
```

---

## After Testing

### Production Run

```powershell
python dev/run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42
```

**Duration**: 3-4 days
**Can run unattended**: Yes (after initial confirmation)
**Output**:
- 750 rows in `optimization_history.csv`
- Best parameters in `best_parameters.json`
- Full result in `result_ScipyDE_*.json`

### Monitor Progress

```powershell
# Check latest evaluation
Get-Content data/output/optimization_history.csv -Tail 1

# Count completed evaluations
(Get-Content data/output/optimization_history.csv | Measure-Object -Line).Lines - 1

# Check best objective so far
Get-Content data/output/best_parameters.json | ConvertFrom-Json | Select-Object -First 3
```

### Analyze Results

Use Phase 3 analysis tools:
```powershell
python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv
```

Generates:
- Convergence plot (`optimization_history.png`)
- Summary statistics
- Best objective per generation

---

## Notes

- **Unity Editor window**: Will be visible during simulations (not completely headless)
- **PC usage**: Can use PC for other tasks between simulations, but don't close Unity
- **Interruption**: Ctrl+C to stop optimization, partial results saved in history CSV
- **Resume**: Not implemented yet (restart from beginning if interrupted)

---

## Need Help?

1. **Check CLAUDE.md**: Architecture and design decisions
2. **Check log files**: `unity_log.txt` or terminal output
3. **Test components individually**: Run Tests 1-4 separately to isolate issues
4. **Verify file locations**:
   - Unity project: `D:\UnityProjects\META_VERYOLD_P01_s\`
   - Python code: `c:\dev\calibration_hybrid\dev\`
   - Results: `c:\dev\calibration_hybrid\data\output\`
