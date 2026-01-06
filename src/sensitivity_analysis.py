"""
Parameter sensitivity analysis for market-making strategies.

Provides grid search, heatmap generation, and robustness analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable
from itertools import product
from tqdm import tqdm


def grid_search_parameters(
    parameter_grid: Dict[str, List[float]],
    simulation_func: Callable,
    n_runs_per_config: int = 20,
    metrics: List[str] = ['sharpe_ratio', 'max_drawdown', 'total_pnl'],
    verbose: bool = True
) -> pd.DataFrame:
    """
    Perform grid search over parameter space.
    
    Args:
        parameter_grid: Dict mapping parameter names to lists of values
            Example: {'risk_aversion': [0.01, 0.05, 0.1], 'vpin_threshold': [0.6, 0.7, 0.8]}
        simulation_func: Function that takes parameters and seed, returns dict with metrics
        n_runs_per_config: Number of Monte Carlo runs per configuration
        metrics: List of metrics to track
        verbose: Show progress bar
    
    Returns:
        DataFrame with columns: [param1, param2, ..., metric1_mean, metric1_std, metric1_ci_lower, metric1_ci_upper, ...]
    """
    # Generate all parameter combinations
    param_names = list(parameter_grid.keys())
    param_values = list(parameter_grid.values())
    combinations = list(product(*param_values))
    
    results = []
    
    iterator = tqdm(combinations, desc="Grid search") if verbose else combinations
    
    for combo in iterator:
        # Create parameter dict
        params = dict(zip(param_names, combo))
        
        # Run simulations with these parameters
        run_results = []
        for run_idx in range(n_runs_per_config):
            try:
                result = simulation_func(**params, seed=42 + run_idx)
                run_results.append(result)
            except Exception as e:
                if verbose:
                    print(f"Warning: Simulation failed for params {params}: {e}")
                continue
        
        if len(run_results) == 0:
            continue
        
        # Calculate statistics for this configuration
        config_stats = params.copy()
        
        for metric in metrics:
            values = np.array([r.get(metric, np.nan) for r in run_results])
            values = values[~np.isnan(values)]  # Remove NaN values
            
            if len(values) > 0:
                config_stats[f'{metric}_mean'] = np.mean(values)
                config_stats[f'{metric}_std'] = np.std(values)
                config_stats[f'{metric}_ci_lower'] = np.percentile(values, 2.5)
                config_stats[f'{metric}_ci_upper'] = np.percentile(values, 97.5)
            else:
                config_stats[f'{metric}_mean'] = np.nan
                config_stats[f'{metric}_std'] = np.nan
                config_stats[f'{metric}_ci_lower'] = np.nan
                config_stats[f'{metric}_ci_upper'] = np.nan
        
        results.append(config_stats)
    
    return pd.DataFrame(results)


def create_heatmap_data(
    results_df: pd.DataFrame,
    x_param: str,
    y_param: str,
    z_metric: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data for heatmap plotting.
    
    Args:
        results_df: DataFrame from grid_search_parameters
        x_param: Parameter name for x-axis
        y_param: Parameter name for y-axis
        z_metric: Metric name for heatmap values (e.g., 'sharpe_ratio_mean')
    
    Returns:
        (x_values, y_values, z_matrix) suitable for plotting
    """
    # Get unique parameter values
    x_values = sorted(results_df[x_param].unique())
    y_values = sorted(results_df[y_param].unique())
    
    # Create matrix
    z_matrix = np.zeros((len(y_values), len(x_values)))
    
    for i, y_val in enumerate(y_values):
        for j, x_val in enumerate(x_values):
            mask = (results_df[x_param] == x_val) & (results_df[y_param] == y_val)
            if mask.any():
                z_matrix[i, j] = results_df.loc[mask, z_metric].values[0]
            else:
                z_matrix[i, j] = np.nan
    
    return np.array(x_values), np.array(y_values), z_matrix


def find_optimal_parameters(
    results_df: pd.DataFrame,
    optimization_metric: str,
    maximize: bool = True
) -> Dict:
    """
    Find optimal parameter configuration.
    
    Args:
        results_df: DataFrame from grid_search_parameters
        optimization_metric: Metric to optimize (e.g., 'sharpe_ratio_mean')
        maximize: True to maximize, False to minimize
    
    Returns:
        Dict with optimal parameters and their values
    """
    if maximize:
        best_idx = results_df[optimization_metric].idxmax()
    else:
        best_idx = results_df[optimization_metric].idxmin()
    
    best_config = results_df.loc[best_idx].to_dict()
    
    return best_config


