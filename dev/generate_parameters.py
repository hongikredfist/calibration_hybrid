import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import csv
from scipy.optimize import differential_evolution

# Import from other dev scripts
import sys
sys.path.append(str(Path(__file__).parent))
from export_to_unity import (
    export_to_unity_json,
    generate_experiment_id,
    PARAMETER_BOUNDS,
    PARAMETER_NAMES
)
from evaluate_objective import load_simulation_result, evaluate_objective

DEFAULT_UNITY_OUTPUT = r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\simulation_result.json"

# Baseline parameters (current Unity defaults from simulation_result.json)
BASELINE_PARAMETERS = {
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
    "visibleFactor": 0.7
}

class OptimizationHistory:
    """Track optimization history and save to CSV."""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.history = []

        # Create CSV file with header
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['iteration', 'timestamp', 'objective'] + PARAMETER_NAMES
            writer.writerow(header)

    def add_evaluation(self, iteration: int, objective: float, params: np.ndarray):
        """Add evaluation result to history."""
        timestamp = datetime.now().isoformat()
        entry = {
            'iteration': iteration,
            'timestamp': timestamp,
            'objective': objective,
            'params': params.tolist()
        }
        self.history.append(entry)

        # Append to CSV
        with open(self.output_path, 'a', newline='') as f:
            writer = csv.writer(f)
            row = [iteration, timestamp, objective] + params.tolist()
            writer.writerow(row)

    def get_best(self) -> Dict[str, Any]:
        """Get best evaluation so far."""
        if not self.history:
            return None

        best = min(self.history, key=lambda x: x['objective'])
        return best

def load_parameter_bounds() -> List[Tuple[float, float]]:
    """
    Load 18 parameter bounds for optimization.

    Returns:
        List of (min, max) tuples for each parameter
    """
    bounds = [PARAMETER_BOUNDS[name] for name in PARAMETER_NAMES]
    return bounds

def params_array_to_dict(params: np.ndarray) -> Dict[str, float]:
    """
    Convert numpy array to parameter dictionary.

    Args:
        params: Array of 18 parameter values

    Returns:
        Dictionary mapping parameter names to values
    """
    return {name: float(params[i]) for i, name in enumerate(PARAMETER_NAMES)}

def params_dict_to_array(params: Dict[str, float]) -> np.ndarray:
    """
    Convert parameter dictionary to numpy array.

    Args:
        params: Dictionary mapping parameter names to values

    Returns:
        Array of 18 parameter values
    """
    return np.array([params[name] for name in PARAMETER_NAMES])

def create_baseline_parameters(output_path: str = None) -> str:
    """
    Create baseline parameter JSON file.

    Args:
        output_path: Output file path (optional)

    Returns:
        Path to created file
    """
    if output_path is None:
        output_path = "data/input/baseline_parameters.json"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(BASELINE_PARAMETERS, f, indent=2)

    return str(output_path)

