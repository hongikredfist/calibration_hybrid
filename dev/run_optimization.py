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
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime

# Add dev directory to path
sys.path.append(str(Path(__file__).parent))

from core.unity_simulator import UnitySimulator
from core.objective_function import ObjectiveFunction
from core.parameter_utils import load_parameter_bounds, params_array_to_dict
from core.history_tracker import OptimizationHistory
from optimizer.scipy_de_optimizer import ScipyDEOptimizer


def load_checkpoint(checkpoint_path="data/output/checkpoint_latest.pkl"):
    """
    Load checkpoint file.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Dictionary with checkpoint data

    Raises:
        FileNotFoundError: If checkpoint file not found
    """
    path = Path(checkpoint_path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    with open(path, 'rb') as f:
        checkpoint = pickle.load(f)

    return checkpoint


def create_optimizer(args, bounds, objective_function, max_evaluations, checkpoint=None):
    """
    Factory function to create optimizer based on CLI arguments.

    Args:
        args: Argparse namespace
        bounds: Parameter bounds
        objective_function: Objective function callable
        max_evaluations: Calculated max evaluations
        checkpoint: Optional checkpoint dict for resume

    Returns:
        BaseOptimizer instance
    """
    if args.algorithm == 'scipy_de':
        # Extract resume info from checkpoint
        resume_eval = checkpoint.get('eval_counter', 0) if checkpoint else 0
        resume_gen = checkpoint.get('generation', 0) if checkpoint else 0

        return ScipyDEOptimizer(
            bounds=bounds,
            objective_function=objective_function,
            max_evaluations=max_evaluations,
            seed=args.seed,
            popsize=args.popsize,
            generations=args.generations,
            strategy=args.strategy,
            resume_eval_counter=resume_eval,
            resume_generation=resume_gen
        )
    # Future algorithms:
    # elif args.algorithm == 'bayesian':
    #     return BayesianOptimizer(...)
    # elif args.algorithm == 'cmaes':
    #     return CMAESOptimizer(...)
    else:
        raise ValueError(f"Unknown algorithm: {args.algorithm}")


def save_results(result, output_dir: Path, history_csv: Path = None):
    """
    Save optimization results to JSON file.

    Args:
        result: OptimizerResult object
        output_dir: Directory to save results
        history_csv: Path to history CSV to extract true best result
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename based on history CSV filename (if available)
    if history_csv and history_csv.exists():
        # Replace 'history_' with 'result_' and '.csv' with '.json'
        filename = history_csv.stem.replace('history_', 'result_') + '.json'
    else:
        # Fallback to timestamp-based naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{result.algorithm_name}_{timestamp}.json"

    filepath = output_dir / filename

    # Convert to JSON-serializable format
    result_dict = result.to_dict()

    # Override with true best from history CSV (if available)
    if history_csv and history_csv.exists():
        import csv
        with open(history_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if rows:
            # Find true best
            best_row = min(rows, key=lambda r: float(r['objective']))
            best_iteration = int(best_row['iteration'])
            best_generation = int(best_row['generation'])
            best_objective = float(best_row['objective'])

            # Extract best parameters
            from export_to_unity import PARAMETER_NAMES
            best_params = [float(best_row[name]) for name in PARAMETER_NAMES]

            # Override optimizer result with true best
            result_dict['best_objective'] = best_objective
            result_dict['best_params'] = best_params
            result_dict['best_params_dict'] = params_array_to_dict(np.array(best_params))
            result_dict['best_iteration'] = best_iteration
            result_dict['best_generation'] = best_generation
            result_dict['n_evaluations'] = len(rows)

            # Add metrics from best evaluation
            result_dict['best_metrics'] = {
                'mean_error': float(best_row.get('mean_error', 0)),
                'percentile_95': float(best_row.get('percentile_95', 0)),
                'time_growth': float(best_row.get('time_growth', 0)),
                'density_diff': float(best_row.get('density_diff', 0))
            }
    else:
        # Fallback: use optimizer result as-is
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
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from latest checkpoint (data/output/checkpoint_latest.pkl)'
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

    # Check for resume mode
    if args.resume:
        try:
            checkpoint = load_checkpoint()

            print("=" * 80)
            print("RESUMING FROM CHECKPOINT")
            print("=" * 80)
            print(f"Algorithm:       {checkpoint['algorithm']}")
            print(f"Completed:       {checkpoint['eval_counter']}/{checkpoint['max_evaluations']}")
            print(f"Generation:      {checkpoint.get('generation', 'N/A')}")
            print(f"Best so far:     {checkpoint['best_objective']:.4f}")
            print(f"Checkpoint time: {checkpoint['timestamp']}")
            print("=" * 80)
            print()

            # Validation - check algorithm match
            expected_algo = f"ScipyDE_pop{args.popsize}_{args.strategy}"
            if checkpoint['algorithm'] != expected_algo:
                print(f"WARNING: Algorithm mismatch!")
                print(f"  Checkpoint: {checkpoint['algorithm']}")
                print(f"  Current:    {expected_algo}")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return

            # Resume mode specific initialization
            bounds = load_parameter_bounds()
            n_params = len(bounds)

            # Keep original max_evaluations from checkpoint
            max_evaluations = checkpoint['max_evaluations']
            remaining_evals = max_evaluations - checkpoint['eval_counter']
            print(f"Remaining evaluations: {remaining_evals}\n")

            # Restore random state and seed
            np.random.set_state(checkpoint['random_state'])
            args.seed = checkpoint.get('seed', None)  # Restore original seed for logging
            print(f"Random state restored (original seed: {args.seed})")

        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            print("Cannot resume without checkpoint file.")
            return

    else:
        # Normal mode (not resuming)
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

        # For normal mode, remaining = total
        remaining_evals = max_evaluations

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

    # Confirm with user (use remaining_evals for time estimate)
    estimated_time = remaining_evals * 7 / 60  # 7 minutes per eval average
    if args.resume:
        print(f"Estimated remaining time: {estimated_time:.1f} hours ({estimated_time/24:.1f} days)")
        print(f"This will run {remaining_evals} more Unity simulations (total: {checkpoint['eval_counter']}/{max_evaluations}).")
    else:
        print(f"Estimated total time: {estimated_time:.1f} hours ({estimated_time/24:.1f} days)")
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

    # Create history tracker with unique filename (or resume existing)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.resume and checkpoint['history_csv']:
        # Resume mode: use existing history CSV
        history_path = Path(checkpoint['history_csv'])
        history = OptimizationHistory(
            str(history_path),
            append=True,
            start_iteration=0  # No offset needed - eval_counter already correct
        )
        print(f"History tracking: {history_path} (appending from eval {checkpoint['eval_counter']})")
    else:
        # Normal mode: create new history file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.algorithm == 'scipy_de':
            # Simplified filename: only algorithm + strategy (no popsize)
            simplified_name = f"ScipyDE_{args.strategy}"
        else:
            simplified_name = args.algorithm

        history_filename = f"history_{simplified_name}_{timestamp}.csv"
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

    # Set initial best and eval counter if resuming
    if args.resume and checkpoint:
        obj_func.set_initial_best(checkpoint['best_params'], checkpoint['best_objective'])
        obj_func.set_eval_counter(checkpoint['eval_counter'])

    # Create optimizer (pass checkpoint for resume)
    optimizer = create_optimizer(args, bounds, obj_func, max_evaluations, checkpoint if args.resume else None)

    # Run optimization
    try:
        result = optimizer.optimize()

        # Save results (with history CSV for accurate best)
        result_file = save_results(result, output_dir, history_csv=history_path)

        # Save best parameters separately (extract from result_file to get corrected best)
        with open(result_file, 'r') as f:
            result_data = json.load(f)
        best_params_dict = result_data['best_params_dict']
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

        # Print summary (use corrected data from result_file)
        print("\n" + "=" * 80)
        print("OPTIMIZATION SUMMARY")
        print("=" * 80)
        print(f"Algorithm:         {result_data.get('algorithm_name', result.algorithm_name)}")
        print(f"Success:           {result_data.get('success', result.success)}")
        print(f"Best Objective:    {result_data.get('best_objective', result.best_objective):.4f}")
        print(f"Best Iteration:    {result_data.get('best_iteration', 'N/A')}")
        print(f"Best Generation:   {result_data.get('best_generation', 'N/A')}")
        print(f"Total Evaluations: {result_data.get('n_evaluations', result.n_evaluations)}")
        print(f"Message:           {result_data.get('message', result.message)}")
        if result_data.get('seed') is not None:
            print(f"Random Seed:       {result_data['seed']}")

        # Print best metrics if available
        if 'best_metrics' in result_data:
            metrics = result_data['best_metrics']
            print()
            print("Best Metrics:")
            print(f"  RMSE:         {metrics.get('mean_error', 0):.4f}")
            print(f"  Percentile95: {metrics.get('percentile_95', 0):.4f}")
            print(f"  TimeGrowth:   {metrics.get('time_growth', 0):.4f}")
            print(f"  DensityDiff:  {metrics.get('density_diff', 0):.4f}")
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

        # Print reproduction command
        if result.seed is not None:
            print()
            print("To reproduce this result:")
            if args.algorithm == 'scipy_de':
                print(f"  python dev/run_optimization.py --algorithm scipy_de --popsize {args.popsize} --generations {args.generations} --seed {result.seed}")
            else:
                print(f"  python dev/run_optimization.py --algorithm {args.algorithm} --seed {result.seed}")
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
