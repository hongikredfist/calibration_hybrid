"""
Optimization history tracking for parameter calibration.

Tracks evaluation results and saves to CSV file for later analysis.
"""

import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import numpy as np

# Import parameter names from export_to_unity
import sys
sys.path.append(str(Path(__file__).parent.parent))
from export_to_unity import PARAMETER_NAMES


class OptimizationHistory:
    """
    Track optimization history and save to CSV.

    Creates CSV file with header and appends each evaluation result.
    Used by optimizers to track progress during optimization.

    Example:
        history = OptimizationHistory("data/output/optimization_history.csv")
        history.add_evaluation(iteration=1, objective=4.5, params=param_array)
        best = history.get_best()
    """

    def __init__(self, output_path: str, append: bool = False, start_iteration: int = 0):
        """
        Initialize history tracker.

        Args:
            output_path: Path to CSV file (will be created if doesn't exist)
            append: If True, append to existing file (resume mode)
            start_iteration: Starting iteration number (for resume)
        """
        self.output_path = Path(output_path)
        self.history = []
        self.start_iteration = start_iteration

        if append and self.output_path.exists():
            # Append mode: skip header, existing file preserved
            print(f"[History] Appending to existing file: {output_path}")
        else:
            # New file mode: create with header
            with open(self.output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                header = ['iteration', 'generation', 'timestamp', 'objective',
                          'mean_error', 'percentile_95', 'time_growth', 'density_diff'] + PARAMETER_NAMES
                writer.writerow(header)

    def add_evaluation(self, iteration: int, objective: float, params: np.ndarray,
                      metrics: Dict[str, Any] = None, generation: int = 0):
        """
        Add evaluation result to history.

        Args:
            iteration: Evaluation iteration number (relative if resuming)
            objective: Objective value (lower is better)
            params: Parameter array (18 values)
            metrics: Optional dict with individual metrics (mean_error, percentile_95, time_growth, density_diff)
            generation: Generation number (0 if not applicable)
        """
        # Adjust iteration number for resume mode
        actual_iteration = self.start_iteration + iteration

        timestamp = datetime.now().isoformat()
        entry = {
            'iteration': actual_iteration,
            'generation': generation,
            'timestamp': timestamp,
            'objective': objective,
            'params': params.tolist(),
            'metrics': metrics
        }
        self.history.append(entry)

        # Extract individual metrics (with defaults for backward compatibility)
        if metrics is not None:
            mean_error = metrics.get('mean_error', 0.0)
            percentile_95 = metrics.get('percentile_95', 0.0)
            time_growth = metrics.get('time_growth', 0.0)
            density_diff = metrics.get('density_diff', 0.0)
        else:
            mean_error = percentile_95 = time_growth = density_diff = 0.0

        # Append to CSV
        with open(self.output_path, 'a', newline='') as f:
            writer = csv.writer(f)
            row = [actual_iteration, generation, timestamp, objective,
                   mean_error, percentile_95, time_growth, density_diff] + params.tolist()
            writer.writerow(row)

    def get_best(self) -> Dict[str, Any]:
        """
        Get best evaluation so far.

        Returns:
            Dictionary with best evaluation data (iteration, objective, params)
            Returns None if no evaluations recorded yet
        """
        if not self.history:
            return None

        best = min(self.history, key=lambda x: x['objective'])
        return best
