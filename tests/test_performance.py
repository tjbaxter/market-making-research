"""Tests for performance metrics."""

import pytest
import numpy as np
from src.metrics import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
    PerformanceMetrics
)


def test_sharpe_ratio_positive_returns():
    """Test Sharpe ratio with positive returns."""
    returns = np.array([0.01, 0.02, 0.015, 0.012, 0.018])
    
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
    
    assert sharpe > 0


def test_sharpe_ratio_zero_volatility():
    """Test Sharpe ratio with zero volatility."""
    returns = np.array([0.01, 0.01, 0.01, 0.01])
    
    sharpe = calculate_sharpe_ratio(returns)
    
    # Should handle zero std dev
    assert sharpe == 0.0


def test_max_drawdown_monotonic():
    """Test max drawdown with monotonically increasing PnL."""
    pnl = np.array([0, 10, 20, 30, 40, 50])
    
    max_dd = calculate_max_drawdown(pnl)
    
    # No drawdown if always increasing
    assert max_dd == pytest.approx(0.0, abs=1e-6)


def test_max_drawdown_with_loss():
    """Test max drawdown with losses."""
    pnl = np.array([0, 10, 20, 15, 10, 5, 15])
    
    max_dd = calculate_max_drawdown(pnl)
    
    # Should detect drawdown from 20 to 5
    assert max_dd > 0
    assert max_dd < 1.0


def test_sortino_ratio():
    """Test Sortino ratio calculation."""
    # Mix of positive and negative returns
    returns = np.array([0.02, -0.01, 0.03, -0.015, 0.025])
    
    sortino = calculate_sortino_ratio(returns)
    
    # Should be defined
    assert not np.isnan(sortino)


def test_calmar_ratio():
    """Test Calmar ratio calculation."""
    pnl = np.array([0, 10, 15, 12, 18, 25, 30])
    
    calmar = calculate_calmar_ratio(pnl)
    
    # Should be positive if PnL increases
    assert calmar > 0


def test_performance_metrics_all():
    """Test comprehensive metric calculation."""
    pnl = np.linspace(0, 100, 100)
    
    from src.simulation.accounting import Trade
    trades = [
        Trade(0, 'buy', 100, 10, 100, 0),
        Trade(1, 'sell', 101, 10, 100, 10)
    ]
    
    metrics = PerformanceMetrics.calculate_all(pnl, trades)
    
    # Should have all metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'total_pnl' in metrics
    assert 'num_trades' in metrics
    assert metrics['num_trades'] == 2

