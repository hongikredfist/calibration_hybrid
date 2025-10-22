"""
Optimization history analysis functions.

Analyzes CSV history files and generates convergence plots.
"""

import json
import csv
from pathlib import Path
import numpy as np

# Import from existing scripts
import sys
sys.path.append(str(Path(__file__).parent.parent))
from export_to_unity import PARAMETER_BOUNDS, PARAMETER_NAMES


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
    generations = [int(row['generation']) for row in rows]

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

    # Group by generation (use CSV generation column)
    unique_generations = sorted(set(generations))

    if len(unique_generations) > 1:
        print("Best objective per generation:")
        print("-" * 80)

        for gen in unique_generations:
            gen_objs = [objectives[i] for i, g in enumerate(generations) if g == gen]
            gen_iters = [iterations[i] for i, g in enumerate(generations) if g == gen]

            if gen_objs:
                best_gen_obj = min(gen_objs)
                best_gen_iter = gen_iters[gen_objs.index(best_gen_obj)]
                print(f"  Generation {gen:2d} ({len(gen_objs):3d} evals): {best_gen_obj:.4f} (iter {best_gen_iter})")

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

        # Plot best per generation (use CSV generation column)
        if len(unique_generations) > 1:
            plt.subplot(1, 2, 2)
            gen_bests = []
            gen_nums = []

            for gen in unique_generations:
                gen_objs = [objectives[i] for i, g in enumerate(generations) if g == gen]
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
            plt.xticks(gen_nums)  # Show only integer generation numbers

        plt.tight_layout()

        # Generate plot filename matching CSV filename
        # CSV: optimization_history_ScipyDE_pop5_20250116_143052.csv
        # PNG: optimization_history_ScipyDE_pop5_20250116_143052.png
        csv_stem = history_path.stem  # filename without extension
        plot_filename = f"{csv_stem}.png"
        plot_path = history_path.parent / plot_filename

        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Convergence plot saved: {plot_path}")
        print()

    except ImportError:
        print("Note: Install matplotlib to generate convergence plots")
        print("  pip install matplotlib")
        print()
