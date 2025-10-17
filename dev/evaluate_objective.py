import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

DEFAULT_UNITY_OUTPUT = r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\simulation_result.json"

# Objective function weights (must sum to 1.0)
WEIGHTS = {
    'mean_error': 0.40,       # Individual trajectory accuracy (reduced from 0.50)
    'percentile_95': 0.25,    # Outlier control (reduced from 0.30)
    'time_growth': 0.15,      # Temporal stability (reduced from 0.20)
    'density_diff': 0.20      # Crowd-level density fidelity (NEW)
}

def load_simulation_result(filepath: str) -> Dict[str, Any]:
    """Load simulation result JSON file."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path, 'r') as f:
        data = json.load(f)

    return data

def compute_percentile_95(agent_errors: List[Dict[str, Any]]) -> float:
    """
    Compute 95th percentile of agent mean errors.
    This prevents extreme outliers from dominating the objective.
    """
    if not agent_errors:
        return 0.0

    agent_mean_errors = [agent['meanError'] for agent in agent_errors]
    percentile_95 = np.percentile(agent_mean_errors, 95)

    return percentile_95

def compute_time_growth_penalty(agent_errors: List[Dict[str, Any]]) -> float:
    """
    Compute average error growth rate using linear regression.

    For each agent:
    - Fit linear regression: error = slope × time + intercept
    - Extract slope (rate of error growth per time step)
    - Only penalize positive slopes (growing error over time)

    Returns:
        Average positive slope across all agents (higher = more unstable)
    """
    if not agent_errors:
        return 0.0

    from scipy.stats import linregress

    growth_slopes = []

    for agent in agent_errors:
        errors = agent.get('errors', [])

        if len(errors) < 4:  # Need at least 4 points for meaningful regression
            continue

        # Extract error values and time indices
        error_values = [e['error'] for e in errors]
        time_indices = list(range(len(error_values)))

        # Linear regression: error = slope × time + intercept
        slope, intercept, r_value, p_value, std_err = linregress(time_indices, error_values)

        # Only penalize positive slopes (growing error)
        # Negative slopes indicate improving accuracy over time (good!)
        growth_slopes.append(max(0.0, slope))

    if not growth_slopes:
        return 0.0

    return np.mean(growth_slopes)

def get_top_growth_agents(agent_errors: List[Dict[str, Any]], top_n: int = 5) -> List[Tuple[int, float, float, float]]:
    """
    Get agents with highest error growth rates.

    Returns:
        List of (agent_id, early_mean, late_mean, growth_rate)
    """
    agent_growth_data = []

    for agent in agent_errors:
        errors = agent.get('errors', [])

        if len(errors) < 4:
            continue

        quarter = len(errors) // 4
        early_errors = errors[:quarter]
        late_errors = errors[-quarter:]

        early_values = [e['error'] for e in early_errors]
        late_values = [e['error'] for e in late_errors]

        early_mean = np.mean(early_values)
        late_mean = np.mean(late_values)

        if early_mean > 0.1:
            growth = (late_mean - early_mean) / early_mean
        else:
            growth = 0.0

        agent_growth_data.append((
            agent['agentId'],
            early_mean,
            late_mean,
            growth
        ))

    # Sort by growth rate descending
    agent_growth_data.sort(key=lambda x: x[3], reverse=True)

    return agent_growth_data[:top_n]

def compute_density_difference(simulation_result: Dict[str, Any]) -> float:
    """
    Compute spatial density distribution difference (RMSE).

    Compares empirical vs SFM agent density across spatial grid over time.
    This provides macroscopic validation of crowd behavior patterns.

    Args:
        simulation_result: Parsed JSON data from Unity

    Returns:
        density_rmse: Density distribution RMSE (0 if no density data available)
    """
    # Check if density metrics are available (backward compatibility)
    if 'densityMetrics' not in simulation_result or simulation_result['densityMetrics'] is None:
        return 0.0

    density_rmse = simulation_result['densityMetrics']['densityRMSE']
    return density_rmse

def evaluate_objective(simulation_result: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Compute objective value from simulation result.

    Objective = 0.40 * RMSE + 0.25 * Percentile95 + 0.15 * TimeGrowth + 0.20 * DensityDiff
    Lower value = better performance

    Args:
        simulation_result: Parsed JSON data from Unity

    Returns:
        objective: Single scalar value (lower = better)
        metrics: Dict of individual metric values for debugging
    """
    # 1. RMSE (40%) - Individual trajectory accuracy (Root Mean Square Error)
    # RMSE is more sensitive to large errors than MAE (literature standard)
    agent_errors = simulation_result['agentErrors']
    if agent_errors:
        agent_mean_errors = [agent['meanError'] for agent in agent_errors]
        mean_error = np.sqrt(np.mean([err ** 2 for err in agent_mean_errors]))
    else:
        mean_error = 0.0

    # 2. Percentile95 (25%) - Prevent extreme outliers
    percentile_95 = compute_percentile_95(simulation_result['agentErrors'])

    # 3. TimeGrowthPenalty (15%) - Ensure temporal stability
    time_growth = compute_time_growth_penalty(simulation_result['agentErrors'])

    # 4. DensityDifference (20%) - Crowd-level density fidelity (NEW)
    density_diff = compute_density_difference(simulation_result)

    # Weighted sum
    objective = (
        WEIGHTS['mean_error'] * mean_error +
        WEIGHTS['percentile_95'] * percentile_95 +
        WEIGHTS['time_growth'] * time_growth +
        WEIGHTS['density_diff'] * density_diff
    )

    metrics = {
        'mean_error': mean_error,
        'percentile_95': percentile_95,
        'time_growth': time_growth,
        'density_diff': density_diff,
        'objective': objective,
        'weighted_mean': WEIGHTS['mean_error'] * mean_error,
        'weighted_p95': WEIGHTS['percentile_95'] * percentile_95,
        'weighted_growth': WEIGHTS['time_growth'] * time_growth,
        'weighted_density': WEIGHTS['density_diff'] * density_diff
    }

    return objective, metrics

