"""
Analysis module for optimization results.

Provides functions for analyzing optimization history and generating reports.
"""

from .analyze_history import analyze_optimization_history, load_baseline_objective

__all__ = ['analyze_optimization_history', 'load_baseline_objective']
