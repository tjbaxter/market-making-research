"""Analytics and metrics for market-making research."""

from .vpin import (
    VPINCalculator,
    VPINConfig,
    BulkVolumeClassifier
)
from .pnl_decomposition import (
    PnLDecomposer,
    decompose_pnl_detailed,
    calculate_spread_capture,
    calculate_adverse_selection
)
from .performance import (
    PerformanceMetrics,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio
)

__all__ = [
    'VPINCalculator',
    'VPINConfig',
    'BulkVolumeClassifier',
    'PnLDecomposer',
    'decompose_pnl_detailed',
    'calculate_spread_capture',
    'calculate_adverse_selection',
    'PerformanceMetrics',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_calmar_ratio',
]