def print_evaluation(simulation_result: Dict[str, Any], metrics: Dict[str, float], verbose: bool = False):
    """Print objective evaluation results."""
    print("=" * 80)
    print("OBJECTIVE EVALUATION")
    print("=" * 80)
    print(f"Experiment ID:       {simulation_result.get('experimentId', 'N/A')}")
    print(f"Execution Time:      {simulation_result.get('executionTimeSeconds', 0):.2f} seconds")
    print(f"Total Agents:        {simulation_result.get('totalAgents', 0)}")
    print()

    print("METRICS BREAKDOWN:")
    print("-" * 80)
    print(f"RMSE ({WEIGHTS['mean_error']:.0%}):               "
          f"{metrics['mean_error']:8.4f} m   →   "
          f"{metrics['weighted_mean']:8.4f} weighted")
    print(f"Percentile95 ({WEIGHTS['percentile_95']:.0%}):     "
          f"{metrics['percentile_95']:8.4f} m   →   "
          f"{metrics['weighted_p95']:8.4f} weighted")
    print(f"TimeGrowthPenalty ({WEIGHTS['time_growth']:.0%}): "
          f"{metrics['time_growth']:8.4f}     →   "
          f"{metrics['weighted_growth']:8.4f} weighted")
    print(f"DensityDifference ({WEIGHTS['density_diff']:.0%}): "
          f"{metrics['density_diff']:8.4f}     →   "
          f"{metrics['weighted_density']:8.4f} weighted")
    print()
    print(f"OBJECTIVE VALUE:      {metrics['objective']:8.4f}     (lower is better)")
    print("=" * 80)
    print()

    if verbose:
        print("TOP 10 WORST TIME-GROWTH AGENTS:")
        print("-" * 80)
        print(f"{'Agent ID':<12} {'Early Mean':<15} {'Late Mean':<15} {'Growth':<15}")
        print("-" * 80)

        top_agents = get_top_growth_agents(simulation_result['agentErrors'], top_n=10)
        for agent_id, early, late, growth in top_agents:
            print(f"{agent_id:<12} {early:<15.4f} {late:<15.4f} {growth:+14.2%}")
        print()

