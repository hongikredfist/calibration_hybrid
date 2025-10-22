"""
Create checkpoint from existing history CSV.

This script creates a checkpoint file from rebuilt history CSV,
allowing optimization to resume from the last completed evaluation.

Usage:
    python dev/utils/create_checkpoint.py
"""

import pickle
import csv
import numpy as np
from pathlib import Path
from datetime import datetime


def create_checkpoint_from_history():
    """Create checkpoint from rebuilt history CSV."""

    # Find history CSV
    history_file = Path("data/output/history_ScipyDE_best1bin_20251020_134139.csv")

    if not history_file.exists():
        print("=" * 80)
        print("ERROR: History file not found")
        print("=" * 80)
        print(f"Expected: {history_file}")
        print()
        print("Run rebuild_history.py first to create the history file!")
        return

    print("=" * 80)
    print("CREATE CHECKPOINT FROM HISTORY")
    print("=" * 80)
    print(f"Reading history: {history_file.name}")

    # Read CSV
    rows = []
    with open(history_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"Total evaluations: {len(rows)}")

    # Find best evaluation
    best_row = min(rows, key=lambda r: float(r['objective']))
    best_iteration = int(best_row['iteration'])
    best_objective = float(best_row['objective'])

    print(f"\nBest evaluation found:")
    print(f"  Iteration:  {best_iteration}")
    print(f"  Objective:  {best_objective:.4f}")
    print(f"  RMSE:       {float(best_row['mean_error']):.4f}")
    print(f"  P95:        {float(best_row['percentile_95']):.4f}")

    # Extract best parameters (18 values)
    param_names = [
        'minimalDistance', 'relaxationTime', 'repulsionStrengthAgent',
        'repulsionRangeAgent', 'lambdaAgent', 'repulsionStrengthObs',
        'repulsionRangeObs', 'lambdaObs', 'k', 'kappa', 'obsK', 'obsKappa',
        'considerationRange', 'viewAngle', 'viewAngleMax', 'viewDistance',
        'rayStepAngle', 'visibleFactor'
    ]
    best_params = np.array([float(best_row[name]) for name in param_names])

    # Last evaluation (checkpoint point)
    last_row = rows[-1]
    last_iteration = int(last_row['iteration'])

    print(f"\nCheckpoint will be created at:")
    print(f"  Last iteration: {last_iteration}")
    print(f"  Next iteration: {last_iteration + 1}")
    print(f"  Remaining:      {720 - last_iteration} evaluations")

    # Create checkpoint
    checkpoint = {
        'eval_counter': last_iteration,
        'best_params': best_params,
        'best_objective': best_objective,
        'random_state': np.random.get_state(),  # New random state
        'history_csv': str(history_file),
        'algorithm': 'ScipyDE_pop10_best1bin',
        'popsize': 10,
        'seed': 1234567890,  # Placeholder (will be ignored on resume)
        'max_evaluations': 720,
        'timestamp': datetime.now().isoformat()
    }

    # Save checkpoint
    checkpoint_path = Path("data/output/checkpoint_latest.pkl")
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(checkpoint, f)

    print("\n" + "=" * 80)
    print("✅ CHECKPOINT CREATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"File:      {checkpoint_path}")
    print(f"Resume from:    eval_{last_iteration + 1:04d}")
    print(f"Remaining evals: {720 - last_iteration}")
    print("=" * 80)
    print()
    print("You can now resume optimization with:")
    print("  python dev/run_optimization.py --algorithm scipy_de --resume")


if __name__ == '__main__':
    create_checkpoint_from_history()
