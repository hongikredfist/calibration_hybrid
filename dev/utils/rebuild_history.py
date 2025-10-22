"""
Rebuild optimization history CSV from existing result files.

This script recreates the history CSV from eval_0001 to eval_XXXX result files.
Used when resuming optimization from previous runs.

Usage:
    python dev/utils/rebuild_history.py
"""

import json
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

# Add dev to path
sys.path.append(str(Path(__file__).parent.parent))

from evaluate_objective import load_simulation_result, evaluate_objective
from export_to_unity import PARAMETER_NAMES
from core.history_tracker import OptimizationHistory


def rebuild_history_from_results():
    """Rebuild history CSV from eval_0001 to eval_XXXX result files."""

    results_dir = Path("data/output/results")

    # Find all result files
    result_files = sorted(results_dir.glob("eval_*_result.json"))

    if not result_files:
        print("ERROR: No result files found in data/output/results/")
        return

    print("=" * 80)
    print("REBUILD OPTIMIZATION HISTORY FROM RESULTS")
    print("=" * 80)
    print(f"Found {len(result_files)} result files")
    print(f"Range: {result_files[0].name} to {result_files[-1].name}")

    # Use existing filename pattern: history_ScipyDE_best1bin_YYYYMMDD_HHMMSS.csv
    # Keep original date (20251020) to maintain continuity
    history_filename = "history_ScipyDE_best1bin_20251020_134139.csv"
    history_path = Path("data/output") / history_filename

    print(f"\nTarget file: {history_filename}")
    print(f"This will OVERWRITE the existing file with {len(result_files)} rows")
    print("=" * 80)
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    print("\nRebuilding history...")

    # Create new history file (overwrites existing)
    history = OptimizationHistory(str(history_path))

    # Process each result file
    for i, result_file in enumerate(result_files, 1):
        # Extract iteration number from filename (eval_0001 -> 1)
        iteration = int(result_file.stem.split('_')[1])

        # Load result
        result_data = load_simulation_result(str(result_file))

        # Compute objective
        objective, metrics = evaluate_objective(result_data)

        # Extract parameters (18 values)
        params_dict = result_data['parameters']
        params_array = np.array([params_dict[name] for name in PARAMETER_NAMES])

        # Calculate generation (popsize=10, n_params=18)
        population_size = 10 * 18  # 180
        generation = ((iteration - 1) // population_size) + 1

        # Add to history
        history.add_evaluation(
            iteration=iteration,
            objective=objective,
            params=params_array,
            metrics=metrics,
            generation=generation
        )

        # Progress
        if i % 50 == 0 or i == len(result_files):
            print(f"  Processed {i}/{len(result_files)} evaluations...")

    print("\n" + "=" * 80)
    print("✅ HISTORY REBUILT SUCCESSFULLY!")
    print("=" * 80)
    print(f"File: {history_path}")
    print(f"Rows: {len(result_files)}")
    print(f"Range: eval_0001 to eval_{len(result_files):04d}")
    print("=" * 80)
    print()
    print("Next step: Run create_checkpoint.py to create checkpoint for resume")


if __name__ == '__main__':
    rebuild_history_from_results()
