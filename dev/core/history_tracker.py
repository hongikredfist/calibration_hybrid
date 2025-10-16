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

    def __init__(self, output_path: str):
        """
        Initialize history tracker.

        Args:
            output_path: Path to CSV file (will be created if doesn't exist)
        """
        self.output_path = Path(output_path)
        self.history = []

        # Create CSV file with header
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['iteration', 'timestamp', 'objective'] + PARAMETER_NAMES
            writer.writerow(header)

    def add_evaluation(self, iteration: int, objective: float, params: np.ndarray):
        """
        Add evaluation result to history.

        Args:
            iteration: Evaluation iteration number
            objective: Objective value (lower is better)
            params: Parameter array (18 values)
        """
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
