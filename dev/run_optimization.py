"""
Unified optimization CLI for parameter calibration.

This is the main entry point for running automated parameter optimization
with different algorithms.

Usage:
    python run_optimization.py --algorithm scipy_de --max-evals 100 --seed 42

    python run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5 --test

Future algorithms:
    python run_optimization.py --algorithm bayesian --max-evals 100
    python run_optimization.py --algorithm cmaes --max-evals 100
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add dev directory to path
sys.path.append(str(Path(__file__).parent))

from core.unity_simulator import UnitySimulator
from core.objective_function import ObjectiveFunction
from core.parameter_utils import load_parameter_bounds, params_array_to_dict
from optimizer.scipy_de_optimizer import ScipyDEOptimizer
from generate_parameters import OptimizationHistory


def create_optimizer(args, bounds, objective_function):
    """
    Factory function to create optimizer based on CLI arguments.

    Args:
        args: Argparse namespace
        bounds: Parameter bounds
        objective_function: Objective function callable

    Returns:
        BaseOptimizer instance
    """
    if args.algorithm == 'scipy_de':
        return ScipyDEOptimizer(
            bounds=bounds,
            objective_function=objective_function,
            max_evaluations=args.max_evals,
            seed=args.seed,
            popsize=args.popsize,
            strategy=args.strategy
        )
    # Future algorithms:
    # elif args.algorithm == 'bayesian':
    #     return BayesianOptimizer(...)
    # elif args.algorithm == 'cmaes':
    #     return CMAESOptimizer(...)
    else:
        raise ValueError(f"Unknown algorithm: {args.algorithm}")


def save_results(result, output_dir: Path):
    """
    Save optimization results to JSON file.

    Args:
        result: OptimizerResult object
        output_dir: Directory to save results
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp and algorithm name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{result.algorithm_name}_{timestamp}.json"
    filepath = output_dir / filename

    # Convert to JSON-serializable format
    result_dict = result.to_dict()

    # Add parameter dictionary for readability
    result_dict['best_params_dict'] = params_array_to_dict(result.best_params)

    # Save
    with open(filepath, 'w') as f:
        json.dump(result_dict, f, indent=2)

    print(f"Results saved: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Automated parameter calibration for Unity PIONA simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test run (10 evaluations, ~1 hour)
  python run_optimization.py --algorithm scipy_de --max-evals 10 --popsize 5

  # Production run (750 evaluations, ~3 days)
  python run_optimization.py --algorithm scipy_de --max-evals 750 --popsize 15 --seed 42

  # Custom Unity path
  python run_optimization.py --algorithm scipy_de --max-evals 100 --unity-path "C:/Unity/Editor/Unity.exe"
        """
    )

    # Required arguments
    parser.add_argument(
        '--algorithm',
        choices=['scipy_de'],  # Future: 'bayesian', 'cmaes', 'pso'
        default='scipy_de',
        help='Optimization algorithm to use'
    )
    parser.add_argument(
        '--max-evals',
        type=int,
        required=True,
        help='Maximum number of objective evaluations (Unity simulations)'
    )

    # Optional arguments
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--unity-path',
        type=str,
        default=None,
        help='Path to Unity.exe (default: auto-detect)'
    )
    parser.add_argument(
        '--project-path',
        type=str,
        default=None,
        help='Path to Unity project (default: D:/UnityProjects/META_VERYOLD_P01_s)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Timeout per simulation in seconds (default: 600 = 10min)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/output',
        help='Output directory for results (default: data/output)'
    )

    # Scipy DE specific arguments
    parser.add_argument(
        '--popsize',
        type=int,
        default=15,
        help='[Scipy DE] Population size (default: 15)'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        default='best1bin',
        choices=['best1bin', 'best2bin', 'rand1bin', 'rand2bin'],
        help='[Scipy DE] Mutation strategy (default: best1bin)'
    )

    args = parser.parse_args()

    # Print configuration
    print("=" * 80)
    print("PARAMETER CALIBRATION - AUTOMATED OPTIMIZATION")
    print("=" * 80)
    print(f"Algorithm:       {args.algorithm}")
    print(f"Max Evaluations: {args.max_evals}")
    print(f"Random Seed:     {args.seed}")
    print(f"Unity Timeout:   {args.timeout}s per simulation")
    print(f"Output Dir:      {args.output_dir}")

    if args.algorithm == 'scipy_de':
        print(f"\nScipyDE Configuration:")
        print(f"  Population:    {args.popsize}")
        print(f"  Strategy:      {args.strategy}")
        print(f"  Generations:   ~{args.max_evals // args.popsize}")

    print("=" * 80)
    print()

    # Confirm with user
    estimated_time = args.max_evals * 7 / 60  # 7 minutes per eval average
    print(f"Estimated time: {estimated_time:.1f} hours ({estimated_time/24:.1f} days)")
    print(f"This will run {args.max_evals} Unity simulations automatically.")
    print()

    response = input("Continue? [y/N]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return

    print("\nStarting optimization...\n")

    # Initialize components
    bounds = load_parameter_bounds()
    print(f"Loaded {len(bounds)} parameter bounds")

    unity_sim = UnitySimulator(
        unity_editor_path=args.unity_path,
        project_path=args.project_path,
        timeout=args.timeout
    )

    # Create history tracker
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    history_path = output_dir / "optimization_history.csv"
    history = OptimizationHistory(str(history_path))
    print(f"History tracking: {history_path}")
    print()

    # Create objective function
    obj_func = ObjectiveFunction(
        unity_simulator=unity_sim,
        history_tracker=history,
        verbose=True
    )

    # Create optimizer
    optimizer = create_optimizer(args, bounds, obj_func)

    # Run optimization
    try:
        result = optimizer.optimize()

        # Save results
        result_file = save_results(result, output_dir)

        # Save best parameters separately
        best_params_dict = params_array_to_dict(result.best_params)
        best_params_file = output_dir / "best_parameters.json"
        with open(best_params_file, 'w') as f:
            json.dump(best_params_dict, f, indent=2)
        print(f"Best parameters saved: {best_params_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("OPTIMIZATION SUMMARY")
        print("=" * 80)
        print(f"Algorithm:        {result.algorithm_name}")
        print(f"Success:          {result.success}")
        print(f"Best Objective:   {result.best_objective:.4f}")
        print(f"Total Evaluations: {result.n_evaluations}")
        print(f"Message:          {result.message}")
        print()
        print("Files created:")
        print(f"  - Results:      {result_file}")
        print(f"  - Best params:  {best_params_file}")
        print(f"  - History:      {history_path}")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\nOptimization interrupted by user (Ctrl+C)")
        print(f"Partial results saved to: {history_path}")
        sys.exit(1)

    except Exception as e:
        print(f"\n\nOptimization failed with error:")
        print(f"  {type(e).__name__}: {e}")
        print(f"\nPartial results may be in: {history_path}")
        raise

    finally:
        unity_sim.cleanup()


if __name__ == '__main__':
    main()
