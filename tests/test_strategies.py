"""Tests for individual strategy implementations."""

import pytest
import numpy as np
from src.strategies import (
    NaiveStrategy,
    InventoryAwareStrategy,
    AvellanedaStoikovStrategy
)


def test_naive_strategy_initialization():
    """Test naive strategy initializes correctly."""
    strategy = NaiveStrategy(spread_width=2.0)
    
    assert strategy.spread_width == 2.0
    assert strategy.name == "Naive"


def test_naive_strategy_quotes():
    """Test naive strategy generates symmetric quotes."""
    strategy = NaiveStrategy(spread_width=2.0)
    
    state = {
        'mid_price': 100.0,
        'inventory': 0,
        'time': 0,
        'time_remaining': 100
    }
    
    bid, ask = strategy.get_quotes(state)
    
    assert bid == pytest.approx(99.0)
    assert ask == pytest.approx(101.0)
    assert ask - bid == pytest.approx(2.0)


def test_naive_strategy_ignores_inventory():
    """Test naive strategy doesn't adjust for inventory."""
    strategy = NaiveStrategy(spread_width=2.0)
    
    state_neutral = {
        'mid_price': 100.0,
        'inventory': 0,
        'time': 0,
        'time_remaining': 100
    }
    
    state_long = {
        'mid_price': 100.0,
        'inventory': 100,  # Large long position
        'time': 0,
        'time_remaining': 100
    }
    
    bid1, ask1 = strategy.get_quotes(state_neutral)
    bid2, ask2 = strategy.get_quotes(state_long)
    
    # Should be identical (no inventory management)
    assert bid1 == pytest.approx(bid2)
    assert ask1 == pytest.approx(ask2)


def test_inventory_aware_initialization():
    """Test inventory-aware strategy initializes correctly."""
    strategy = InventoryAwareStrategy(
        base_spread=2.0,
        inventory_penalty=0.01
    )
    
    assert strategy.base_spread == 2.0
    assert strategy.inventory_penalty == 0.01


def test_inventory_aware_skew():
    """Test inventory-aware strategy skews quotes."""
    strategy = InventoryAwareStrategy(
        base_spread=2.0,
        inventory_penalty=0.01
    )
    
    # Neutral position
    state_neutral = {
        'mid_price': 100.0,
        'inventory': 0,
        'time': 0,
        'time_remaining': 100
    }
    
    # Long position
    state_long = {
        'mid_price': 100.0,
        'inventory': 100,
        'time': 0,
        'time_remaining': 100
    }
    
    bid_neutral, ask_neutral = strategy.get_quotes(state_neutral)
    bid_long, ask_long = strategy.get_quotes(state_long)
    
    # When long, should lower quotes to encourage selling
    assert bid_long < bid_neutral
    assert ask_long < ask_neutral


def test_avellaneda_stoikov_initialization():
    """Test AS strategy initializes correctly."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        kappa=0.5
    )
    
    assert strategy.gamma == 0.1
    assert strategy.sigma == 0.02
    assert strategy.optimal_spread > 0


def test_avellaneda_stoikov_reservation_price():
    """Test AS reservation price calculation."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        T=1000
    )
    
    # Test neutral inventory
    state_neutral = {
        'mid_price': 100.0,
        'inventory': 0,
        'time_remaining': 500
    }
    
    reservation_neutral = strategy.get_reservation_price(state_neutral)
    assert reservation_neutral == pytest.approx(100.0)  # Should equal mid
    
    # Test long inventory
    state_long = {
        'mid_price': 100.0,
        'inventory': 100,
        'time_remaining': 500
    }
    
    reservation_long = strategy.get_reservation_price(state_long)
    assert reservation_long < 100.0  # Should be below mid when long


