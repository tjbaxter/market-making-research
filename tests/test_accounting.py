"""Tests for accounting module."""

import pytest
from src.simulation import Portfolio, Trade


def test_portfolio_initialization():
    """Test portfolio initializes correctly."""
    portfolio = Portfolio(initial_cash=10000.0)
    
    assert portfolio.cash == 10000.0
    assert portfolio.inventory == 0
    assert len(portfolio.trades) == 0


def test_buy_execution():
    """Test buy order execution (we sell)."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # We sell 100 shares at $101
    portfolio.buy(price=101.0, size=100, mid_price=100.0)
    
    assert portfolio.cash == 10100.0  # Received cash
    assert portfolio.inventory == -100  # Short position
    assert len(portfolio.trades) == 1


def test_sell_execution():
    """Test sell order execution (we buy)."""
    portfolio = Portfolio(initial_cash=10000.0, commission_rate=0.0)
    
    # We buy 100 shares at $99
    portfolio.sell(price=99.0, size=100, mid_price=100.0)
    
    assert portfolio.cash == 100.0  # Paid cash
    assert portfolio.inventory == 100  # Long position
    assert len(portfolio.trades) == 1


def test_pnl_calculation():
    """Test PnL calculation."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # Buy at 100, mark at 110
    portfolio.sell(price=100.0, size=100, mid_price=100.0)
    
    pnl = portfolio.calculate_pnl(current_price=110.0)
    
    # Paid $10000, inventory worth $11000
    assert pnl == pytest.approx(1000.0)


def test_pnl_decomposition():
    """Test PnL decomposition."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # Capture spread
    portfolio.buy(price=101.0, size=100, mid_price=100.0)  # Sell above mid
    portfolio.sell(price=99.0, size=100, mid_price=100.0)  # Buy below mid
    
    decomp = portfolio.decompose_pnl()
    
    assert decomp['spread_capture'] == pytest.approx(200.0)  # $1 * 100 * 2
    assert 'adverse_selection' in decomp
    assert 'total' in decomp


def test_commission_rate():
    """Test that commission is applied correctly."""
    portfolio = Portfolio(initial_cash=10000.0, commission_rate=0.001)
    
    # We buy 100 shares at $99
    portfolio.sell(price=99.0, size=100, mid_price=100.0)
    
    # Should pay 9900 + 9.9 commission = 9909.9
    assert portfolio.cash == pytest.approx(10000.0 - 9909.9)


def test_get_trade_df():
    """Test trade DataFrame export."""
    portfolio = Portfolio(initial_cash=0.0, commission_rate=0.0)
    
    # Make some trades
    portfolio.buy(price=101.0, size=100, mid_price=100.0)
    portfolio.sell(price=99.0, size=100, mid_price=100.0)
    
    df = portfolio.get_trade_df()
    
    assert len(df) == 2
    assert 'price' in df.columns
    assert 'side' in df.columns


def test_reset():
    """Test portfolio reset."""
    portfolio = Portfolio(initial_cash=10000.0, commission_rate=0.0)
    
    # Make a trade
    portfolio.buy(price=101.0, size=100, mid_price=100.0)
    
    # Reset
    portfolio.reset()
    
    assert portfolio.cash == 10000.0
    assert portfolio.inventory == 0
    assert len(portfolio.trades) == 0

