"""
Sample data with statistical results for Streamlit dashboard.

This shows what the experiments look like with multiple runs and statistics.
Use this for the dashboard until you run full experiments.
"""

import numpy as np

# Seed for reproducibility
np.random.seed(42)

# =============================================================================
# EXPERIMENT 1: PnL Decomposition (100 runs per strategy/regime)
# =============================================================================

EXPERIMENT_1_DATA = {
    'benign_flow': {
        'naive': {
            'total_pnl': np.random.normal(850, 120, 100).tolist(),
            'spread_capture': np.random.normal(1200, 80, 100).tolist(),
            'adverse_selection': np.random.normal(-180, 40, 100).tolist(),
            'inventory_pnl': np.random.normal(-170, 90, 100).tolist(),
        },
        'inventory_aware': {
            'total_pnl': np.random.normal(920, 110, 100).tolist(),
            'spread_capture': np.random.normal(1180, 75, 100).tolist(),
            'adverse_selection': np.random.normal(-160, 35, 100).tolist(),
            'inventory_pnl': np.random.normal(-100, 70, 100).tolist(),
        },
        'avellaneda_stoikov': {
            'total_pnl': np.random.normal(980, 100, 100).tolist(),
            'spread_capture': np.random.normal(1150, 70, 100).tolist(),
            'adverse_selection': np.random.normal(-140, 30, 100).tolist(),
            'inventory_pnl': np.random.normal(-30, 50, 100).tolist(),
        }
    },
    'toxic_flow': {
        'naive': {
            'total_pnl': np.random.normal(-420, 180, 100).tolist(),
            'spread_capture': np.random.normal(1100, 90, 100).tolist(),
            'adverse_selection': np.random.normal(-1050, 150, 100).tolist(),
            'inventory_pnl': np.random.normal(-470, 120, 100).tolist(),
        },
        'inventory_aware': {
            'total_pnl': np.random.normal(-180, 160, 100).tolist(),
            'spread_capture': np.random.normal(1080, 85, 100).tolist(),
            'adverse_selection': np.random.normal(-880, 130, 100).tolist(),
            'inventory_pnl': np.random.normal(-380, 100, 100).tolist(),
        },
        'avellaneda_stoikov': {
            'total_pnl': np.random.normal(120, 140, 100).tolist(),
            'spread_capture': np.random.normal(1050, 80, 100).tolist(),
            'adverse_selection': np.random.normal(-680, 110, 100).tolist(),
            'inventory_pnl': np.random.normal(-250, 90, 100).tolist(),
        }
    }
}

# =============================================================================
# EXPERIMENT 2: VPIN Analysis (100 runs)
# =============================================================================

EXPERIMENT_2_DATA = {
    'vpin_correlation': 0.64,  # Correlation between VPIN and subsequent losses
    'high_vpin_loss_multiplier': 3.2,  # Loss increase when VPIN > 0.7
    'vpin_lead_time_steps': 75,  # Average lead time
    
    # VPIN vs Loss data points (for scatter plot)
    'vpin_values': np.clip(np.random.beta(2, 5, 200), 0.1, 0.95).tolist(),
    'subsequent_losses': None,  # Will be calculated based on vpin_values
}

# Calculate losses correlated with VPIN
vpin_arr = np.array(EXPERIMENT_2_DATA['vpin_values'])
losses = -50 * vpin_arr + np.random.normal(0, 10, len(vpin_arr)) - 20
EXPERIMENT_2_DATA['subsequent_losses'] = losses.tolist()

# =============================================================================
# EXPERIMENT 3: Regime Switching (100 runs each)
# =============================================================================

EXPERIMENT_3_DATA = {
    'static_strategy': {
        'sharpe_ratio': np.random.normal(1.12, 0.18, 100).tolist(),
        'max_drawdown': np.random.normal(1850, 320, 100).tolist(),
        'total_pnl': np.random.normal(680, 150, 100).tolist(),
        'fill_rate': np.random.normal(0.68, 0.08, 100).tolist(),
    },
    'adaptive_strategy': {
        'sharpe_ratio': np.random.normal(1.32, 0.16, 100).tolist(),
        'max_drawdown': np.random.normal(1090, 240, 100).tolist(),
        'total_pnl': np.random.normal(645, 140, 100).tolist(),
        'fill_rate': np.random.normal(0.61, 0.07, 100).tolist(),
    }
}

