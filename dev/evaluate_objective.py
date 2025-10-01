import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple

DEFAULT_UNITY_OUTPUT = r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\simulation_result.json"

WEIGHTS = {
    'mean_error': 0.50,
    'percentile_95': 0.30,
    'time_growth': 0.20
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
    Compute average error growth rate from early to late trajectory.

    For each agent:
    - Compare first 25% of trajectory with last 25%
    - Calculate growth rate: (late_mean - early_mean) / early_mean
    - Only penalize positive growth (increasing error)

    Returns:
        Average growth rate across all agents (0 = no growth, 3.0 = 300% growth)
    """
    if not agent_errors:
        return 0.0

    growth_rates = []

    for agent in agent_errors:
        errors = agent.get('errors', [])

        if len(errors) < 4:
            continue

        # Split into quarters
        quarter = len(errors) // 4
        early_errors = errors[:quarter]
        late_errors = errors[-quarter:]

        # Extract error values
        early_values = [e['error'] for e in early_errors]
        late_values = [e['error'] for e in late_errors]

        early_mean = np.mean(early_values)
        late_mean = np.mean(late_values)

        # Calculate growth rate
        if early_mean > 0.1:  # Avoid division by very small numbers
            growth = (late_mean - early_mean) / early_mean
        else:
            growth = 0.0

        # Only penalize growth (not improvement)
        growth_rates.append(max(0.0, growth))

    if not growth_rates:
        return 0.0

    return np.mean(growth_rates)

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

def evaluate_objective(simulation_result: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Compute objective value from simulation result.

    Objective = 0.50 * MeanError + 0.30 * Percentile95 + 0.20 * TimeGrowth
    Lower value = better performance

    Args:
        simulation_result: Parsed JSON data from Unity

    Returns:
        objective: Single scalar value (lower = better)
        metrics: Dict of individual metric values for debugging
    """
    # 1. MeanError (50%) - Overall average accuracy
    mean_error = simulation_result['averageError']

    # 2. Percentile95 (30%) - Prevent extreme outliers
    percentile_95 = compute_percentile_95(simulation_result['agentErrors'])

    # 3. TimeGrowthPenalty (20%) - Ensure temporal stability
    time_growth = compute_time_growth_penalty(simulation_result['agentErrors'])

    # Weighted sum
    objective = (
        WEIGHTS['mean_error'] * mean_error +
        WEIGHTS['percentile_95'] * percentile_95 +
        WEIGHTS['time_growth'] * time_growth
    )

    metrics = {
        'mean_error': mean_error,
        'percentile_95': percentile_95,
        'time_growth': time_growth,
        'objective': objective,
        'weighted_mean': WEIGHTS['mean_error'] * mean_error,
        'weighted_p95': WEIGHTS['percentile_95'] * percentile_95,
        'weighted_growth': WEIGHTS['time_growth'] * time_growth
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
    print(f"MeanError ({WEIGHTS['mean_error']:.0%}):          "
          f"{metrics['mean_error']:8.4f} m   →   "
          f"{metrics['weighted_mean']:8.4f} weighted")
    print(f"Percentile95 ({WEIGHTS['percentile_95']:.0%}):     "
          f"{metrics['percentile_95']:8.4f} m   →   "
          f"{metrics['weighted_p95']:8.4f} weighted")
    print(f"TimeGrowthPenalty ({WEIGHTS['time_growth']:.0%}): "
          f"{metrics['time_growth']:8.4f}     →   "
          f"{metrics['weighted_growth']:8.4f} weighted")
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

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate objective function from Unity PIONA simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev/evaluate_objective.py
  python dev/evaluate_objective.py --file path/to/result.json
  python dev/evaluate_objective.py --verbose
  python dev/evaluate_objective.py --compare file1.json file2.json file3.json
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        default=DEFAULT_UNITY_OUTPUT,
        help=f'Path to simulation_result.json (default: {DEFAULT_UNITY_OUTPUT})'
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

    args = parser.parse_args()

    try:
        if args.compare:
            compare_evaluations(args.compare)
        else:
            data = load_simulation_result(args.file)
            objective, metrics = evaluate_objective(data)
            print_evaluation(data, metrics, verbose=args.verbose)

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
