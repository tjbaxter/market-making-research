"""
Statistical analysis utilities for market-making research.

Provides bootstrap confidence intervals, hypothesis testing, and statistical comparisons.
"""

import numpy as np
from typing import Dict, List, Tuple, Callable
from scipy import stats


def bootstrap_confidence_interval(
    data: np.ndarray,
    statistic_func: Callable,
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95
) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval for a statistic.
    
    Args:
        data: Original data array
        statistic_func: Function that calculates the statistic (e.g., np.mean)
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence_level: Confidence level (default: 0.95 for 95% CI)
    
    Returns:
        (point_estimate, lower_bound, upper_bound)
    
    Example:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> mean, lower, upper = bootstrap_confidence_interval(data, np.mean)
    """
    bootstrap_statistics = []
    n = len(data)
    
    np.random.seed(42)  # For reproducibility
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stat = statistic_func(bootstrap_sample)
        bootstrap_statistics.append(bootstrap_stat)
    
    bootstrap_statistics = np.array(bootstrap_statistics)
    
    # Calculate percentiles
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    point_estimate = statistic_func(data)
    lower_bound = np.percentile(bootstrap_statistics, lower_percentile)
    upper_bound = np.percentile(bootstrap_statistics, upper_percentile)
    
    return point_estimate, lower_bound, upper_bound


def sharpe_ratio_func(returns: np.ndarray) -> float:
    """
    Calculate annualized Sharpe ratio from returns array.
    
    Args:
        returns: Array of returns
    
    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    return np.mean(returns) / np.std(returns) * np.sqrt(252)


def max_drawdown_func(pnl_series: np.ndarray) -> float:
    """
    Calculate maximum drawdown from PnL series.
    
    Args:
        pnl_series: Array of PnL values
    
    Returns:
        Maximum drawdown (positive value)
    """
    if len(pnl_series) == 0:
        return 0.0
    
    cumulative = np.array(pnl_series)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = running_max - cumulative
    return np.max(drawdown)


def analyze_metric_with_ci(
    values: np.ndarray,
    statistic_func: Callable,
    n_bootstrap: int = 1000
) -> Dict:
    """
    Analyze a metric with confidence intervals and hypothesis testing.
    
    Args:
        values: Array of metric values from multiple runs
        statistic_func: Function to calculate the statistic
        n_bootstrap: Number of bootstrap samples
    
    Returns:
        Dict with point_estimate, ci_lower, ci_upper, p_value (vs zero), n_samples
    """
    # Bootstrap CI
    point_est, ci_lower, ci_upper = bootstrap_confidence_interval(
        values, statistic_func, n_bootstrap=n_bootstrap
    )
    
    # One-sample t-test (H0: mean = 0)
    if len(values) > 1:
        t_stat, p_value = stats.ttest_1samp(values, 0.0)
    else:
        t_stat, p_value = 0.0, 1.0
    
    return {
        'point_estimate': float(point_est),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'p_value': float(p_value),
        'n_samples': len(values),
        't_statistic': float(t_stat)
    }


def compare_strategies_paired_ttest(
    values_a: np.ndarray,
    values_b: np.ndarray,
    strategy_a_name: str = "Strategy A",
    strategy_b_name: str = "Strategy B"
) -> Dict:
    """
    Compare two strategies using paired t-test.
    
    Assumes both strategies were run with same random seeds (paired samples).
    
    Args:
        values_a: Metric values from strategy A
        values_b: Metric values from strategy B
        strategy_a_name: Name of strategy A
        strategy_b_name: Name of strategy B
    
    Returns:
        Dict with t_statistic, p_value, mean_difference, cohens_d, significance flags
    """
    # Paired t-test
    if len(values_a) != len(values_b):
        raise ValueError("Strategies must have same number of samples for paired test")
    
    if len(values_a) < 2:
        return {
            'strategy_a': strategy_a_name,
            'strategy_b': strategy_b_name,
            't_statistic': 0.0,
            'p_value': 1.0,
            'mean_difference': 0.0,
            'cohens_d': 0.0,
            'significant_at_0.05': False,
            'significant_at_0.01': False
        }
    
    t_stat, p_value = stats.ttest_rel(values_a, values_b)
    
    # Effect size (Cohen's d for paired samples)
    differences = values_a - values_b
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0
    
    return {
        'strategy_a': strategy_a_name,
        'strategy_b': strategy_b_name,
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'mean_difference': float(mean_diff),
        'cohens_d': float(cohens_d),
        'significant_at_0.05': p_value < 0.05,
        'significant_at_0.01': p_value < 0.01
    }


def bonferroni_correction(p_values: List[float]) -> List[float]:
    """
    Apply Bonferroni correction for multiple comparisons.
    
    Args:
        p_values: List of p-values
    
    Returns:
        List of corrected p-values (capped at 1.0)
    """
    n_comparisons = len(p_values)
    return [min(p * n_comparisons, 1.0) for p in p_values]


def compare_all_strategies(
    results_dict: Dict[str, np.ndarray],
    metric_name: str = "metric"
) -> Dict:
    """
    Compare all strategies pairwise with Bonferroni correction.
    
    Args:
        results_dict: Dict mapping strategy names to arrays of metric values
        metric_name: Name of metric being compared (for reporting)
    
    Returns:
        Dict with comparison results and corrected p-values
    """
    from itertools import combinations
    
    strategy_names = list(results_dict.keys())
    comparisons = []
    p_values = []
    
    for strat_a, strat_b in combinations(strategy_names, 2):
        comparison = compare_strategies_paired_ttest(
            results_dict[strat_a],
            results_dict[strat_b],
            strat_a,
            strat_b
        )
        comparisons.append(comparison)
        p_values.append(comparison['p_value'])
    
    # Apply Bonferroni correction
    corrected_p_values = bonferroni_correction(p_values)
    
    for comp, corrected_p in zip(comparisons, corrected_p_values):
        comp['p_value_bonferroni'] = corrected_p
        comp['significant_bonferroni'] = corrected_p < 0.05
    
    return {
        'comparisons': comparisons,
        'metric': metric_name,
        'n_comparisons': len(comparisons)
    }


def format_significance(p_value: float) -> str:
    """
    Format p-value as significance stars.
    
    Args:
        p_value: P-value from hypothesis test
    
    Returns:
        String with stars: '***' for p<0.001, '**' for p<0.01, '*' for p<0.05, 'ns' otherwise
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'


def calculate_effect_size_interpretation(cohens_d: float) -> str:
    """
    Interpret Cohen's d effect size.
    
    Args:
        cohens_d: Cohen's d value
    
    Returns:
        String interpretation ('negligible', 'small', 'medium', 'large')
    """
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        return 'negligible'
    elif abs_d < 0.5:
        return 'small'
    elif abs_d < 0.8:
        return 'medium'
    else:
        return 'large'