def analyze_parameter_robustness(
    results_df: pd.DataFrame,
    parameter_name: str,
    metric: str
) -> Dict:
    """
    Analyze how robust results are to parameter changes.
    
    Args:
        results_df: DataFrame from grid_search_parameters
        parameter_name: Parameter to analyze
        metric: Metric to track (e.g., 'sharpe_ratio_mean')
    
    Returns:
        Dict with sensitivity statistics (correlation, range, std, coefficient of variation)
    """
    param_values = results_df[parameter_name].values
    metric_values = results_df[metric].values
    
    # Remove NaN values
    valid_mask = ~(np.isnan(param_values) | np.isnan(metric_values))
    param_values = param_values[valid_mask]
    metric_values = metric_values[valid_mask]
    
    if len(param_values) < 2:
        return {
            'parameter': parameter_name,
            'metric': metric,
            'correlation': np.nan,
            'range': np.nan,
            'std': np.nan,
            'coefficient_of_variation': np.nan
        }
    
    # Calculate correlation
    correlation = np.corrcoef(param_values, metric_values)[0, 1]
    
    # Calculate range of performance
    metric_range = np.max(metric_values) - np.min(metric_values)
    metric_std = np.std(metric_values)
    metric_mean = np.mean(metric_values)
    
    return {
        'parameter': parameter_name,
        'metric': metric,
        'correlation': float(correlation),
        'range': float(metric_range),
        'std': float(metric_std),
        'mean': float(metric_mean),
        'coefficient_of_variation': float(metric_std / metric_mean) if metric_mean != 0 else np.nan
    }


def calculate_parameter_importance(
    results_df: pd.DataFrame,
    parameters: List[str],
    metric: str
) -> pd.DataFrame:
    """
    Calculate importance of each parameter using variance decomposition.
    
    Args:
        results_df: DataFrame from grid_search_parameters
        parameters: List of parameter names to analyze
        metric: Metric to analyze
    
    Returns:
        DataFrame with parameter importance scores
    """
    importances = []
    
    total_variance = results_df[metric].var()
    
    for param in parameters:
        # Group by parameter and calculate variance explained
        grouped = results_df.groupby(param)[metric].agg(['mean', 'std', 'count'])
        
        # Between-group variance
        grand_mean = results_df[metric].mean()
        between_var = np.sum(grouped['count'] * (grouped['mean'] - grand_mean)**2) / len(results_df)
        
        # Variance explained
        var_explained = between_var / total_variance if total_variance > 0 else 0
        
        importances.append({
            'parameter': param,
            'variance_explained': var_explained,
            'importance_pct': var_explained * 100
        })
    
    importance_df = pd.DataFrame(importances)
    importance_df = importance_df.sort_values('variance_explained', ascending=False)
    
    return importance_df


def perform_1d_sensitivity(
    parameter_grid: Dict[str, List[float]],
    baseline_params: Dict[str, float],
    simulation_func: Callable,
    n_runs_per_config: int = 20,
    metrics: List[str] = ['sharpe_ratio', 'max_drawdown', 'total_pnl']
) -> Dict[str, pd.DataFrame]:
    """
    Perform 1D sensitivity analysis (vary one parameter at a time).
    
    Args:
        parameter_grid: Dict mapping parameter names to lists of values to try
        baseline_params: Dict with baseline parameter values (for parameters not being varied)
        simulation_func: Function that takes parameters and seed
        n_runs_per_config: Number of runs per configuration
        metrics: List of metrics to track
    
    Returns:
        Dict mapping parameter names to DataFrames with results
    """
    results = {}
    
    for param_name, param_values in parameter_grid.items():
        param_results = []
        
        for param_value in tqdm(param_values, desc=f"Varying {param_name}"):
            # Create parameters for this run (baseline + varied parameter)
            params = baseline_params.copy()
            params[param_name] = param_value
            
            # Run simulations
            run_results = []
            for run_idx in range(n_runs_per_config):
                try:
                    result = simulation_func(**params, seed=42 + run_idx)
                    run_results.append(result)
                except Exception as e:
                    print(f"Warning: Simulation failed for {param_name}={param_value}: {e}")
                    continue
            
            if len(run_results) == 0:
                continue
            
            # Calculate statistics
            param_stats = {param_name: param_value}
            
            for metric in metrics:
                values = np.array([r.get(metric, np.nan) for r in run_results])
                values = values[~np.isnan(values)]
                
                if len(values) > 0:
                    param_stats[f'{metric}_mean'] = np.mean(values)
                    param_stats[f'{metric}_std'] = np.std(values)
                    param_stats[f'{metric}_ci_lower'] = np.percentile(values, 2.5)
                    param_stats[f'{metric}_ci_upper'] = np.percentile(values, 97.5)
            
            param_results.append(param_stats)
        
        results[param_name] = pd.DataFrame(param_results)
    
    return results

