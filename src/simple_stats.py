"""
Simple statistics for experiment results.

No fancy stuff - just mean ± std and basic p-values.
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple


def mean_with_std(values: List[float]) -> Tuple[float, float]:
    """
    Calculate mean ± standard deviation.
    
    Args:
        values: List of values from multiple runs
    
    Returns:
        (mean, std_dev)
    """
    if len(values) == 0:
        return 0.0, 0.0
    
    return float(np.mean(values)), float(np.std(values))


def format_mean_std(mean: float, std: float, decimals: int = 2) -> str:
    """
    Format as "mean ± std".
    
    Args:
        mean: Mean value
        std: Standard deviation
        decimals: Number of decimal places
    
    Returns:
        Formatted string like "1.42 ± 0.15"
    """
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


def simple_ttest(values_a: List[float], values_b: List[float]) -> Dict:
    """
    Simple t-test comparing two groups.
    
    Args:
        values_a: Values from group A
        values_b: Values from group B
    
    Returns:
        Dict with p_value and significance stars
    """
    if len(values_a) < 2 or len(values_b) < 2:
        return {
            'p_value': 1.0,
            'significance': 'ns',
            'mean_diff': 0.0
        }
    
    # Independent t-test
    t_stat, p_value = stats.ttest_ind(values_a, values_b)
    
    # Significance stars
    if p_value < 0.001:
        significance = '***'
    elif p_value < 0.01:
        significance = '**'
    elif p_value < 0.05:
        significance = '*'
    else:
        significance = 'ns'
    
    mean_diff = np.mean(values_a) - np.mean(values_b)
    
    return {
        'p_value': float(p_value),
        'significance': significance,
        'mean_diff': float(mean_diff),
        't_stat': float(t_stat)
    }


def format_pvalue(p_value: float, show_value: bool = True) -> str:
    """
    Format p-value with significance stars.
    
    Args:
        p_value: P-value from test
        show_value: Whether to show numeric value
    
    Returns:
        Formatted string like "p=0.003 ***" or just "***"
    """
    if p_value < 0.001:
        sig = '***'
    elif p_value < 0.01:
        sig = '**'
    elif p_value < 0.05:
        sig = '*'
    else:
        sig = 'ns'
    
    if show_value:
        if p_value < 0.001:
            return f"p<0.001 {sig}"
        else:
            return f"p={p_value:.3f} {sig}"
    else:
        return sig

