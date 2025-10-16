"""
Unified optimization CLI for parameter calibration.

This is the main entry point for running automated parameter optimization
with different algorithms.

Usage:
    # Default (720 evals, intuitive interface)
    python run_optimization.py --algorithm scipy_de

    # Custom generations and population
    python run_optimization.py --algorithm scipy_de --popsize 10 --generations 4

    # Quick test
    python run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

    # Reproducible run (specify seed)
    python run_optimization.py --algorithm scipy_de --seed 42

Future algorithms:
    python run_optimization.py --algorithm bayesian
    python run_optimization.py --algorithm cmaes
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
from core.history_tracker import OptimizationHistory
from optimizer.scipy_de_optimizer import ScipyDEOptimizer


def create_optimizer(args, bounds, objective_function, max_evaluations):
    """
    Factory function to create optimizer based on CLI arguments.

    Args:
        args: Argparse namespace
        bounds: Parameter bounds
        objective_function: Objective function callable
        max_evaluations: Calculated max evaluations

    Returns:
        BaseOptimizer instance
    """
    if args.algorithm == 'scipy_de':
        return ScipyDEOptimizer(
            bounds=bounds,
            objective_function=objective_function,
            max_evaluations=max_evaluations,
            seed=args.seed,
            popsize=args.popsize,
            generations=args.generations,
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
  # Default (720 evals, ~2-3 days)
  python run_optimization.py --algorithm scipy_de

  # Quick test (36 evals, ~5 hours)
  python run_optimization.py --algorithm scipy_de --popsize 2 --generations 1

  # More exploration (1350 evals, ~5 days)
  python run_optimization.py --algorithm scipy_de --popsize 15 --generations 5

  # Reproducible run (specify seed)
  python run_optimization.py --algorithm scipy_de --seed 42

  # Custom Unity path
  python run_optimization.py --algorithm scipy_de --unity-path "C:/Unity/Editor/Unity.exe"
        """
    )

    # Required arguments
    parser.add_argument(
        '--algorithm',
        choices=['scipy_de'],  # Future: 'bayesian', 'cmaes', 'pso'
        default='scipy_de',
        help='Optimization algorithm to use'
    )

    # Optional arguments
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (default: None = auto-generate and save for reproducibility)'
    )
    parser.add_argument(
        '--max-evals',
        type=int,
        default=None,
        help='[Optional] Hard limit on evaluations (default: None = auto-calculate from popsize×generations)'
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
        default=10,
        help='[Scipy DE] Population multiplier: actual_pop = popsize × 18 params (default: 10 → 180 individuals/gen)'
    )
    parser.add_argument(
        '--generations',
        type=int,
        default=4,
        help='[Scipy DE] Number of generations (default: 4)'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        default='best1bin',
        choices=['best1bin', 'best2bin', 'rand1bin', 'rand2bin'],
        help='[Scipy DE] Mutation strategy (default: best1bin)'
    )

    args = parser.parse_args()

    # Initialize components
    bounds = load_parameter_bounds()
    n_params = len(bounds)

    # Calculate max_evaluations
    if args.max_evals is None:
        # Auto-calculate from popsize × n_params × generations
        max_evaluations = args.popsize * n_params * args.generations
    else:
        # User-specified override
        max_evaluations = args.max_evals

    # Print configuration
    print("=" * 80)
    print("PARAMETER CALIBRATION - AUTOMATED OPTIMIZATION (FILE TRIGGER MODE)")
    print("=" * 80)
    print()
    print("IMPORTANT: Unity Editor must be open with the project loaded!")
    print("Project: D:\\UnityProjects\\META_VERYOLD_P01_s")
    print()
    print(f"Algorithm:       {args.algorithm}")
    print(f"Max Evaluations: {max_evaluations}")
    print(f"Random Seed:     {args.seed if args.seed is not None else 'Random'}")
    print(f"Unity Timeout:   {args.timeout}s per simulation")
    print(f"Output Dir:      {args.output_dir}")

    if args.algorithm == 'scipy_de':
        actual_pop = args.popsize * n_params
        print(f"\nScipyDE Configuration:")
        print(f"  Population:    {args.popsize} (multiplier) → {actual_pop} individuals/generation")
        print(f"  Generations:   {args.generations}")
        print(f"  Strategy:      {args.strategy}")
        if args.max_evals is not None:
            print(f"  Note:          max-evals override active ({args.max_evals} limit)")

    print("=" * 80)
    print()

    # Confirm with user
    estimated_time = max_evaluations * 7 / 60  # 7 minutes per eval average
    print(f"Estimated time: {estimated_time:.1f} hours ({estimated_time/24:.1f} days)")
    print(f"This will run {max_evaluations} Unity simulations automatically.")
    print(f"Unity Editor will remain open during optimization.")
    print()

    response = input("Continue? [y/n]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return

    print("\nStarting optimization...\n")
    print(f"Loaded {n_params} parameter bounds")

    # Use file trigger mode (Unity Editor must be open)
    unity_sim = UnitySimulator(
        unity_editor_path=args.unity_path,
        project_path=args.project_path,
        timeout=args.timeout,
        use_file_trigger=True
    )

    # Create history tracker with unique filename
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique history filename: optimization_history_{algorithm}_{timestamp}.csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.algorithm == 'scipy_de':
        algorithm_name = f"ScipyDE_pop{args.popsize}_{args.strategy}"
    else:
        algorithm_name = args.algorithm

    history_filename = f"optimization_history_{algorithm_name}_{timestamp}.csv"
    history_path = output_dir / history_filename

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
    optimizer = create_optimizer(args, bounds, obj_func, max_evaluations)

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

        # Automatic analysis and convergence plot
        print("\n" + "=" * 80)
        print("GENERATING ANALYSIS AND CONVERGENCE PLOT")
        print("=" * 80)
        from analysis.analyze_history import analyze_optimization_history
        try:
            analyze_optimization_history(str(history_path))
        except Exception as e:
            print(f"Warning: Analysis failed: {e}")
            print("You can manually analyze with:")
            print(f"  python dev/analysis/analyze_history.py {history_path}")

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

        # Check if plot was created (same stem as CSV, different extension)
        plot_file = history_path.with_suffix('.png')
        if plot_file.exists():
            print(f"  - Plot:         {plot_file}")

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
