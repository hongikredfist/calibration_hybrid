"""
Parameter conversion and validation utilities.

Provides functions for:
- Loading parameter bounds from export_to_unity.py
- Converting between array and dictionary formats
- Parameter validation and clamping
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# Import from existing scripts
sys.path.append(str(Path(__file__).parent.parent))
from export_to_unity import PARAMETER_BOUNDS, PARAMETER_NAMES


def load_parameter_bounds() -> List[Tuple[float, float]]:
    """
    Load 18 parameter bounds for optimization.

    Returns:
        List of (min, max) tuples for each parameter in order
    """
    bounds = [PARAMETER_BOUNDS[name] for name in PARAMETER_NAMES]
    return bounds


def params_array_to_dict(params: np.ndarray) -> Dict[str, float]:
    """
    Convert numpy array to parameter dictionary.

    Args:
        params: Array of 18 parameter values

    Returns:
        Dictionary mapping parameter names to values

    Example:
        >>> params = np.array([0.2, 0.5, 1.2, ...])
        >>> params_dict = params_array_to_dict(params)
        >>> params_dict['minimalDistance']
        0.2
    """
    if len(params) != len(PARAMETER_NAMES):
        raise ValueError(
            f"Expected {len(PARAMETER_NAMES)} parameters, got {len(params)}"
        )

    return {name: float(params[i]) for i, name in enumerate(PARAMETER_NAMES)}


def params_dict_to_array(params_dict: Dict[str, float]) -> np.ndarray:
    """
    Convert parameter dictionary to numpy array.

    Args:
        params_dict: Dictionary mapping parameter names to values

    Returns:
        Array of parameter values in standard order

    Example:
        >>> params_dict = {'minimalDistance': 0.2, 'relaxationTime': 0.5, ...}
        >>> params = params_dict_to_array(params_dict)
        >>> params[0]
        0.2
    """
    params = np.array([params_dict[name] for name in PARAMETER_NAMES])
    return params


def validate_and_clamp_params(params: np.ndarray) -> np.ndarray:
    """
    Validate parameters and clamp to bounds if necessary.

    Args:
        params: Parameter array to validate

    Returns:
        Clamped parameter array (all values within bounds)
    """
    bounds = load_parameter_bounds()
    clamped = params.copy()

    for i, (low, high) in enumerate(bounds):
        if clamped[i] < low:
            clamped[i] = low
        elif clamped[i] > high:
            clamped[i] = high

    return clamped


def get_baseline_parameters() -> Dict[str, float]:
    """
    Get baseline parameter values (Unity defaults).

    Returns:
        Dictionary of baseline parameters
    """
    from generate_parameters import BASELINE_PARAMETERS
    return BASELINE_PARAMETERS.copy()