def save_baseline_objective(
    simulation_result: Dict[str, Any],
    objective: float,
    metrics: Dict[str, float],
    output_path: str = "data/output/baseline_objective.json"
):
    """
    Save baseline objective for future comparison.

    Args:
        simulation_result: Full simulation result data
        objective: Computed objective value
        metrics: Metrics breakdown
        output_path: Path to save baseline JSON
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    baseline_data = {
        "objective": objective,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat(),
        "experimentId": simulation_result.get("experimentId", "N/A"),
        "parameters": simulation_result.get("parameters", {}),
        "totalAgents": simulation_result.get("totalAgents", 0),
        "executionTimeSeconds": simulation_result.get("executionTimeSeconds", 0)
    }

    with open(output_path, 'w') as f:
        json.dump(baseline_data, f, indent=2)

    print("=" * 80)
    print("BASELINE OBJECTIVE SAVED")
    print("=" * 80)
    print(f"Output file:     {output_path}")
    print(f"Objective value: {objective:.4f}")
    print(f"Timestamp:       {baseline_data['timestamp']}")
    print()
    print("This baseline will be used for comparison in future optimizations.")
    print("To update baseline, run this command again with --save-baseline")
    print("=" * 80)
    print()

def compare_evaluations(filepaths: List[str]):
    """Compare objective values across multiple simulation results."""
    print("=" * 80)
    print("OBJECTIVE COMPARISON")
    print("=" * 80)
    print()

    results = []

    for filepath in filepaths:
        try:
            data = load_simulation_result(filepath)
            objective, metrics = evaluate_objective(data)

            results.append({
                'file': Path(filepath).name,
                'experiment_id': data.get('experimentId', 'N/A')[:8],
                'objective': objective,
                'mean_error': metrics['mean_error'],
                'percentile_95': metrics['percentile_95'],
                'time_growth': metrics['time_growth']
            })
        except Exception as e:
            print(f"ERROR loading {filepath}: {e}")
            continue

    if not results:
        print("No valid results to compare")
        return

    # Sort by objective (best first)
    results.sort(key=lambda x: x['objective'])

    print(f"{'Rank':<6} {'Exp ID':<10} {'Objective':<12} {'MeanErr':<10} {'P95':<10} {'Growth':<10} {'File':<30}")
    print("-" * 95)

    for i, result in enumerate(results, 1):
        rank_marker = "[BEST]" if i == 1 else f"{i:4d}  "
        print(f"{rank_marker:<6} "
              f"{result['experiment_id']:<10} "
              f"{result['objective']:<12.4f} "
              f"{result['mean_error']:<10.4f} "
              f"{result['percentile_95']:<10.4f} "
              f"{result['time_growth']:<10.4f} "
              f"{result['file']:<30}")

    print()
    print(f"Best objective:  {results[0]['objective']:.4f} ({results[0]['file']})")
    print(f"Worst objective: {results[-1]['objective']:.4f} ({results[-1]['file']})")
    print(f"Improvement:     {results[-1]['objective'] - results[0]['objective']:.4f} "
          f"({(results[-1]['objective'] - results[0]['objective']) / results[-1]['objective'] * 100:.1f}%)")
    print()

def find_latest_result_file(output_dir: str = None) -> str:
    """
    Find the most recently created *_result.json file.

    Args:
        output_dir: Directory to search (default: Unity StreamingAssets/Calibration/Output)

    Returns:
        Path to most recent result file

    Raises:
        FileNotFoundError: If no result files found
    """
    if output_dir is None:
        output_dir = Path(DEFAULT_UNITY_OUTPUT).parent
    else:
        output_dir = Path(output_dir)

    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    # Find all *_result.json files
    result_files = list(output_dir.glob("*_result.json"))

    if not result_files:
        raise FileNotFoundError(f"No *_result.json files found in {output_dir}")

    # Sort by modification time (most recent first)
    result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return str(result_files[0])

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate objective function from Unity PIONA simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev/evaluate_objective.py                              # Use latest result file
  python dev/evaluate_objective.py --file path/to/result.json   # Use specific file
  python dev/evaluate_objective.py --verbose
  python dev/evaluate_objective.py --compare file1.json file2.json file3.json
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        default=None,
        help='Path to result JSON file (default: most recent *_result.json)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed time-growth statistics'
    )

    parser.add_argument(
        '--compare', '-c',
        nargs='+',
        type=str,
        help='Compare multiple simulation results'
    )

    parser.add_argument(
        '--save-baseline',
        action='store_true',
        help='Save current result as baseline for future optimization comparison'
    )

    args = parser.parse_args()

    try:
        if args.compare:
            compare_evaluations(args.compare)
        else:
            # Auto-detect latest file if not specified
            if args.file is None:
                try:
                    args.file = find_latest_result_file()
                    print(f"[Auto-detected] Using latest result file: {Path(args.file).name}")
                    print()
                except FileNotFoundError as e:
                    print(f"ERROR: {e}")
                    print("Please specify a file with --file option")
                    return 1

            data = load_simulation_result(args.file)
            objective, metrics = evaluate_objective(data)
            print_evaluation(data, metrics, verbose=args.verbose)

            if args.save_baseline:
                save_baseline_objective(data, objective, metrics)

            print(f"[OK] Objective value computed: {objective:.4f}")
            print(f"[OK] Lower is better (optimization goal: minimize this value)")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format - {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
