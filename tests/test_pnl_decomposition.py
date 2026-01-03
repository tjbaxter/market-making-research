"""Tests for PnL decomposition."""

import pytest
import numpy as np
from src.simulation import Portfolio
from src.metrics import (
    PnLDecomposer,
    calculate_spread_capture,
    calculate_adverse_selection
)


def test_spread_capture_calculation():
    """Test spread capture calculation."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # Sell above mid, buy below mid
    portfolio.buy(price=101.0, size=100, mid_price=100.0)  # Capture $1 * 100
    portfolio.sell(price=99.0, size=100, mid_price=100.0)   # Capture $1 * 100
    
    spread = calculate_spread_capture(portfolio.trades)
    
    assert spread == pytest.approx(200.0)


def test_pnl_decomposition_no_trades():
    """Test decomposition with no trades."""
    decomposer = PnLDecomposer()
    prices = np.array([100.0, 101.0, 102.0])
    
    components = decomposer.decompose(
        trades=[],
        prices=prices
    )
    
    assert components.total_pnl == 0.0
    assert components.spread_capture == 0.0


def test_pnl_decomposition_with_trades():
    """Test decomposition with actual trades."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # Make some trades
    portfolio.buy(price=101.0, size=100, mid_price=100.0)
    portfolio.sell(price=99.0, size=100, mid_price=100.0)
    
    prices = np.array([100.0, 100.0, 100.0])
    
    decomposer = PnLDecomposer()
    components = decomposer.decompose(
        trades=portfolio.trades,
        prices=prices
    )
    
    # Should have positive spread capture
    assert components.spread_capture > 0


def test_transaction_costs():
    """Test transaction cost calculation."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.001)  # 10 bps
    
    portfolio.buy(price=100.0, size=100, mid_price=100.0)
    
    prices = np.array([100.0, 100.0])
    
    decomposer = PnLDecomposer()
    components = decomposer.decompose(
        trades=portfolio.trades,
        prices=prices,
        commission_rate=0.001
    )
    
    # Should have transaction costs
    assert components.transaction_costs > 0


def test_adverse_selection_measure():
    """Test adverse selection measurement."""
    from src.simulation.accounting import Trade
    
    # Create trades where price moves against us
    trades = [
        Trade(
            timestamp=0,
            side='buy',
            price=100.0,
            size=100,
            mid_price=100.0,
            inventory_before=0
        )
    ]
    
    # Price falls after we bought
    prices = np.array([100.0, 99.0, 98.0, 97.0, 96.0, 95.0])
    
    adverse_cost = calculate_adverse_selection(trades, prices, lookback=5)
    
    # Should have adverse selection cost
    assert adverse_cost > 0

