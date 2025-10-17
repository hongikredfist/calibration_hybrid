"""
Scipy Differential Evolution optimizer implementation.

Wraps scipy.optimize.differential_evolution to conform to BaseOptimizer interface.
"""

import numpy as np
from scipy.optimize import differential_evolution
from typing import Callable, List, Tuple, Optional

from optimizer.base_optimizer import BaseOptimizer, OptimizerResult


class ScipyDEOptimizer(BaseOptimizer):
    """
    Scipy Differential Evolution optimizer.

    Differential Evolution is a population-based, gradient-free optimization
    algorithm well-suited for black-box optimization problems like Unity simulations.

    Key features:
    - No gradients required (Unity simulation is black-box)
    - Global optimization (explores entire parameter space)
    - Robust to noise and local minima
    - Simple configuration (3-4 hyperparameters)

    IMPORTANT - Scipy popsize behavior:
    - popsize is a MULTIPLIER, not absolute population size
    - Actual population = popsize × n_parameters
    - For 18 parameters: popsize=10 → 180 individuals/generation
    - Total evaluations = (popsize × n_params) × generations
    - Recommended popsize range: 5-15 (90-270 individuals for 18D problem)
    - Minimum 3 generations needed for evolution to work effectively

    References:
        - Storn & Price (1997): "Differential Evolution - A Simple and Efficient
          Heuristic for Global Optimization over Continuous Spaces"
        - scipy.optimize.differential_evolution documentation

    Example:
        # Direct generations control (recommended)
        optimizer = ScipyDEOptimizer(
            bounds=[(0.15, 0.35), (0.3, 0.8), ...],  # 18 parameter bounds
            objective_function=obj_func,
            max_evaluations=720,  # Used for history tracking
            popsize=10,           # 10×18 = 180 individuals/generation
            generations=4,        # 4 generations
            seed=None             # Random seed (default)
        )
        result = optimizer.optimize()
        print(f"Best objective: {result.best_objective}")

        # Alternative: auto-calculate generations from max_evaluations
        optimizer = ScipyDEOptimizer(
            bounds=bounds,
            objective_function=obj_func,
            max_evaluations=720,  # Auto: 720/(10×18) = 4 generations
            popsize=10
        )
    """

    def __init__(
        self,
        bounds: List[Tuple[float, float]],
        objective_function: Callable[[np.ndarray], float],
        max_evaluations: int,
        seed: Optional[int] = None,
        popsize: int = 10,
        generations: Optional[int] = None,
        strategy: str = 'best1bin',
        mutation: Tuple[float, float] = (0.5, 1.0),
        recombination: float = 0.7,
        atol: float = 0.01,
        tol: float = 0.01
    ):
        """
        Initialize Scipy DE optimizer.

        Args:
            bounds: Parameter bounds [(min, max), ...]
            objective_function: Function to minimize, signature: params -> objective
            max_evaluations: Target number of evaluations (used if generations not specified)
            seed: Random seed for reproducibility (None = random seed)
            popsize: Population multiplier (actual_pop = popsize × n_params, default: 10, recommended: 5-15)
            generations: Number of generations (default: None = auto-calculate from max_evaluations)
            strategy: DE mutation strategy ('best1bin', 'rand1bin', 'best2bin', etc.)
            mutation: Mutation factor range (min, max)
            recombination: Crossover probability [0, 1]
            atol: Absolute tolerance for convergence
            tol: Relative tolerance for convergence
        """
        super().__init__(bounds, objective_function, max_evaluations, seed)

        self.popsize = popsize
        self.strategy = strategy
        self.mutation = mutation
        self.recombination = recombination
        self.atol = atol
        self.tol = tol

        # Generate random seed if not provided (for reproducibility)
        if seed is None:
            import random
            self.seed = random.randint(0, 2**31 - 1)
            self.seed_was_random = True
        else:
            self.seed_was_random = False

        # Calculate max iterations (generations)
        # Priority: generations parameter > auto-calculate from max_evaluations
        n_params = len(bounds)
        if generations is not None:
            self.maxiter = generations
            self.generations = generations
        else:
            # Auto-calculate: max_evals / (popsize × n_params)
            self.maxiter = max_evaluations // (popsize * n_params)
            self.generations = self.maxiter

    def optimize(self) -> OptimizerResult:
        """
        Run Scipy Differential Evolution optimization.

        Uses callback mechanism to ensure exact evaluation count:
        - Scipy maxiter is set high (maxiter * 10)
        - Callback counts evaluations and stops when limit reached
        - This guarantees exactly max_evaluations evaluations

        Returns:
            OptimizerResult with best parameters and metadata
        """
        print("=" * 80)
        print("SCIPY DIFFERENTIAL EVOLUTION OPTIMIZATION")
        print("=" * 80)
        print(f"Algorithm:       {self.get_algorithm_name()}")
        print(f"Parameters:      {self.n_params}")
        print(f"Population:      {self.popsize}")
        print(f"Max Generations: {self.maxiter}")
        print(f"Max Evaluations: {self.max_evaluations}")
        print(f"Strategy:        {self.strategy}")
        print(f"Mutation:        {self.mutation}")
        print(f"Recombination:   {self.recombination}")
        if self.seed_was_random:
            print(f"Random Seed:     {self.seed} (auto-generated, use --seed {self.seed} to reproduce)")
        else:
            print(f"Random Seed:     {self.seed} (user-specified)")
        print("=" * 80)
        print()

        # Evaluation counter, generation tracker, and termination flag
        eval_counter = [0]
        current_generation = [0]  # Track current generation number
        termination_flag = [False]

        # Objective function wrapper (counts evaluations and enforces limit)
        def objective_wrapper(params):
            eval_counter[0] += 1
            self.eval_count = eval_counter[0]

            # Calculate current generation (1-indexed)
            # Population size = popsize × n_params
            population_size = self.popsize * len(self.bounds)
            current_generation[0] = ((eval_counter[0] - 1) // population_size) + 1

            # Check if limit exceeded BEFORE running evaluation
            if eval_counter[0] > self.max_evaluations:
                print(f"\n[Optimizer] Evaluation limit reached ({self.max_evaluations}), skipping eval {eval_counter[0]}")
                termination_flag[0] = True
                # Return large penalty to signal termination
                return 1e10

            # Pass generation number to objective function
            if hasattr(self.objective_function, 'set_generation'):
                self.objective_function.set_generation(current_generation[0])

            return self.objective_function(params)

        # Callback to enforce evaluation limit (called after each generation)
        def callback(xk, convergence):
            """
            Callback called after each generation.

            Args:
                xk: Current best solution
                convergence: Convergence metric

            Returns:
                True to stop optimization, False to continue
            """
            if eval_counter[0] >= self.max_evaluations:
                print(f"\n[Optimizer] Stopping optimization: {eval_counter[0]} evaluations completed")
                termination_flag[0] = True
                return True  # Stop optimization
            return False  # Continue

        # Run Differential Evolution
        print("Starting optimization...")
        print(f"Note: Callback will stop at exactly {self.max_evaluations} evaluations")
        print()

        # Set scipy maxiter high, callback will enforce actual limit
        scipy_maxiter = self.maxiter * 10

        result = differential_evolution(
            func=objective_wrapper,
            bounds=self.bounds,
            strategy=self.strategy,
            maxiter=scipy_maxiter,
            popsize=self.popsize,
            mutation=self.mutation,
            recombination=self.recombination,
            atol=self.atol,
            tol=self.tol,
            seed=self.seed,
            disp=False,  # Suppress scipy output (we print our own)
            polish=False,  # No local polish (stays within bounds)
            workers=1,  # Single worker (Unity can't run in parallel)
            updating='deferred',  # Update population after all evaluations
            callback=callback
        )

        # Update message if terminated by callback
        message = result.message
        if termination_flag[0]:
            message = f"Max evaluations ({self.max_evaluations}) reached"

        # Print summary
        print("\n" + "=" * 80)
        print("OPTIMIZATION COMPLETE")
        print("=" * 80)
        print(f"Success:         {result.success or termination_flag[0]}")
        print(f"Best Objective:  {result.fun:.4f}")
        print(f"Iterations:      {result.nit}")
        print(f"Evaluations:     {eval_counter[0]}")
        print(f"Message:         {message}")
        print("=" * 80)
        print()

        return OptimizerResult(
            success=result.success or termination_flag[0],
            best_params=result.x,
            best_objective=result.fun,
            n_evaluations=eval_counter[0],
            message=message,
            algorithm_name=self.get_algorithm_name(),
            seed=self.seed
        )

    def get_algorithm_name(self) -> str:
        """
        Return algorithm identifier including key hyperparameters.

        Format: ScipyDE_pop{popsize}_{strategy}

        Example: "ScipyDE_pop15_best1bin"
        """
        return f"ScipyDE_pop{self.popsize}_{self.strategy}"


def test_scipy_de_optimizer():
    """
    Test Scipy DE optimizer with a simple quadratic function.

    Minimizes: f(x) = sum(x^2)
    Expected minimum: x = [0, 0, ..., 0], f(x) = 0
    """
    print("=" * 80)
    print("SCIPY DE OPTIMIZER TEST (Quadratic Function)")
    print("=" * 80)

    # Simple test function: sum of squares
    def quadratic(params):
        return np.sum(params ** 2)

    # Bounds: [-5, 5] for each parameter
    n_params = 5
    bounds = [(-5.0, 5.0) for _ in range(n_params)]

    # Create optimizer
    optimizer = ScipyDEOptimizer(
        bounds=bounds,
        objective_function=quadratic,
        max_evaluations=100,
        popsize=10,
        seed=42
    )

    # Run optimization
    result = optimizer.optimize()

    print(f"\n[TEST] Results:")
    print(f"  Algorithm:       {result.algorithm_name}")
    print(f"  Success:         {result.success}")
    print(f"  Best Objective:  {result.best_objective:.6f}")
    print(f"  Best Params:     {result.best_params}")
    print(f"  Evaluations:     {result.n_evaluations}")
    print(f"  Expected:        ~0.0 at [0, 0, 0, 0, 0]")

    # Verify
    if result.best_objective < 0.01:
        print(f"\n[TEST] SUCCESS! Found minimum close to zero.")
    else:
        print(f"\n[TEST] Warning: Minimum not reached (try more evaluations)")


if __name__ == '__main__':
    # Run test
    test_scipy_de_optimizer()
