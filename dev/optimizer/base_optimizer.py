"""
Base optimizer interface for parameter calibration.

All optimization algorithms must implement this interface to be compatible
with the calibration system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional
import numpy as np


@dataclass
class OptimizerResult:
    """
    Standardized optimization result.

    All optimizers return this format for consistent analysis and comparison.
    """
    success: bool
    best_params: np.ndarray
    best_objective: float
    n_evaluations: int
    message: str
    algorithm_name: str

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'best_params': self.best_params.tolist(),
            'best_objective': float(self.best_objective),
            'n_evaluations': int(self.n_evaluations),
            'message': self.message,
            'algorithm_name': self.algorithm_name
        }


class BaseOptimizer(ABC):
    """
    Abstract base class for all optimization algorithms.

    Subclasses must implement:
    - optimize(): Run optimization and return OptimizerResult
    - get_algorithm_name(): Return algorithm identifier

    Example:
        class MyOptimizer(BaseOptimizer):
            def optimize(self):
                # Run optimization
                return OptimizerResult(...)

            def get_algorithm_name(self):
                return "MyAlgorithm_v1"
    """

    def __init__(
        self,
        bounds: List[Tuple[float, float]],
        objective_function: Callable[[np.ndarray], float],
        max_evaluations: int,
        seed: Optional[int] = None
    ):
        """
        Initialize optimizer.

        Args:
            bounds: Parameter bounds [(min, max), ...] for each parameter
            objective_function: Function to minimize, signature: params -> objective
            max_evaluations: Maximum number of objective function evaluations
            seed: Random seed for reproducibility (None = random)
        """
        self.bounds = bounds
        self.objective_function = objective_function
        self.max_evaluations = max_evaluations
        self.seed = seed

        self.n_params = len(bounds)
        self.eval_count = 0

    @abstractmethod
    def optimize(self) -> OptimizerResult:
        """
        Run optimization algorithm.

        Returns:
            OptimizerResult with best parameters and metadata
        """
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Return algorithm identifier for logging and result tracking.

        Should include key hyperparameters for reproducibility.
        Example: "ScipyDE_pop15_best1bin"
        """
        pass

    def _validate_params(self, params: np.ndarray) -> bool:
        """
        Validate parameters are within bounds.

        Args:
            params: Parameter array to validate

        Returns:
            True if all parameters within bounds
        """
        if len(params) != self.n_params:
            return False

        for i, (low, high) in enumerate(self.bounds):
            if not (low <= params[i] <= high):
                return False

        return True
