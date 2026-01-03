"""
Core experiments for market-making research.

This module contains the four main experiments:
1. PnL Decomposition - Quantify adverse selection costs
2. VPIN Analysis - Validate toxicity detection
3. Regime Switching - Test adaptive strategy
4. Failure Analysis - Document edge cases
"""

from .config import ExperimentConfig
from .experiment_base import BaseExperiment

__all__ = [
    'ExperimentConfig',
    'BaseExperiment',
]