def objective_function_manual(
    params: np.ndarray,
    history: OptimizationHistory,
    iteration: int,
    unity_output_path: str
) -> float:
    """
    Objective function for manual optimization mode.

    This function:
    1. Exports parameters to Unity JSON
    2. Waits for user to run Unity simulation
    3. Loads simulation result
    4. Evaluates objective

    Args:
        params: Parameter array (18 values)
        history: Optimization history tracker
        iteration: Current iteration number
        unity_output_path: Path to Unity simulation result

    Returns:
        Objective value (lower is better)
    """
    # Convert params to dict
    param_dict = params_array_to_dict(params)

    # Generate experiment ID
    exp_id = generate_experiment_id(prefix=f"opt_iter{iteration}")

    # Export to Unity JSON
    unity_input_dir = Path(r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Input")
    unity_input_path = unity_input_dir / f"{exp_id}_parameters.json"

    print("\n" + "=" * 80)
    print(f"ITERATION {iteration} - PARAMETER EXPORT")
    print("=" * 80)

    export_to_unity_json(
        params=param_dict,
        output_path=str(unity_input_path),
        experiment_id=exp_id
    )

    print(f"Parameters exported: {unity_input_path}")
    print()
    print("MANUAL STEP REQUIRED:")
    print("1. Run Unity simulation with this parameter file")
    print("2. Wait for simulation to complete")
    print(f"3. Check output: {unity_output_path}")
    print()

    # Wait for user confirmation
    input("Press ENTER after Unity simulation completes...")

    # Load simulation result
    print("\nLoading simulation result...")
    result_data = load_simulation_result(unity_output_path)

    # Evaluate objective
    objective, metrics = evaluate_objective(result_data)

    print("\n" + "=" * 80)
    print(f"ITERATION {iteration} - OBJECTIVE EVALUATION")
    print("=" * 80)
    print(f"Objective:      {objective:.4f}")
    print(f"MeanError:      {metrics['mean_error']:.4f}")
    print(f"Percentile95:   {metrics['percentile_95']:.4f}")
    print(f"TimeGrowth:     {metrics['time_growth']:.4f}")
    print("=" * 80)

    # Save to history
    history.add_evaluation(iteration, objective, params)

    return objective

def run_optimization_manual(
    maxiter: int,
    popsize: int,
    seed: int,
    history_path: str,
    unity_output_path: str
):
    """
    Run Differential Evolution optimization in manual mode.

    In manual mode:
    - DE generates parameter sets
    - User manually runs Unity for each evaluation
    - DE updates based on results

    Args:
        maxiter: Maximum generations (total evaluations = maxiter * popsize)
        popsize: Population size
        seed: Random seed
        history_path: Path to save optimization history
        unity_output_path: Path to Unity simulation result
    """
    # Calculate total evaluations limit
    max_evaluations = maxiter * popsize

    print("=" * 80)
    print("DIFFERENTIAL EVOLUTION OPTIMIZATION - MANUAL MODE")
    print("=" * 80)
    print(f"Algorithm:       Differential Evolution (scipy)")
    print(f"Parameters:      18 (SFM model)")
    print(f"Population:      {popsize}")
    print(f"Generations:     {maxiter}")
    print(f"Max Evaluations: {max_evaluations} Unity simulations")
    print(f"Random Seed:     {seed}")
    print()
    print("Manual mode: You will run Unity simulation for each evaluation")
    print("=" * 80)
    print()

    # Load parameter bounds
    bounds = load_parameter_bounds()

    # Create history tracker
    history = OptimizationHistory(history_path)

    # Counter for evaluations (with hard limit)
    evaluation_counter = [0]
    termination_flag = [False]

    # Define objective function wrapper
    def objective_wrapper(params):
        evaluation_counter[0] += 1
        current_eval = evaluation_counter[0]

        return objective_function_manual(
            params=params,
            history=history,
            iteration=current_eval,
            unity_output_path=unity_output_path
        )

    # Callback to check evaluation limit
    def callback(xk, convergence):
        """
        Callback function called after each generation.
        Return True to terminate optimization.
        """
        if evaluation_counter[0] >= max_evaluations:
            print(f"\nMax evaluations ({max_evaluations}) reached. Stopping optimization.")
            termination_flag[0] = True
            return True  # Signal termination
        return False  # Continue optimization

    # Run Differential Evolution
    print("Starting optimization...")
    print(f"Note: This will require {max_evaluations} Unity simulations.")
    print()

    # Set scipy maxiter high, but we'll stop via callback
    # This ensures we hit exactly maxiter * popsize evaluations
    scipy_maxiter = maxiter * 10  # Safety margin

    result = differential_evolution(
        func=objective_wrapper,
        bounds=bounds,
        strategy='best1bin',
        maxiter=scipy_maxiter,
        popsize=popsize,
        atol=0.01,
        tol=0.01,
        seed=seed,
        disp=True,
        polish=False,
        workers=1,
        updating='deferred',
        callback=callback
    )

    # Update result message if terminated by callback
    if termination_flag[0]:
        result.message = f"Max evaluations ({max_evaluations}) reached"

    # Print final results
    print("\n" + "=" * 80)
    print("OPTIMIZATION COMPLETE")
    print("=" * 80)
    print(f"Success:         {result.success}")
    print(f"Best Objective:  {result.fun:.4f}")
    print(f"Iterations:      {result.nit}")
    print(f"Evaluations:     {result.nfev}")
    print(f"Message:         {result.message}")
    print()

    # Print best parameters
    best_params = params_array_to_dict(result.x)
    print("BEST PARAMETERS:")
    print("-" * 80)
    for name, value in best_params.items():
        bounds_str = f"[{PARAMETER_BOUNDS[name][0]}, {PARAMETER_BOUNDS[name][1]}]"
        print(f"{name:30s} {value:10.4f}  {bounds_str}")
    print()

    # Save best parameters
    best_output = Path(history_path).parent / "best_parameters.json"
    with open(best_output, 'w') as f:
        json.dump(best_params, f, indent=2)

    print(f"Best parameters saved: {best_output}")
    print(f"Optimization history saved: {history_path}")
    print()

    return result

def analyze_optimization_history(history_path: str):
    """
    Analyze optimization history from CSV.

    Args:
        history_path: Path to optimization_history.csv

    Prints:
    - Summary statistics
    - Best objective per generation
    - Parameter evolution
    - Convergence plot (if matplotlib available)
    """
    history_path = Path(history_path)

    if not history_path.exists():
        print(f"ERROR: History file not found: {history_path}")
        return

    # Read CSV
    with open(history_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) == 0:
        print("ERROR: History file is empty")
        return

    # Convert to numeric
    iterations = [int(row['iteration']) for row in rows]
    objectives = [float(row['objective']) for row in rows]

    # Summary statistics
    print("=" * 80)
    print("OPTIMIZATION HISTORY ANALYSIS")
    print("=" * 80)
    print(f"History file:      {history_path}")
    print(f"Total evaluations: {len(rows)}")
    print(f"Best objective:    {min(objectives):.4f} (iteration {iterations[objectives.index(min(objectives))]})")
    print(f"Worst objective:   {max(objectives):.4f}")
    print(f"Mean objective:    {sum(objectives) / len(objectives):.4f}")
    print(f"Std objective:     {np.std(objectives):.4f}")
    print()

    # Group by generation (assuming evaluations are sequential)
    max_iter = max(iterations)
    generation_size = len([i for i in iterations if i == 1])  # Count first generation evals

    if generation_size > 0:
        print(f"Detected {generation_size} evaluations per generation")
        print()
        print("Best objective per generation:")
        print("-" * 80)

        for gen in range(1, (max_iter // generation_size) + 2):
            gen_start = (gen - 1) * generation_size + 1
            gen_end = gen * generation_size
            gen_objs = [objectives[i] for i, iter_num in enumerate(iterations)
                       if gen_start <= iter_num <= gen_end]

            if gen_objs:
                best_gen_obj = min(gen_objs)
                print(f"  Generation {gen:2d} (iter {gen_start:3d}-{gen_end:3d}): {best_gen_obj:.4f}")

        print()

    # Best parameters
    best_idx = objectives.index(min(objectives))
    best_row = rows[best_idx]

    # Load and compare with baseline
    baseline_obj = load_baseline_objective()
    best_obj = min(objectives)
    improvement = baseline_obj - best_obj
    improvement_pct = (improvement / baseline_obj * 100) if baseline_obj > 0 else 0

    print("BASELINE vs BEST COMPARISON:")
    print("-" * 80)
    print(f"Baseline objective:    {baseline_obj:.4f}")
    print(f"Best objective:        {best_obj:.4f}")
    print(f"Improvement:           {improvement:.4f} ({improvement_pct:+.2f}%)")
    print()

    print("BEST PARAMETERS:")
    print("-" * 80)
    for param_name in PARAMETER_NAMES:
        value = float(best_row[param_name])
        bounds_str = f"[{PARAMETER_BOUNDS[param_name][0]}, {PARAMETER_BOUNDS[param_name][1]}]"
        print(f"{param_name:30s} {value:10.4f}  {bounds_str}")
    print()

    # Try to plot convergence
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        # Plot all evaluations
        plt.subplot(1, 2, 1)
        plt.plot(iterations, objectives, 'o', alpha=0.3, label='All evaluations')
        plt.plot(iterations[best_idx], objectives[best_idx], 'r*', markersize=15, label='Best')
        plt.axhline(y=baseline_obj, color='r', linestyle='--', linewidth=1.5, label='Baseline', alpha=0.7)
        plt.xlabel('Iteration')
        plt.ylabel('Objective')
        plt.title('Optimization History - All Evaluations')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Plot best per generation
        if generation_size > 0:
            plt.subplot(1, 2, 2)
            gen_bests = []
            gen_nums = []

            for gen in range(1, (max_iter // generation_size) + 2):
                gen_start = (gen - 1) * generation_size + 1
                gen_end = gen * generation_size
                gen_objs = [objectives[i] for i, iter_num in enumerate(iterations)
                           if gen_start <= iter_num <= gen_end]

                if gen_objs:
                    gen_bests.append(min(gen_objs))
                    gen_nums.append(gen)

            plt.plot(gen_nums, gen_bests, 'o-', linewidth=2, markersize=8, label='Best per gen')
            plt.axhline(y=baseline_obj, color='r', linestyle='--', linewidth=1.5, label='Baseline', alpha=0.7)
            plt.xlabel('Generation')
            plt.ylabel('Best Objective')
            plt.title('Optimization Convergence - Best per Generation')
            plt.grid(True, alpha=0.3)
            plt.legend()

        plt.tight_layout()
        plot_path = history_path.parent / 'optimization_history.png'
        plt.savefig(plot_path, dpi=150)
        print(f"Convergence plot saved: {plot_path}")
        print()

    except ImportError:
        print("Note: Install matplotlib to generate convergence plots")
        print("  pip install matplotlib")
        print()

def load_baseline_objective(baseline_path: str = "data/output/baseline_objective.json") -> float:
    """
    Load baseline objective from file.

    Args:
        baseline_path: Path to baseline_objective.json

    Returns:
        Baseline objective value (fallback to 4.5932 if file not found)
    """
    baseline_path = Path(baseline_path)

    if not baseline_path.exists():
        print(f"Note: Baseline file not found ({baseline_path}), using hardcoded value 4.5932")
        return 4.5932

    try:
        with open(baseline_path, 'r') as f:
            baseline_data = json.load(f)

        baseline_obj = baseline_data['objective']
        timestamp = baseline_data.get('timestamp', 'N/A')
        print(f"Loaded baseline objective: {baseline_obj:.4f} (saved at {timestamp})")
        return baseline_obj

    except Exception as e:
        print(f"Warning: Failed to load baseline ({e}), using hardcoded value 4.5932")
        return 4.5932

def compare_with_baseline(baseline_obj: float, optimized_obj: float):
    """Print comparison between baseline and optimized results."""
    print("=" * 80)
    print("BASELINE vs OPTIMIZED COMPARISON")
    print("=" * 80)
    print(f"Baseline Objective:   {baseline_obj:.4f}")
    print(f"Optimized Objective:  {optimized_obj:.4f}")
    print(f"Improvement:          {baseline_obj - optimized_obj:.4f}")
    print(f"Improvement %:        {(baseline_obj - optimized_obj) / baseline_obj * 100:.2f}%")
    print("=" * 80)
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Generate and optimize SFM parameters using Differential Evolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create baseline parameters
  python dev/generate_parameters.py --baseline

  # Run optimization (manual mode - Phase 3)
  python dev/generate_parameters.py --optimize --manual --maxiter 1 --popsize 5

  # Analyze optimization history
  python dev/generate_parameters.py --analyze --history data/output/optimization_history.csv

  # Run optimization (auto mode - Phase 4, not yet implemented)
  python dev/generate_parameters.py --optimize --auto --maxiter 50 --popsize 15

Notes:
  - Differential Evolution is a population-based optimization algorithm
  - Population size (popsize): Number of parameter sets per generation
  - Generations (maxiter): Number of generations to run
  - Total evaluations: maxiter * popsize Unity simulations
    * Example: maxiter=1, popsize=5 → 1*5 = 5 total evaluations
    * Example: maxiter=2, popsize=5 → 2*5 = 10 total evaluations
  - Manual mode: You run Unity for each evaluation (Phase 3)
  - Auto mode: Script runs Unity automatically (Phase 4)
  - Analyze mode: Analyze existing optimization history (no Unity required)
        """
    )

    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Create baseline parameter file'
    )

    parser.add_argument(
        '--optimize',
        action='store_true',
        help='Run optimization'
    )

    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze existing optimization history'
    )

    parser.add_argument(
        '--manual',
        action='store_true',
        help='Manual mode: User runs Unity (Phase 3)'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto mode: Script runs Unity (Phase 4, not implemented yet)'
    )

    parser.add_argument(
        '--maxiter',
        type=int,
        default=5,
        help='Number of generations (default: 5). Total evals: maxiter*popsize'
    )

    parser.add_argument(
        '--popsize',
        type=int,
        default=10,
        help='Population size (default: 10)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )

    parser.add_argument(
        '--history',
        type=str,
        default='data/output/optimization_history.csv',
        help='Path to optimization history CSV'
    )

    parser.add_argument(
        '--unity-output',
        type=str,
        default=DEFAULT_UNITY_OUTPUT,
        help=f'Path to Unity simulation result (default: {DEFAULT_UNITY_OUTPUT})'
    )

    args = parser.parse_args()

    try:
        if args.baseline:
            # Create baseline parameters
            output_path = create_baseline_parameters()
            print("=" * 80)
            print("BASELINE PARAMETERS CREATED")
            print("=" * 80)
            print(f"Output: {output_path}")
            print()
            print("Baseline parameters:")
            for name, value in BASELINE_PARAMETERS.items():
                bounds_str = f"[{PARAMETER_BOUNDS[name][0]}, {PARAMETER_BOUNDS[name][1]}]"
                print(f"{name:30s} {value:10.4f}  {bounds_str}")
            print()

        elif args.analyze:
            # Analyze optimization history
            analyze_optimization_history(args.history)

        elif args.optimize:
            if args.auto:
                print("ERROR: Auto mode not implemented yet (Phase 4)")
                print("Use --manual for Phase 3 testing")
                return 1

            if not args.manual:
                print("ERROR: Must specify --manual or --auto")
                return 1

            # Create output directory
            history_path = Path(args.history)
            history_path.parent.mkdir(parents=True, exist_ok=True)

            # Run optimization
            result = run_optimization_manual(
                maxiter=args.maxiter,
                popsize=args.popsize,
                seed=args.seed,
                history_path=str(history_path),
                unity_output_path=args.unity_output
            )

            # Compare with baseline (auto-load from file or fallback)
            baseline_obj = load_baseline_objective()
            compare_with_baseline(baseline_obj, result.fun)

        else:
            print("ERROR: Must specify --baseline, --analyze, or --optimize")
            parser.print_help()
            return 1

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