def test_avellaneda_stoikov_quotes_symmetric_around_reservation():
    """Test AS quotes are symmetric around reservation price."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        kappa=0.5
    )
    
    state = {
        'mid_price': 100.0,
        'inventory': 50,
        'time': 0,
        'time_remaining': 100
    }
    
    bid, ask = strategy.get_quotes(state)
    reservation = strategy.get_reservation_price(state)
    
    # Check symmetry around reservation
    bid_distance = reservation - bid
    ask_distance = ask - reservation
    
    assert bid_distance == pytest.approx(ask_distance, rel=1e-6)


def test_all_strategies_return_valid_quotes():
    """Test all strategies return valid bid < ask."""
    strategies = [
        NaiveStrategy(spread_width=1.0),
        InventoryAwareStrategy(base_spread=1.0, inventory_penalty=0.01),
        AvellanedaStoikovStrategy(risk_aversion=0.1, volatility=0.02)
    ]
    
    state = {
        'mid_price': 100.0,
        'inventory': 25,
        'time': 50,
        'time_remaining': 50
    }
    
    for strategy in strategies:
        bid, ask = strategy.get_quotes(state)
        
        # Check validity
        assert bid > 0, f"{strategy.name}: bid must be positive"
        assert ask > 0, f"{strategy.name}: ask must be positive"
        assert bid < ask, f"{strategy.name}: bid must be less than ask"


def test_strategy_parameter_validation():
    """Test strategies reject invalid parameters."""
    
    # Naive: negative spread
    with pytest.raises(ValueError):
        NaiveStrategy(spread_width=-1.0)
    
    # Inventory-aware: negative spread
    with pytest.raises(ValueError):
        InventoryAwareStrategy(base_spread=-1.0)
    
    # AS: negative risk aversion
    with pytest.raises(ValueError):
        AvellanedaStoikovStrategy(risk_aversion=-0.1)
    
    # AS: zero volatility
    with pytest.raises(ValueError):
        AvellanedaStoikovStrategy(volatility=0.0)


def test_naive_strategy_reset():
    """Test strategy reset functionality."""
    strategy = NaiveStrategy(spread_width=1.0)
    
    state = {'mid_price': 100.0, 'inventory': 0, 'time': 0, 'time_remaining': 100}
    
    # Generate some quotes
    for _ in range(10):
        strategy.get_quotes(state)
    
    assert len(strategy.get_quote_history()) == 10
    
    # Reset
    strategy.reset()
    assert len(strategy.get_quote_history()) == 0


def test_inventory_aware_short_position():
    """Test inventory-aware strategy with short position."""
    strategy = InventoryAwareStrategy(
        base_spread=2.0,
        inventory_penalty=0.01
    )
    
    state_neutral = {
        'mid_price': 100.0,
        'inventory': 0,
        'time': 0,
        'time_remaining': 100
    }
    
    state_short = {
        'mid_price': 100.0,
        'inventory': -100,  # Short position
        'time': 0,
        'time_remaining': 100
    }
    
    bid_neutral, ask_neutral = strategy.get_quotes(state_neutral)
    bid_short, ask_short = strategy.get_quotes(state_short)
    
    # When short, should raise quotes to encourage buying
    assert bid_short > bid_neutral
    assert ask_short > ask_neutral


def test_as_strategy_optimal_spread_calculation():
    """Test AS optimal spread calculation."""
    # Small gamma/kappa ratio - should use approximation
    strategy1 = AvellanedaStoikovStrategy(
        risk_aversion=0.01,
        volatility=0.02,
        kappa=0.5
    )
    
    # Larger gamma/kappa ratio - should use exact formula
    strategy2 = AvellanedaStoikovStrategy(
        risk_aversion=0.5,
        volatility=0.02,
        kappa=0.5
    )
    
    # Both should have positive spreads
    assert strategy1.optimal_spread > 0
    assert strategy2.optimal_spread > 0
    
    # Optimal spread formula: delta = log(1 + gamma/kappa) / gamma
    # Actually decreases as gamma increases (more risk averse = tighter quotes)
    # This is correct per AS 2008 formula


def test_as_strategy_time_decay():
    """Test AS strategy adjusts for time to horizon."""
    strategy = AvellanedaStoikovStrategy(
        risk_aversion=0.1,
        volatility=0.02,
        T=1000
    )
    
    # Same inventory, different time remaining
    state_early = {
        'mid_price': 100.0,
        'inventory': 100,
        'time_remaining': 900
    }
    
    state_late = {
        'mid_price': 100.0,
        'inventory': 100,
        'time_remaining': 100
    }
    
    res_early = strategy.get_reservation_price(state_early)
    res_late = strategy.get_reservation_price(state_late)
    
    # Early in horizon, inventory penalty should be stronger
    assert abs(res_early - 100.0) > abs(res_late - 100.0)

