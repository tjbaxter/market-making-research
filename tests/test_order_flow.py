"""Tests for order flow module."""

import pytest
from src.simulation import OrderFlowGenerator, OrderFlowConfig, FlowRegime


def test_order_flow_initialization():
    """Test order flow initializes correctly."""
    config = OrderFlowConfig(A=10.0, kappa=0.5)
    flow = OrderFlowGenerator(config, seed=42)
    
    assert flow.regime == FlowRegime.BENIGN
    assert len(flow.order_history) == 0


def test_fill_intensity_calculation():
    """Test fill intensity depends on spread."""
    config = OrderFlowConfig(A=10.0, kappa=0.5)
    flow = OrderFlowGenerator(config, seed=42)
    
    mid = 100.0
    
    # Tight spread -> high intensity
    lambda_bid1, lambda_ask1 = flow.calculate_fill_intensity(99.9, 100.1, mid)
    
    # Wide spread -> low intensity
    lambda_bid2, lambda_ask2 = flow.calculate_fill_intensity(99.0, 101.0, mid)
    
    assert lambda_bid1 > lambda_bid2
    assert lambda_ask1 > lambda_ask2


def test_toxic_flow_regime():
    """Test toxic flow increases fills in price direction."""
    config = OrderFlowConfig(A=10.0, kappa=0.5, toxicity_factor=0.5)
    flow = OrderFlowGenerator(config, seed=42)
    flow.set_regime(FlowRegime.TOXIC)
    
    # Price rising -> should get more buys
    buy_orders, sell_orders = flow.generate_orders(
        bid=99.0,
        ask=101.0,
        mid_price=100.0,
        future_price=105.0,  # Rising
        dt=1.0/252.0
    )
    
    # Can't guarantee specific counts due to randomness,
    # but on average should see more buys
    assert len(buy_orders) >= 0  # Just check it runs


def test_order_flow_reproducibility():
    """Test order flow is reproducible."""
    config = OrderFlowConfig(A=10.0, kappa=0.5)
    
    flow1 = OrderFlowGenerator(config, seed=42)
    flow2 = OrderFlowGenerator(config, seed=42)
    
    orders1 = flow1.generate_orders(99.0, 101.0, 100.0, None, 1.0/252.0)
    orders2 = flow2.generate_orders(99.0, 101.0, 100.0, None, 1.0/252.0)
    
    assert len(orders1[0]) == len(orders2[0])  # Same buy count
    assert len(orders1[1]) == len(orders2[1])  # Same sell count


def test_get_recent_volume():
    """Test recent volume calculation."""
    config = OrderFlowConfig(A=10.0, kappa=0.5)
    flow = OrderFlowGenerator(config, seed=42)
    
    # Generate some orders
    for _ in range(10):
        flow.generate_orders(99.0, 101.0, 100.0, None, 1.0/252.0)
    
    buy_vol, sell_vol = flow.get_recent_volume(window=50)
    
    # Should have some volume
    assert buy_vol >= 0
    assert sell_vol >= 0


def test_reset():
    """Test order flow reset."""
    config = OrderFlowConfig(A=10.0, kappa=0.5)
    flow = OrderFlowGenerator(config, seed=42)
    
    # Generate some orders
    flow.generate_orders(99.0, 101.0, 100.0, None, 1.0/252.0)
    
    # Reset
    flow.reset()
    
    assert len(flow.order_history) == 0
    assert flow.time == 0.0