# Calculate improvements
static_sharpe_mean = np.mean(EXPERIMENT_3_DATA['static_strategy']['sharpe_ratio'])
adaptive_sharpe_mean = np.mean(EXPERIMENT_3_DATA['adaptive_strategy']['sharpe_ratio'])
sharpe_improvement = ((adaptive_sharpe_mean - static_sharpe_mean) / static_sharpe_mean) * 100

static_dd_mean = np.mean(EXPERIMENT_3_DATA['static_strategy']['max_drawdown'])
adaptive_dd_mean = np.mean(EXPERIMENT_3_DATA['adaptive_strategy']['max_drawdown'])
drawdown_reduction = ((static_dd_mean - adaptive_dd_mean) / static_dd_mean) * 100

EXPERIMENT_3_DATA['sharpe_improvement_pct'] = sharpe_improvement
EXPERIMENT_3_DATA['drawdown_reduction_pct'] = drawdown_reduction

# =============================================================================
# EXPERIMENT 4: Failure Analysis (20 runs each scenario)
# =============================================================================

EXPERIMENT_4_DATA = {
    'false_positives': {
        'pnl': np.random.normal(720, 95, 20).tolist(),
        'impact': 'Low',
        'description': 'VPIN spikes without actual toxicity (high volume, no adverse selection)'
    },
    'detection_lag': {
        'pnl': np.random.normal(-180, 140, 20).tolist(),
        'impact': 'Medium',
        'description': 'Toxicity starts before VPIN rises (50-100 step delay)'
    },
    'extreme_jumps': {
        'pnl': np.random.normal(-650, 280, 20).tolist(),
        'impact': 'High',
        'description': 'Large price jumps overwhelm any strategy (unavoidable inventory losses)'
    },
    'high_frequency_switches': {
        'pnl': np.random.normal(280, 120, 20).tolist(),
        'impact': 'Medium',
        'description': 'Regime changes every 20 steps (too fast for adaptation)'
    }
}

# =============================================================================
# SENSITIVITY ANALYSIS: VPIN Threshold (for heatmap)
# =============================================================================

SENSITIVITY_VPIN_THRESHOLDS = np.linspace(0.5, 0.9, 9).tolist()
SENSITIVITY_SPREAD_MULTIPLIERS = [1.25, 1.5, 1.75, 2.0]

# Create heatmap data
SENSITIVITY_SHARPE_MATRIX = []
for spread_mult in SENSITIVITY_SPREAD_MULTIPLIERS:
    row = []
    for vpin_thresh in SENSITIVITY_VPIN_THRESHOLDS:
        # Optimal around vpin=0.7, spread=1.5
        distance_from_optimal = abs(vpin_thresh - 0.7) + abs(spread_mult - 1.5) * 0.2
        sharpe = 1.4 - distance_from_optimal * 0.6 + np.random.normal(0, 0.05)
        row.append(max(sharpe, 0.3))  # Floor at 0.3
    SENSITIVITY_SHARPE_MATRIX.append(row)

# =============================================================================
# Helper function to get data
# =============================================================================

def get_experiment_data(experiment_num: int):
    """Get sample data for experiment."""
    if experiment_num == 1:
        return EXPERIMENT_1_DATA
    elif experiment_num == 2:
        return EXPERIMENT_2_DATA
    elif experiment_num == 3:
        return EXPERIMENT_3_DATA
    elif experiment_num == 4:
        return EXPERIMENT_4_DATA
    else:
        return None

def get_sensitivity_data():
    """Get sensitivity analysis data."""
    return {
        'vpin_thresholds': SENSITIVITY_VPIN_THRESHOLDS,
        'spread_multipliers': SENSITIVITY_SPREAD_MULTIPLIERS,
        'sharpe_matrix': SENSITIVITY_SHARPE_MATRIX
    }

