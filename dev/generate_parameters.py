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
        maxiter: Maximum generations
        popsize: Population size
        seed: Random seed
        history_path: Path to save optimization history
        unity_output_path: Path to Unity simulation result
    """
    print("=" * 80)
    print("DIFFERENTIAL EVOLUTION OPTIMIZATION - MANUAL MODE")
    print("=" * 80)
    print(f"Algorithm:       Differential Evolution (scipy)")
    print(f"Parameters:      18 (SFM model)")
    print(f"Population:      {popsize}")
    print(f"Total Generations: {maxiter}")
    print(f"Total Evals:     {maxiter * popsize} Unity simulations")
    print(f"Random Seed:     {seed}")
    print()
    print("Manual mode: You will run Unity simulation for each evaluation")
    print("=" * 80)
    print()

    # Load parameter bounds
    bounds = load_parameter_bounds()

    # Create history tracker
    history = OptimizationHistory(history_path)

    # Counter for iterations
    iteration_counter = [0]

    # Define objective function wrapper
    def objective_wrapper(params):
        iteration_counter[0] += 1
        return objective_function_manual(
            params=params,
            history=history,
            iteration=iteration_counter[0],
            unity_output_path=unity_output_path
        )

    # Run Differential Evolution
    print("Starting optimization...")
    print("Note: This will take a long time. Each evaluation requires Unity simulation.")
    print()

    # Adjust maxiter for scipy: scipy counts generations AFTER init
    # User expects maxiter=2 to mean 2 total generations
    # Scipy expects maxiter=1 to run 2 total generations (init + 1)
    scipy_maxiter = maxiter - 1

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
        updating='deferred'
    )

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
  python dev/generate_parameters.py --optimize --manual --maxiter 5 --popsize 10

  # Run optimization (auto mode - Phase 4, not yet implemented)
  python dev/generate_parameters.py --optimize --auto --maxiter 50 --popsize 15

Beginner Notes:
  - Differential Evolution is a population-based optimization algorithm
  - Population size (popsize): Number of parameter sets per generation
  - Max iterations (maxiter): Total number of generations to run
  - Total evaluations: maxiter * popsize Unity simulations
    * Example: maxiter=2, popsize=5 → 2*5 = 10 total evaluations
  - Manual mode: You run Unity for each evaluation (Phase 3)
  - Auto mode: Script runs Unity automatically (Phase 4)
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
        help='Total number of generations (default: 5 for testing). Total evals: maxiter*popsize'
    )

    parser.add_argument(
        '--popsize',
        type=int,
        default=10,
        help='Population size (default: 10 for testing)'
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
        help='Path to save optimization history CSV'
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

            # Compare with baseline if available
            baseline_obj = 4.5932  # From Phase 2
            compare_with_baseline(baseline_obj, result.fun)

        else:
            print("ERROR: Must specify --baseline or --optimize")
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
