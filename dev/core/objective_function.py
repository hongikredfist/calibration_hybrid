"""
Objective function wrapper for optimization algorithms.

Coordinates Unity simulation execution and result evaluation.
Provides a callable interface that optimizers can use.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

# Import from existing scripts
sys.path.append(str(Path(__file__).parent.parent))
from evaluate_objective import load_simulation_result, evaluate_objective
from core.unity_simulator import UnitySimulator


class ObjectiveFunction:
    """
    Callable objective function for parameter optimization.

    This class wraps Unity simulation execution and result evaluation
    into a single callable that optimization algorithms can use.

    The function signature matches what optimizers expect:
        f(params: np.ndarray) -> float

    Example:
        simulator = UnitySimulator()
        obj_func = ObjectiveFunction(simulator)

        params = np.array([0.2, 0.5, 1.2, ...])  # 18 parameters
        objective = obj_func(params)  # Returns objective value
    """

    def __init__(
        self,
        unity_simulator: UnitySimulator,
        history_tracker: Optional[Any] = None,
        verbose: bool = True
    ):
        """
        Initialize objective function.

        Args:
            unity_simulator: UnitySimulator instance for running simulations
            history_tracker: Optional history tracker (e.g., OptimizationHistory)
            verbose: Print detailed evaluation info
        """
        self.simulator = unity_simulator
        self.history = history_tracker
        self.verbose = verbose

        self.eval_count = 0
        self.current_generation = 0  # Track current generation
        self.evaluations = []  # Store all evaluations

    def set_generation(self, generation: int):
        """
        Set current generation number (called by optimizer).

        Args:
            generation: Current generation number (1-indexed)
        """
        self.current_generation = generation

    def __call__(self, params: np.ndarray) -> float:
        """
        Evaluate objective function for given parameters.

        Workflow:
        1. Increment evaluation counter
        2. Run Unity simulation with parameters
        3. Load simulation result
        4. Compute objective value
        5. Track history (if tracker provided)
        6. Return objective

        Args:
            params: Parameter array (18 values)

        Returns:
            Objective value (lower is better)

        Raises:
            TimeoutError: If Unity simulation times out
            RuntimeError: If Unity crashes or produces invalid results
        """
        self.eval_count += 1

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"EVALUATION {self.eval_count}")
            print(f"{'='*80}")

        # Run Unity simulation
        experiment_id = f"eval_{self.eval_count:04d}"
        result_path = self.simulator.run_simulation(params, experiment_id)

        # Load result
        if self.verbose:
            print(f"[ObjectiveFunction] Loading result: {Path(result_path).name}")

        result_data = load_simulation_result(result_path)

        # Compute objective
        objective, metrics = evaluate_objective(result_data)

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"EVALUATION {self.eval_count} - RESULTS")
            print(f"{'='*80}")
            print(f"Objective:      {objective:.4f}")
            print(f"RMSE:           {metrics['mean_error']:.4f}")
            print(f"Percentile95:   {metrics['percentile_95']:.4f}")
            print(f"TimeGrowth:     {metrics['time_growth']:.4f}")
            print(f"DensityDiff:    {metrics['density_diff']:.4f}")
            print(f"{'='*80}\n")

        # Track history
        evaluation_record = {
            'iteration': self.eval_count,
            'params': params.copy(),
            'objective': objective,
            'metrics': metrics.copy(),
            'experiment_id': experiment_id
        }
        self.evaluations.append(evaluation_record)

        if self.history is not None:
            self.history.add_evaluation(
                iteration=self.eval_count,
                objective=objective,
                params=params,
                metrics=metrics,  # Pass individual metrics to history tracker
                generation=self.current_generation  # Pass generation number
            )

        return objective

    def get_best_evaluation(self) -> Dict[str, Any]:
        """
        Get best evaluation so far.

        Returns:
            Dictionary with best evaluation data
        """
        if not self.evaluations:
            return None

        best = min(self.evaluations, key=lambda x: x['objective'])
        return best

    def get_evaluation_count(self) -> int:
        """
        Get total number of evaluations performed.

        Returns:
            Evaluation count
        """
        return self.eval_count

    def reset(self):
        """
        Reset evaluation counter and history.

        Use this to start a fresh optimization run.
        """
        self.eval_count = 0
        self.evaluations.clear()


def test_objective_function():
    """
    Test objective function with baseline parameters.

    Run this to verify the full pipeline works:
    Unity simulation → Result loading → Objective evaluation
    """
    print("="*80)
    print("OBJECTIVE FUNCTION TEST (FILE TRIGGER MODE)")
    print("="*80)
    print()
    print("IMPORTANT: Unity Editor must be open with the project loaded!")
    print("Project: D:\\UnityProjects\\META_VERYOLD_P01_s")
    print()
    input("Press ENTER when Unity Editor is ready...")
    print()

    # Import utilities
    from core.parameter_utils import get_baseline_parameters, params_dict_to_array
    from core.unity_simulator import UnitySimulator

    # Get baseline parameters
    baseline = get_baseline_parameters()
    params = params_dict_to_array(baseline)

    print(f"Testing with baseline parameters")
    print(f"Expected objective: ~4.59 (baseline)")

    # Create simulator and objective function (FILE TRIGGER MODE)
    simulator = UnitySimulator(timeout=600, use_file_trigger=True)
    obj_func = ObjectiveFunction(simulator, verbose=True)

    # Evaluate
    try:
        objective = obj_func(params)

        print(f"\n[TEST] SUCCESS!")
        print(f"[TEST] Objective: {objective:.4f}")
        print(f"[TEST] Evaluation count: {obj_func.get_evaluation_count()}")

        # Get best evaluation
        best = obj_func.get_best_evaluation()
        print(f"[TEST] Best evaluation:")
        print(f"  - Iteration: {best['iteration']}")
        print(f"  - Objective: {best['objective']:.4f}")
        print(f"  - Experiment ID: {best['experiment_id']}")

        # Verify objective is reasonable
        if abs(objective - 4.59) > 1.0:
            print(f"\n[TEST] WARNING: Objective {objective:.4f} differs significantly from expected ~4.59")
        else:
            print(f"\n[TEST] Objective is within expected range!")

    except Exception as e:
        print(f"\n[TEST] FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        simulator.cleanup()


if __name__ == '__main__':
    # Run test
    test_objective_function()
